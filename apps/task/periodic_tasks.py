# coding=utf-8
"""
定时任务

on_after_configure - Signal sent after app has prepared the configuration.
"""

from celery.schedules import crontab
from celery.utils.log import get_task_logger

from . import celery
from .tasks import echo
from celery import signature

logger = get_task_logger(__name__)


class PeriodicTask(object):
    """定时任务model"""
    id = None
    crontab = 10.0
    task_name = 'echo'
    args = ('hello',)

    def to_dict(self):
        d = dict(
            id=self.id,
            crontab=self.crontab,
            task_name=self.task_name,
            args=self.args
        )
        return d


def get_periodic_tasks_from_db():
    """从数据库返回定时任务的列表"""
    task_list = [PeriodicTask()]
    return task_list


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls echo('hello') every 10 seconds.
    # sender.add_periodic_task(10.0, echo.s('hello'), name='hello every 10s')

    # 使用 signature 获取 task
    # sender.add_periodic_task(10.0, signature('echo', args=('hello', )))

    task_list = get_periodic_tasks_from_db()
    for task in task_list:
        temp = task.to_dict()
        print(temp)
        sender.add_periodic_task(temp['crontab'], signature(
            temp['task_name'], args=temp['args'])
        )
        print('add task ' + temp['task_name'])

    # Calls echo('world') every 30 seconds
    sender.add_periodic_task(30.0, echo.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        echo.s('Happy Mondays!'),
    )
