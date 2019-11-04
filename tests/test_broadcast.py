# coding=utf-8

from tasks.tasks import celery
from tasks.tasks import broadcast_task

if __name__ == "__main__":
    broadcast_task.apply_async()
    # call by task name
    # celery.send_task('broadcast_task')
