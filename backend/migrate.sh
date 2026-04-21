#!/bin/bash
set -e

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Migrations completed successfully!"
