#!/bin/bash

# Production startup script for FastAPI application

# Set environment variables
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}

# Number of workers (recommended: 2 * CPU cores + 1)
WORKERS=${WORKERS:-3}

echo "Starting FastAPI application with $WORKERS workers..."
echo "Host: $HOST"
echo "Port: $PORT"

# Use gunicorn with uvicorn workers for production
exec gunicorn main:create_app \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind $HOST:$PORT \
    --workers $WORKERS \
    --worker-timeout 120 \
    --access-logfile - \
    --error-logfile -