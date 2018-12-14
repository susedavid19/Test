from celery import Celery

app = Celery('tasks', backend='rpc://', broker='pyamqp://guest@queue//')
app.conf.broker_transport_options = {
    'max_retries': 4,
    'interval_start': 0,
    'interval_step': 0.5,
    'interval_max': 3,
}
# https://github.com/celery/celery/issues/4895
app.conf.broker_heartbeat = 0
