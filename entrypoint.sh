#!/bin/sh

# Blank line added for formatting
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Running Alembic migrations..."
cd /app/chatplatform
poetry run alembic upgrade head

echo "Starting application..."
# Navigate back to the root application directory
cd /app

# Start Uvicorn with the FastAPI application without SSL configuration
exec uvicorn chatplatform.app.main:app --host 0.0.0.0 --port 8000 --log-level debug
