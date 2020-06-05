#!/bin/bash

cd /data
celery -A expressways.calculation worker --loglevel=info
tail -f /dev/null
