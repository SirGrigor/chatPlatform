#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Running Alembic migrations..."
poetry run alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile=/app/certificates/key.pem --ssl-certfile=/app/certificates/cert.pem --log-level debug
