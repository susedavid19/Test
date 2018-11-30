#!/bin/bash

cd /data
celery -A expressways.calculation.tasks worker --loglevel=info
