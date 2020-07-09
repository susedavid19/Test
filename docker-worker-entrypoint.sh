#!/bin/bash

cd /data
# We only want to allow for 1 concurrent task to run at any 1 time to prevent
# memory issues. This can be autoscaled and incresed later, with additional time
# for design
celery -A expressways.calculation worker --concurrency=1 --loglevel=info --max-memory-per-child=2000000
tail -f /dev/null
