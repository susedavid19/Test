from celery import Celery

app = Celery('tasks', backend='redis://queue:6379/0', broker='redis://queue:6379/0')
