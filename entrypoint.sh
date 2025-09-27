#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Wait for the database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
    sleep 1
done
echo "Database is ready."

# Run database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files in production
python manage.py collectstatic --noinput

# Execute the CMD provided in the Dockerfile or docker-compose
exec "$@"
