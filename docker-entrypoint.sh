#!/bin/bash

cd /data
gunicorn config.wsgi:application

echo "Migrating data..."
python3 /data/manage.py migrate
sleep 3 && echo "Collecting static files..."
python3 /data/manage.py collectstatic --noinput
sleep 3 && echo "Creating default superuser..."
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@expressways.com', '!23Express')" | python3 /data/manage.py shell
sleep 3 && echo "Loading initial data..."
python3 /data/manage.py loaddata /data/expressways/core/fixtures/occurrences.json