# Documentation — Architecture & Security (Skeleton)

## 1. Introduction
- Objectif : expliquer pourquoi l’architecture assure robustesse, sécurité, maintenabilité.

## 2. Architecture (MVC étendu)
- **Model** : SQLAlchemy (PostgreSQL), logs/audit (MongoDB si utilisé)
- **View** : Jinja2 (SSR), RGAA, CSP, CSRF
- **Controller** : Blueprints orchestrant Stripe (paiements), génération IA (HuggingFace), e‑mail (SMTP/Mailpit)
- **Extensions** : Flask‑Login, Flask‑Migrate, CORS, Limiter (anti‑abus)

## 3. Déploiement (CI/CD simplifié)
- `.env.example` -> secrets hors du code
- Dockerfile (user non‑root), image immuable
- `docker-compose.yml` (web + db)
- Migrations `flask db upgrade`

## 4. Sécurité (exemples)
- Mots de passe hashés
- Rate limiting (Flask‑Limiter)
- Headers de sécurité (CSP, HSTS via reverse proxy si applicable)
- Logs (accès/erreurs)

## 5. Tests & Qualité
- Smoke tests manuels (checklist)
- TODO: pytest

## 6. Annexes
- Captures d’écran (home, login, panier, paiement)
- Schémas : flux de paiement, flux de génération IA
- Tableaux Compétences ↔ Preuves
