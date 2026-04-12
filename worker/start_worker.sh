#!/bin/bash
set -e

echo "Starting Celery Worker..."
celery -A app.tasks.celery_app worker --loglevel=info --concurrency=${WORKER_CONCURRENCY:-1}
