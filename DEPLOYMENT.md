# Deploying Highways England OMS Expressways Tool

## Prerequisites
In order to deploy a working tool, the following is needed:

1. A working cloud based VM (preferably Linux based) with a minimum resource allocation as provided in supporting documentation 
    1. The latest version of docker-compose installed onto the VM (https://docs.docker.com/compose/install/)
    1. GIT installed onto the VM (https://git-scm.com/download/linux)
1. A PostgreSQL database for data storage, analysis and worker, with read/write user access

NOTE: All database could be combined into a single database. Separate databases will provide isolation and reduce risk on data corruption etc

### Environment Variables

The following environment variables **NEED** to be set for the tool to work successfully:

`DJANGO_SECRET_KEY` = a secret key used for cryptographic signing.  This is provided
by django when creating a project and should only be overwritten if really needed.  See [this](https://docs.djangoproject.com/en/2.1/ref/settings/#secret-key) for more details.
`CELERY_BACKEND_URL` = the full url of the queue container.  Default: 'redis://queue:6379/0'
`CELERY_BROKER_URL` = the full url of the queue container.  Defaults: 'redis://queue:6379/0'
`DEBUG` = Set this to False within production environments

The following environment variables are **OPTIONAL** as defaults are set within the docker-compose files:

`DATABASE_URL` = The full URL of the PostgreSQL database to be used. Default: 'postgres://express:express@database:5432/express'
`GUNICORN_CMD_ARGS` = The Gunicorn server command. Default: '--bind=0.0.0.0:8000 --workers=3 --timeout 120'
`ALLOWED_HOST` = The url and ports of the allowed hosts for the application, comma delimited. This will need to contain your application URL. Default: '${ELB_IP_ADDRESS}'
`MINIMUM_PASSWORD_LENGTH` = The minimum number of characters allowed for the user password. Default: 9
`DJANGO_SETTINGS_MODULE` = The settings module for the Django application. Default: 'config.settings'

## Deployment
Follow these steps to deploy the OMS Expressways tool using Docker:

1. If the code provided has been uploaded into a source control repository, log into the VM and using GIT, clone the repository
    1. Alternatively, if you have the code located elsewhere as a filezip, you will need to transfer this onto the VM and unpack
1. Navigate (`cd`) into the `expressways` folder
1. Run the following docker-compose commands, your site should appear at `localhost:{port}`
    1. `docker-compose up -d`
    1. `bash scripts/launch_server.sh`
    
Remaining within the docker container commandline, the following actions can also be carried out, but will have been 
initially handled during the above process:

### Creating A Test User
Default admin user will be auto-generated during container build. To have separate test user, run below command:
```
docker-compose exec application python3 /data/manage.py createsuperuser
```

### Loading Initial Data
Default data will be loaded during container build. If you need to reload the data, run below command:
```
docker-compose exec -T application python3 /data/manage.py loaddata occurrences designcomponents roads operationalobjectives --app core
```

## Infrastructure changes
On deployment, it is possible to change/update the following information through the docker-compose files `docker-compose.yml` and `docker-compose-prod.yml`:

1. The application port, defaults to 8000
1. The proxy port, defaults to 80:80
1. The Redis post, defaults to 6379
1. The database URL for each service, defaults to using the environment variable DATABASE_URL
1. The flower port, defaults to 5555:5555

## DNS Setup
Once the application is deployed successfully and running against localhost, you will need to setup the
DNS and point it to the appropriate IP address. Ideally you should have a load balancer setup, and the IP
address should be the address of the LB
