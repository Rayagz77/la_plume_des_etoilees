# admin_seed.py (à la racine du projet)
from __future__ import annotations
from app import create_app
from models import db
from models.user_model import User

# >>>>> MODIFIE ICI <<<<<
EMAIL = "nadegekiemde.cdawch@gmail.com"      # ← remplace par ton email admin
PASSWORD = "Moncompteadmin33!"           # ← remplace par ton mot de passe
FIRSTNAME = "Admin"
LASTNAME = "User"

app = create_app()
with app.app_context():
    email = EMAIL.strip().lower()
    user = User.query.filter_by(user_email=email).first()
    if not user:
        user = User(
            user_email=email,
            user_firstname=FIRSTNAME,
            user_lastname=LASTNAME if hasattr(User, "user_lastname") else None,
            user_role="admin",
        )
        if hasattr(user, "set_password"):
            user.set_password(PASSWORD)
        else:
            raise RuntimeError("Ton modèle User doit avoir set_password().")
        db.session.add(user)
        action = "créé"
    else:
        user.user_role = "admin"
        if hasattr(user, "set_password"):
            user.set_password(PASSWORD)
        action = "promu en admin"
    db.session.commit()
    print(f"Utilisateur {email} {action} avec succès.")
