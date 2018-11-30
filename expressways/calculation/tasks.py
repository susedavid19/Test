from celery import Celery

app = Celery('tasks', backend='rpc://', broker='pyamqp://guest@queue//')

@app.task
def add(x, y):
    return x + y
