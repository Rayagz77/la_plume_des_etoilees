# controllers/auth_controller.py
from __future__ import annotations

from urllib.parse import urlparse, urljoin

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.routing import BuildError

from models import User  # adapte si nécessaire

login_bp = Blueprint("login_bp", __name__, template_folder="../templates")

# ---------- Helpers ----------

def _is_safe_url(target: str) -> bool:
    if not target:
        return False
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return (test.scheme in ("http", "https")) and (ref.netloc == test.netloc)

def _redirect_home():
    candidates = ("home", "home_bp.home", "main.home", "main_bp.index", "index", "root")
    for ep in candidates:
        try:
            return redirect(url_for(ep))
        except BuildError:
            continue
    return redirect("/")

# ---------- Routes ----------

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    # Si déjà logué(e) → accueil
    if current_user.is_authenticated:
        return _redirect_home()

    if request.method == "POST":
        email = (request.form.get("user_email") or "").strip().lower()
        password = request.form.get("user_password") or ""

        user = User.query.filter_by(user_email=email).first()
        if not user or not user.check_password(password):
            flash("Email ou mot de passe invalide.", "danger")
            return redirect(url_for("login_bp.login"))  # PRG

        if not getattr(user, "is_active", True):
            flash("Compte désactivé. Contactez le support.", "danger")
            return redirect(url_for("login_bp.login"))

        login_user(user, remember=True)
        flash(f"Bienvenue {user.user_firstname} !", "success")

        # 1) Respecte 'next' si sûr, 2) sinon toujours ACCUEIL (pas /account)
        next_url = request.args.get("next") or request.form.get("next")
        if next_url and _is_safe_url(next_url):
            return redirect(next_url)
        return _redirect_home()

    return render_template("login.html", show_forgot_modal=False)

@login_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Déconnecté.", "info")
    return _redirect_home()

@login_bp.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        flash("Si cet email existe, un lien de réinitialisation a été envoyé.", "info")
        return redirect(url_for("login_bp.login"))
    return render_template("forgot_password.html")
