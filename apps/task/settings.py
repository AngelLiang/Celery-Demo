# coding=utf-8

import os
from datetime import timedelta


from kombu import Exchange, Queue

# 修改默认队列名称
CELERY_DEFAULT_QUEUE = 'celery-demo'
CELERY_QUEUES = (
    Queue('celery-demo', Exchange('celery-demo'), routing_key='default'),
)

# 配置时区
CELERY_TIMEZONE = 'Asia/Shanghai'

# 定时任务的配置
# 启动：celery -A task_app.celery beat -l info
CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
        'task': 'apps.task.tasks.echo',
        'schedule': timedelta(seconds=30),
        'args': ('hello',)
    },
}


# Redis
# CELERY_BROKER_URL='redis://localhost:6379'
# CELERY_RESULT_BACKEND='redis://localhost:6379'

# RabbitMQ
CELERY_BROKER_URL = os.getenv(
    'CELERY_BROKER_URL') or 'amqp://guest:guest@localhost:5672//'
CELERY_RESULT_BACKEND = os.getenv(
    'CELERY_RESULT_BACKEND') or 'amqp://guest:guest@localhost:5672//'

config_dict = dict(
    CELERY_DEFAULT_QUEUE=CELERY_DEFAULT_QUEUE,
    CELERY_QUEUES=CELERY_QUEUES,

    CELERY_TIMEZONE=CELERY_TIMEZONE,
    CELERYBEAT_SCHEDULE=CELERYBEAT_SCHEDULE,

    CELERY_BROKER_URL=CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND
)
