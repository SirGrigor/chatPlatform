#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Navigate to the directory where alembic is located
echo "Running Alembic migrations..."
cd /app/chatplatform
poetry run alembic upgrade head

echo "Starting application..."
# Navigate back to the root application directory
cd /app

# Start Uvicorn with the FastAPI application
exec uvicorn chatplatform.app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile=/app/chatplatform/certificates/key.pem --ssl-certfile=/app/chatplatform/certificates/cert.pem --log-level debug

