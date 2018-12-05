# coding=utf-8

from celery.utils.log import get_task_logger

from . import celery
from .base import BaseTask


logger = get_task_logger(__name__)


@celery.task(name='add', base=BaseTask)
def add(x, y):
    return x + y


@celery.task(name='echo', base=BaseTask, ignore_result=True)
def echo(data):
    logger.info(data)


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
