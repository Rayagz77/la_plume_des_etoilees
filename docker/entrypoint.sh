#!/usr/bin/env bash
set -e

echo "Waiting for database ${POSTGRES_DB} at ${DB_HOST:-db}:5432 ..."
until pg_isready -h "${DB_HOST:-db}" -p 5432 -U "${POSTGRES_USER:-app}" -d "${POSTGRES_DB:-db_psql_labrary}"; do
  sleep 1
done
echo "DB is up!"

export FLASK_APP=${FLASK_APP:-app.py}
export FLASK_ENV=${FLASK_ENV:-production}

# Build DATABASE_URL if not provided
if [ -z "${DATABASE_URL}" ]; then
  export DATABASE_URL="postgresql+psycopg2://${POSTGRES_USER:-app}:${POSTGRES_PASSWORD:-app}@${DB_HOST:-db}:5432/${POSTGRES_DB:-db_psql_labrary}"
fi
export SQLALCHEMY_DATABASE_URI="${DATABASE_URL}"

# Apply DB migrations if Flask-Migrate is configured
if command -v flask >/dev/null 2>&1; then
  echo "Running migrations (if any) ..."
  flask db upgrade || echo "No migrations to apply or Flask-Migrate not configured."
fi

# Start the app with Gunicorn using factory pattern
exec gunicorn -w ${GUNICORN_WORKERS:-2} -k gthread --threads ${GUNICORN_THREADS:-8} -b 0.0.0.0:8000 "app:create_app()"
