from celery import Celery
from django.conf import settings

app = Celery('tasks', backend=settings.CELERY_BACKEND_URL, broker=settings.CELERY_BROKER_URL)
