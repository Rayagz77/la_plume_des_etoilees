#!/usr/bin/env bash
set -e

# Refuser de démarrer si APP_ENV=production sans DATABASE_URL explicite
if [ "${APP_ENV}" = "production" ] && [ -z "${DATABASE_URL}" ]; then
  echo "ERROR: DATABASE_URL must be set when APP_ENV=production" >&2
  exit 1
fi

# Si DATABASE_URL est fournie (prod/ci), attendre via cette URL
if [ -n "${DATABASE_URL}" ]; then
  echo "Waiting for database via DATABASE_URL ..."
  # pg_isready ne comprend pas les schémas dialectaux (ex: postgresql+psycopg2).
  # On extrait donc hôte/port/base/utilisateur pour appeler pg_isready avec les options.
  IFS=$'\n' read -r DB_USER DB_PASSWORD DB_HOST DB_PORT DB_NAME <<<"$(python3 <<'PY'
import os, urllib.parse
url = os.environ['DATABASE_URL']
# Normaliser les schémas non supportés par libpq
url = url.replace('postgresql+psycopg2', 'postgresql').replace('postgres+psycopg2', 'postgresql')
p = urllib.parse.urlparse(url)
print(p.username or '')
print(p.password or '')
print(p.hostname or '')
print(p.port or 5432)
print(p.path.lstrip('/'))
PY
)"
  export PGPASSWORD="${DB_PASSWORD}"
  until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}"; do sleep 1; done
  unset PGPASSWORD
  echo "DB is up (DATABASE_URL)!"
else
  DB_HOST="${DB_HOST:-${POSTGRES_HOST:-db}}"
  DB_PORT="${DB_PORT:-5432}"
  DB_USER="${DB_USER:-${POSTGRES_USER:-app}}"
  DB_PASSWORD="${DB_PASSWORD:-${POSTGRES_PASSWORD:-app}}"
  DB_NAME="${DB_NAME:-${POSTGRES_DB:-db_psql_library}}"
  echo "Waiting for database ${DB_NAME} at ${DB_HOST}:${DB_PORT} ..."
  until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}"; do sleep 1; done
  echo "DB is up!"
  export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}}"
fi

export SQLALCHEMY_DATABASE_URI="${SQLALCHEMY_DATABASE_URI:-${DATABASE_URL}}"
export FLASK_APP=${FLASK_APP:-app.py}
export FLASK_ENV=${FLASK_ENV:-production}

echo "Running migrations ..."
flask db upgrade

# binder $PORT si présent (Railway), sinon 8000
exec gunicorn -w ${GUNICORN_WORKERS:-3} -k gthread --threads ${GUNICORN_THREADS:-8} \
  -b 0.0.0.0:${PORT:-8000} --timeout ${GUNICORN_TIMEOUT:-120} "app:create_app()"
