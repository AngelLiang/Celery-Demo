# coding=utf-8

from apps.task import celery
from apps.task.tasks import echo
from apps.task.tasks import add_periodic_task as add_task


def add_periodic_task():
    # celery.add_periodic_task(3.0, echo.s('hello'), name='hello every 3s')
    add_task.delay()
