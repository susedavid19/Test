#!/bin/bash
CMD_PATH=$(dirname "$(realpath $0)")
RUN_DC () {
    docker-compose -f ../docker-compose.yml -f ../docker-compose-local.yml $1
}
APP_MANAGE () {
    RUN_DC "exec -w /data application python3 manage.py $1"
}

cd $CMD_PATH

if [ "$1" == "clean" ]; then
    echo "Bringing down all containers..."
    RUN_DC "down --remove-orphans"
    echo "Cleaning all docker volumes from the host..."
    docker system prune --volumes -f
elif [ ! -z "$1" ]; then
    echo "Unrecognized parameter!"
fi

echo "Launching application..."
RUN_DC "up -d"

echo "Copying static files..."
APP_MANAGE "collectstatic --noinput"

echo "Running database migrations..."
APP_MANAGE "migrate"

echo "Creating superuser..."
APP_MANAGE "createsuperuser"

echo "Adding initial data..."
APP_MANAGE "loaddata occurrences designcomponents roads operationalobjectives --app core"
