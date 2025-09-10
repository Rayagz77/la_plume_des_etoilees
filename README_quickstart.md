# Quickstart — Emergency Docker Bootstrap (2025-09-05)

This bundle helps you run your Flask app (with `create_app()` in `app.py` at the project root) using Docker + Postgres fast.

## 1) Prepare a clean copy
1. Create a new folder, e.g. `plume_reset_2025-09-05`.
2. Copy **your whole project code** into this folder.
3. Drop the files from this bundle at the project **root** (so you have `docker-compose.yml`, a `docker/` folder, etc.).

## 2) Configure environment
1. Duplicate `.env.example` to `.env` and adjust:
   - `SECRET_KEY` — put any random string.
   - Keep `POSTGRES_*` as-is unless you want to change them.
2. Ensure your app factory exists: `app.py` exposes `create_app()`.

## 3) Run
```bash
docker compose up --build
```
Open http://localhost:8000

If you see import errors like `ModuleNotFoundError: No module named 'models'`:
- Make sure you have a `models/__init__.py` file (even empty).
- In `app.py`, before importing your app packages, add the project root to `sys.path` (you already have this in your previous setup).

## 4) Migrations (optional)
If you use Flask-Migrate, migrations run automatically on container start (`flask db upgrade`). If no migrations exist, the script will just continue.

## 5) Push to GitHub
```bash
git init
git add .
git commit -m "Emergency reboot: Dockerized MVP ready"
# Create a new repo on GitHub (web UI), then:
git remote add origin <your_repo_url>
git branch -M main
git push -u origin main
```

## Plan B (no Docker)
If Docker fails on your machine, you can still run:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Use SQLite quickly:
# Linux/macOS:
export DATABASE_URL=sqlite:///db.sqlite3
# Windows PowerShell:
# $env:DATABASE_URL="sqlite:///db.sqlite3"

flask db upgrade || echo "No migrations"
gunicorn -b 0.0.0.0:8000 "app:create_app()"
# or for quick dev:
# flask --app app.py run -p 8000
```
