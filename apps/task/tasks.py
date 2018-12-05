# coding=utf-8

from celery.utils.log import get_task_logger

from . import celery
from .base import BaseTask


logger = get_task_logger(__name__)


@celery.task(name='add', base=BaseTask)
def add(x, y):
    return x + y


@celery.task(name='echo', base=BaseTask)
def echo(data):
    logger.debug(data)


@celery.task(base=BaseTask)
def error_task():
    res = 1 / 0
    return res


@celery.task(bind=True)
def error_handler(self, uuid):
    result = self.app.AsyncResult(uuid)
    logger.debug('Task {0} raised exception: {1!r}\n{2!r}'.format(
        uuid, result.result, result.traceback))
