# coding=utf-8
"""
定时任务

on_after_configure - Signal sent after app has prepared the configuration.
"""

from celery.schedules import crontab
from celery.utils.log import get_task_logger

from . import celery
from .tasks import echo


logger = get_task_logger(__name__)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls echo('hello') every 10 seconds.
    # sender.add_periodic_task(10.0, echo.s('hello'), name='hello every 10s')

    # Calls echo('world') every 30 seconds
    # sender.add_periodic_task(30.0, echo.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        echo.s('Happy Mondays!'),
    )
