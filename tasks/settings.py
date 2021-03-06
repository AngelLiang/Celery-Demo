# coding=utf-8

import os
from datetime import timedelta

from kombu import Exchange, Queue
from kombu.common import Broadcast

BASEDIR = os.path.realpath(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)

# 默认队列配置
task_default_queue = 'celery-demo'
task_default_exchange = 'celery-demo'
task_default_routing_key = 'celery-demo'

# delivery_mode: =1，message不写入磁盘；=2（默认）message会写入磁盘
default_exchange = Exchange('celery-demo', delivery_mode=1)
broadcast_exchange = Exchange(
    'celery-demo-broadcast',
    # type='fanout',
    delivery_mode=1
)

tasks_queues = (
    # durable: Boolean，重启后是否激活
    Queue('celery-demo', default_exchange,
          routing_key='default', auto_delete=True, durable=True),
    Broadcast('broadcast_tasks', exchange=broadcast_exchange),

    # 广播的时候似乎无法触发task1
    # Queue('task1', broadcast_exchange),
    # Queue('task2', default_exchange, routing_key='task2'),
)

# 配置路由
task_routes = {
    'broadcast_task': {
        'queue': 'broadcast_tasks',
        'exchange': 'broadcast_tasks'
    },
    'task1': {
        'queue': 'task1',
    },
}


# 配置时区
timezone = 'Asia/Shanghai'

# ### Beat Settings
# 定时任务的配置
# 启动：celery -A task_app.celery beat -l info
beat_schedule = {
    'add-every-30-seconds': {
        'task': 'apps.task.tasks.echo',
        'schedule': timedelta(seconds=30),
        'args': ('hello',)
    },
}
beat_scheduler = 'celery.beat:PersistentScheduler'
# beat_schedule = 'apps.task.database.schedulers.DatabaseScheduler'
beat_schedule_filename = 'celerybeat-schedule'
beat_sync_every = 0
# The maximum number of seconds beat can sleep between checking the schedule.
# default: 0
beat_max_loop_interval = 10
# 自定义配置
beat_dburi = 'sqlite:///schedule.db'

# RabbitMQ
broker_url = 'amqp://guest:guest@localhost:5672//'
result_backend = 'rpc://'

# Using the database to store task state and results.
# First install sqlalchemy
# $ pipenv install sqlalchemy
# result_backend = 'db+sqlite:///results.db'
# 非持久化
result_persistent = False

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# 防止内存泄漏
# 默认每个worker跑完10个任务后，自我销毁程序重建来释放内存
worker_max_tasks_per_child = 10

config_dict = dict(
    # task_default_queue=task_default_queue,
    # tasks_queues=tasks_queues,
    # task_routes=task_routes,

    timezone=timezone,
    # beat_schedule=beat_schedule,
    beat_max_loop_interval=beat_max_loop_interval,
    beat_dburi=beat_dburi,

    broker=broker_url,
    result_backend=result_backend,
    result_persistent=result_persistent,

    worker_max_tasks_per_child=worker_max_tasks_per_child
)
