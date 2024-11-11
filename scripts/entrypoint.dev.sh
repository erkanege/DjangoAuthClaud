#!/bin/bash

echo "Waiting for MySQL..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done
echo "MySQL started"

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Creating cache tables..."
python manage.py createcachetable

# Development specific tasks
echo "Collecting static files..."
python manage.py collectstatic --noinput --verbosity 0

# Start development server
exec "$@"