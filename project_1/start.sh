#!/bin/sh
# Startup script for Cloud Run

echo "Starting Screenshot Search App..."
echo "PORT: ${PORT:-8080}"

# Start gunicorn with explicit settings
exec gunicorn \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 1 \
    --threads 8 \
    --timeout 0 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app

