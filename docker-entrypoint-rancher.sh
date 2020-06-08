#!/bin/bash

cd /data
gunicorn config.wsgi:application &
sleep 5

echo "Migrating data..."
python3 manage.py migrate
echo "Loading initial data..."
python3 manage.py loaddata occurrences designcomponents roads operationalobjectives --app core

tail -f /dev/null
