from celery import Celery
from celery.exceptions import Reject

from django.conf import settings

app = Celery('tasks', backend=settings.CELERY_BACKEND_URL, broker=settings.CELERY_BROKER_URL)


class ExpresswaysException(object):
    def __init__(self, task):
        self.task = task

    def log(self, msg):
        self.task.update_state(state='APP', meta={'msg': msg})
        raise Reject(msg)
