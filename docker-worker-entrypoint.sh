#!/bin/bash

cd /data
celery -A expressways.calculation worker --loglevel=info --max-memory-per-child=2000000
tail -f /dev/null
