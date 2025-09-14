# Quickstart — Emergency Docker Bootstrap (2025-09-05)

This bundle helps you run your Flask app (with `create_app()` in `app.py` at the project root) using Docker + Postgres fast.

## 1) Prepare a clean copy
1. Create a new folder, e.g. `plume_reset_2025-09-05`.
2. Copy **your whole project code** into this folder.
3. Drop the files from this bundle at the project **root** (so you have `docker-compose.yml`, a `docker/` folder, etc.).

## 2) Configure environment
1. Duplicate `.env.example` to `.env` and adjust:
   - `SECRET_KEY` — put any random string.
   - `POSTGRES_DB` — default database name `db_psql_library` (adjust if needed).
   - Keep other `POSTGRES_*` as-is unless you want to change them.
2. Ensure your app factory exists: `app.py` exposes `create_app()`.

## 3) Run
```bash
docker compose up --build
