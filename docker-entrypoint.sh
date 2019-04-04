#!/bin/bash

cd /data
gunicorn config.wsgi:application

echo "Migrating data..."
python3 manage.py migrate
echo "Collecting static files..."
python3 manage.py collectstatic --noinput
echo "Creating default superuser..."
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@expressways.com', '!23Express')" | python3 manage.py shell
echo "Loading initial data..."
python3 manage.py loaddata expressways/core/fixtures/occurrences.json
