#!/bin/bash

docker-compose exec -T application python3 manage.py migrate

docker-compose exec -T application python3 manage.py collectstatic --noinput
