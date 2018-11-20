# expressways

This is the repository for the Expressways OMS Tool.

## Getting Started
### Local Environment
```
git clone git@bitbucket.org:wspdigitaluk/expressways.git
cd expressways
docker-compose -f docker-compose.yml -f docker-compose-local.yml up -d
docker-compose exec application python3 /data/manage.py migrate
docker-compose exec application python3 /data/manage.py collectstatic
```

You should see the site appear at `localhost:7080`.

#### Creating A Test User
```
docker-compose exec application python3 /data/manage.py createsuperuser
```

#### Loading Initial Data
```
docker-compose exec application python3 /data/manage.py loaddata /data/expressways/core/fixtures/occurrences.json
```
