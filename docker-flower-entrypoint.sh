#!/bin/bash

cd /data
pip3 install -r requirements/development.txt
celery flower -A expressways.calculation --port=5555
