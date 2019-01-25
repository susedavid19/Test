#!/bin/bash

cd /data
celery -A expressways.calculation flower --port=5555
