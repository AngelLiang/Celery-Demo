# coding=utf-8

import datetime as dt
from celery.utils.log import get_task_logger

from . import celery
from .base import BaseTask


logger = get_task_logger(__name__)


@celery.task(name='add', base=BaseTask)
def add(x, y):
    return x + y


@celery.task(bind=True, name='echo', base=BaseTask, ignore_result=True)
def echo(self, data):
    logger.info(data)


@celery.task(bind=True, name='echo_timer', base=BaseTask, ignore_result=True)
def timer_task(self, data, countdown=3):
    logger.info(data)
    eta = self.request.eta
    logger.info(eta)
    logger.info(type(eta))

    # utc_format = '%Y-%m-%dT%H:%M:%SZ'
    # now_eta = dt.datetime.strptime(eta, utc_format)
    # new_eta = now_eta + dt.timedelta(3)
    # logger.info(new_eta)

    # 循环调用本任务
    # self.apply_async(('timer', countdown), countdown=countdown)


@celery.task(base=BaseTask)
def error_task():
    res = 1 / 0
    return res


@celery.task(bind=True)
def error_handler(self, uuid):
    """错误处理

    usage:

    ```
    error_task.apply_async(link_error=error_handler.s())
    ```

    """
    result = self.app.AsyncResult(uuid)
    logger.debug('Task {0} raised exception: {1!r}\n{2!r}'.format(
        uuid, result.result, result.traceback))


@celery.task(name='task1', base=BaseTask, ignore_result=True)
def task1():
    logger.info('task1')


@celery.task(name='task2', base=BaseTask, ignore_result=True)
def task2():
    logger.info('task2')


@celery.task(name='broadcast_task', ignore_result=True)
def broadcast_task():
    logger.info('broadcast task')


@celery.task(name='add-periodic-task')
def add_periodic_task(second=3.0):
    """添加定时任务"""
    logger.info('add_periodic_task')
    celery.add_periodic_task(second, echo.s(
        'hello'), name='hello every {}s'.format(second))
