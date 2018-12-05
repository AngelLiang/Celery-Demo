# coding=utf-8

from celery.schedules import crontab
# from celery.utils.log import get_task_logger

from . import celery
from .tasks import echo


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, echo.s('hello'), name='add every 10')
    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, echo.s('world'), expires=10)
    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        echo.s('Happy Mondays!'),
    )
