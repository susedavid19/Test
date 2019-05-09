# expressways

This is the repository for the Expressways OMS Tool.

## Getting Started
### Local Environment Default Setup
```
git clone git@bitbucket.org:wspdigitaluk/expressways.git
cd expressways
docker-compose -f docker-compose.yml -f docker-compose-local.yml up -d
docker-compose exec application bash -c /data/docker-entrypoint.sh
```
You should see the site appear at `localhost:7080`.

#### Preparing Environment
All database will be migrated and all static files will be collected during container build. 
For additional migration or updating changes on static files, run below command subsequently:
```
docker-compose exec application python3 /data/manage.py migrate
docker-compose exec application python3 /data/manage.py collectstatic
```

#### Creating A Test User
Default admin user will be auto-generated during container build. To have separate test user, run below command:
```
docker-compose exec application python3 /data/manage.py createsuperuser
```

#### Loading Initial Data
Default data will be loaded during container build. If you need to reload the data, run below command:
```
docker-compose exec application python3 /data/manage.py loaddata occurrences designcomponents roads --app core
```
