# controllers/cart_controller.py
from __future__ import annotations

from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user

from models import db
from models.user_model import User
from models.order_model import Order
from models.order_details_model import OrderDetail
from models.cart_items_model import CartItem

cart_bp = Blueprint('cart_bp', __name__)


# -------- Helpers --------
def _current_user_id() -> int | None:
    """Renvoie l'ID utilisateur quel que soit l'attribut (user_id / id / get_id)."""
    try:
        if getattr(current_user, "is_authenticated", False):
            uid = getattr(current_user, "user_id", None)
            if uid is not None:
                return int(uid)
            gid = current_user.get_id()
            return int(gid) if gid is not None else None
    except Exception:
        pass
    return None


# -------- Routes --------
@cart_bp.route('/add_to_cart/<int:book_id>', methods=['POST'])
def add_to_cart(book_id: int):
    """
    Ajoute un livre au panier.
    - Invité : stocke l'ID dans session['cart_temp'] (panier temporaire).
    - Connecté : persiste dans la table CartItem avec l'user_id courant.
    """
    uid = _current_user_id()

    # Invité → panier temporaire en session
    if uid is None:
        flash("Veuillez vous connecter pour sauvegarder votre panier et procéder au paiement.", "info")
        session.setdefault('cart_temp', [])
        if book_id not in session['cart_temp']:
            session['cart_temp'].append(book_id)
            flash("Livre ajouté temporairement. Connectez-vous pour finaliser.", "success")
        else:
            flash("Ce livre est déjà dans votre panier temporaire.", "info")
        return redirect(url_for('gallery'))

    # Connecté → panier persistant
    exists = CartItem.query.filter_by(user_id=uid, book_id=book_id).first()
    if exists:
        flash("Ce livre est déjà dans votre panier.", "info")
    else:
        db.session.add(CartItem(user_id=uid, book_id=book_id))
        db.session.commit()
        flash("Livre ajouté au panier.", "success")

    return redirect(url_for('gallery'))


@cart_bp.route('/view', methods=['GET'])
@login_required
def view_cart():
    uid = _current_user_id()
    if uid is None:
        flash("Veuillez vous connecter pour voir votre panier.", "warning")
        return redirect(url_for('login_bp.login'))

    cart_items = CartItem.query.filter_by(user_id=uid).all()
    total_price = sum((item.book.book_price or 0) for item in cart_items) if cart_items else 0
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@cart_bp.route('/remove_from_cart/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_item_id: int):
    uid = _current_user_id()
    if uid is None:
        flash("Veuillez vous connecter pour modifier votre panier.", "warning")
        return redirect(url_for('login_bp.login'))

    cart_item = CartItem.query.get(cart_item_id)
    if cart_item and int(cart_item.user_id) == int(uid):
        db.session.delete(cart_item)
        db.session.commit()
        flash("Article retiré du panier.", "success")
    else:
        flash("Impossible de supprimer cet article.", "danger")

    return redirect(url_for('cart_bp.view_cart'))


@cart_bp.route('/checkout-summary', methods=['GET', 'POST'])
@login_required
def checkout_summary():
    uid = _current_user_id()
    if uid is None:
        flash("Veuillez vous connecter pour accéder au récapitulatif.", "warning")
        return redirect(url_for('login_bp.login'))

    user: User = current_user  # type: ignore
    cart_items = CartItem.query.filter_by(user_id=uid).all()
    total_price = sum((item.book.book_price or 0) for item in cart_items)
    tva = round(total_price * 0.2, 2)

    if request.method == 'POST':
        # Email de livraison (par défaut celui du compte)
        email = (request.form.get('email') or getattr(user, "user_email", "")).strip()
        session['delivery_email'] = email

        # Crée la commande
        order = Order(user_id=uid, order_date=datetime.utcnow(), total_price=0, payment_status="pending")
        db.session.add(order)
        db.session.flush()  # pour avoir order.order_id

        running_total = 0.0
        for item in cart_items:
            db.session.add(OrderDetail(
                order_id=order.order_id,
                book_id=item.book_id,
                quantity=1,
                unit_price=(item.book.book_price or 0)
            ))
            running_total += (item.book.book_price or 0)

        order.total_price = running_total
        db.session.commit()

        # Vide le panier
        CartItem.query.filter_by(user_id=uid).delete()
        db.session.commit()

        return redirect(url_for('payement_bp.create_checkout_session', order_id=order.order_id))

    return render_template('checkout_summary.html',
                           cart_items=cart_items, user=user,
                           total_price=total_price, tva=tva)
