#!/bin/bash

set -e

# Set defaults for OTEL
export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-objects-flower}"

export FLOWER_MAX_TASKS="${FLOWER_MAX_TASKS:-1000}"
export FLOWER_MAX_WORKERS="${FLOWER_MAX_WORKERS:-50}"

exec celery \
    --app objects \
    --workdir src \
    --broker "${CELERY_BROKER_URL:-redis://localhost:6379/0}" \
    flower