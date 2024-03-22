#!/bin/bash

set -e

exec celery --app objects --workdir src flower
