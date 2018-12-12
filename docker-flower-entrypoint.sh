#!/bin/bash

cd /data
celery -A expressways.calculation.tasks flower --port=5555
