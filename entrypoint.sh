#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Run Alembic Upgrade
alembic upgrade head

# Then start your application
exec "$@"
