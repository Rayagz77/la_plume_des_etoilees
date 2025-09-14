#!/usr/bin/env bash
set -e

# Si DATABASE_URL est fournie (prod/ci), attendre via cette URL
if [ -n "${DATABASE_URL}" ]; then
  echo "Waiting for database via DATABASE_URL ..."
  until pg_isready -d "${DATABASE_URL}"; do sleep 1; done
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
