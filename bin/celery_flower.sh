#!/bin/bash

set -e

# Set defaults for OTEL
export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-objects-flower}"

exec celery --app objects --workdir src flower
