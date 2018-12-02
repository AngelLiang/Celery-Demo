# coding=utf-8

from . import celery


@celery.task
def add(x, y):
    return x + y


@celery.task
def echo(data):
    print(data)


@celery.task
def error_task():
    res = 1 / 0
    return res


@celery.task(bind=True)
def error_handler(self, uuid):
    result = self.app.AsyncResult(uuid)
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(uuid, result.result, result.traceback))
