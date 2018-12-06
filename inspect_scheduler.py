# coding=utf-8
"""
查询定时任务调度的数据
"""


import shelve

from celery.beat import PersistentScheduler

from apps.task import celery
from apps.task.settings import beat_schedule_filename

# with shelve.open(beat_schedule_filename) as db:
#     print(db)
#     print(db['entries'])


persistent_scheduler = PersistentScheduler(
    app=celery, schedule_filename=beat_schedule_filename)


def get_schedule():
    return persistent_scheduler.get_schedule()


def set_schedule():
    persistent_scheduler.set_schedule()


def add_schedule():
    persistent_scheduler.add()


if __name__ == "__main__":
    data = get_schedule()
    print(data)

    # 一定要记得close，否则python会报错
    persistent_scheduler.close()
