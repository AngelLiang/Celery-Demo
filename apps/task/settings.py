# coding=utf-8

# import os
from datetime import timedelta

from kombu import Exchange, Queue
from kombu.common import Broadcast

# 默认队列配置
CELERY_DEFAULT_QUEUE = 'celery-demo'
CELERY_DEFAULT_EXCHANGE = 'celery-demo'
CELERY_DEFAULT_ROUTING_KEY = 'celery-demo'

# delivery_mode: =1，message不写入磁盘；=2（默认）message会写入磁盘
default_exchange = Exchange('celery-demo', delivery_mode=1)
broadcast_exchange = Exchange('celery-demo-broadcast', type='fanout', delivery_mode=1)

CELERY_QUEUES = (
    # durable: Boolean，重启后是否激活
    Queue('celery-demo', default_exchange, routing_key='default', auto_delete=True, durable=True),
    Broadcast('broadcast_tasks', exchange=broadcast_exchange),

    # 广播的时候似乎无法触发task1
    # Queue('task1', broadcast_exchange),
    # Queue('task2', default_exchange, routing_key='task2'),
)

# 配置路由
CELERY_ROUTES = {
    'broadcast_task': {
        'queue': 'broadcast_tasks'
    },
    'task1': {
        'queue': 'task1',
    },
}


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
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_RESULT_BACKEND = 'amqp://guest:guest@localhost:5672//'

config_dict = dict(
    CELERY_DEFAULT_QUEUE=CELERY_DEFAULT_QUEUE,
    CELERY_QUEUES=CELERY_QUEUES,
    CELERY_ROUTES=CELERY_ROUTES,

    CELERY_TIMEZONE=CELERY_TIMEZONE,
    CELERYBEAT_SCHEDULE=CELERYBEAT_SCHEDULE,

    CELERY_BROKER_URL=CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND
)
