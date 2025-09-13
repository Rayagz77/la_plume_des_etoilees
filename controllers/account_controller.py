# controllers/account_controller.py
from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db
from models.user_model import User
from models.order_model import Order

account_bp = Blueprint("account_bp", __name__)

def _current_user_id() -> int | None:
    """Récupère l'ID utilisateur quel que soit le nom d'attribut (user_id / id)."""
    try:
        uid = getattr(current_user, "user_id", None)
        if uid is not None:
            return int(uid)
        gid = current_user.get_id()  # Flask-Login
        return int(gid) if gid is not None else None
    except Exception:
        return None

@account_bp.route("/", methods=["GET"])
@login_required
def user_dashboard():
    user: User = current_user  # type: ignore

    uid = _current_user_id()
    if uid is None:
        flash("Impossible d’identifier l’utilisateur.", "danger")
        return redirect(url_for("home"))

    user_orders = (
        Order.query
        .filter_by(user_id=uid, payment_status="paid")
        .order_by(Order.order_date.desc())
        .all()
    )
    return render_template("account.html", user=user, orders=user_orders)

@account_bp.route("/order/<int:order_id>", methods=["GET"])
@login_required
def order_details(order_id: int):
    uid = _current_user_id()
    if uid is None:
        flash("Impossible d’identifier l’utilisateur.", "danger")
        return redirect(url_for("account_bp.user_dashboard"))

    order = Order.query.get(order_id)
    if not order or int(getattr(order, "user_id", -1)) != uid:
        flash("Commande introuvable ou accès interdit.", "danger")
        return redirect(url_for("account_bp.user_dashboard"))

    return render_template("order_details.html", order=order)

@account_bp.route('/password', methods=['GET', 'POST'])
@login_required
def change_password():
    user: User = current_user  # type: ignore
    if request.method == 'POST':
        user.set_password(request.form['new_password'])
        db.session.commit()
        flash('Mot de passe mis à jour.', 'success')
        return redirect(url_for('account_bp.user_dashboard'))
    return render_template('change_password.html')
