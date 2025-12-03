#!/bin/bash
set -e

echo "Starting Django application on port ${PORT:-8080}..."

# Start Gunicorn immediately - no migrations during startup
exec python -m gunicorn --bind 0.0.0.0:${PORT:-8080} \
  --workers 1 \
  --threads 8 \
  --worker-class gthread \
  --timeout 0 \
  --graceful-timeout 300 \
  --keep-alive 300 \
  --access-logfile - \
  --error-logfile - \
  --log-level debug \
  backend_project.wsgi:application
