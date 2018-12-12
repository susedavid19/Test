from celery import Celery

app = Celery('tasks', backend='rpc://', broker='pyamqp://guest@queue//')
