web: bash -lc "flask db upgrade && gunicorn --factory app:create_app -w 3 -k gthread -b 0.0.0.0:$PORT --timeout 120"
