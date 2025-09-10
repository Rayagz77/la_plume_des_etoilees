from __future__ import annotations

import logging
from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user

logger = logging.getLogger(__name__)

def _to_role(value) -> str:
    try:
        return (value or "").strip().lower()
    except Exception:
        return ""

def admin_required(f):
    """Décorateur pour les routes réservées aux administrateurs (basé sur Flask-Login)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.debug(
            f"Tentative d'accès admin à {request.path} par "
            f"{getattr(current_user, 'user_email', 'anonyme') if current_user.is_authenticated else 'anonyme'}"
        )

        if not current_user.is_authenticated:
            flash("Authentification requise pour cette zone.", "danger")
            return redirect(url_for("login_bp.login", next=request.url))

        role = _to_role(getattr(current_user, "user_role", None))
        is_admin = role == "admin" or bool(getattr(current_user, "is_admin", False))
        if not is_admin:
            flash("Privilèges insuffisants — accès réservé aux administrateurs.", "danger")
            return redirect(url_for("home"))

        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    """Décorateur pour utilisateurs connectés (non invités). Redirige les admins vers le panel admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Veuillez vous connecter pour accéder à cette page.", "warning")
            return redirect(url_for("login_bp.login", next=request.url))

        role = _to_role(getattr(current_user, "user_role", None))
        if role == "admin":
            flash("Espace réservé : utilisez le panel administrateur.", "info")
            # Tolérant au nom d'endpoint : dashboard -> admin_dashboard -> fallback /admin
            try:
                return redirect(url_for("admin_bp.dashboard"))
            except Exception:
                try:
                    return redirect(url_for("admin_bp.admin_dashboard"))
                except Exception:
                    return redirect("/admin")

        return f(*args, **kwargs)
    return decorated_function


def guest_required(f):
    """Décorateur pour visiteurs non connectés."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            role = _to_role(getattr(current_user, "user_role", None))
            user_type = "administrateur" if role == "admin" else "utilisateur"
            flash(f"Vous êtes déjà connecté(e) en tant que {user_type}.", "info")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(required_role: str):
    """Décorateur générique pour un rôle unique."""
    required_role = _to_role(required_role)

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Authentification requise.", "danger")
                return redirect(url_for("login_bp.login", next=request.url))

            role = _to_role(getattr(current_user, "user_role", None))
            if role != required_role:
                flash(f"Accès réservé aux {required_role}s.", "danger")
                return redirect(url_for("home"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def has_role(roles):
    """Décorateur acceptant plusieurs rôles (list/tuple/str)."""
    if isinstance(roles, str):
        roles = [roles]
    roles_norm = {_to_role(r) for r in roles}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Accès non autorisé.", "danger")
                return redirect(url_for("login_bp.login", next=request.url))

            role = _to_role(getattr(current_user, "user_role", None))
            if role not in roles_norm:
                flash("Privilèges insuffisants.", "danger")
                return redirect(url_for("home"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
