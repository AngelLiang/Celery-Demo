# cofing=utf-8

"""
启动Work:

    $ python task_app.py worker -l info

简单任务调度示例:

    $ pipenv shell
    $ python
    >>> from apps.task import tasks
    >>> t = tasks.add.delay(1, 2)
    >>> t.get()

启动定时任务心跳：

    $ python task_app.py beat -l info

查看Celery状态：

    $ python task_app.py status

查看任务激活的队列：

    $ python task_app.py inspect active_queues

关闭Celery：

    $ python task_app.py control shutdown

"""

from apps.task import celery

if __name__ == "__main__":
    celery.start()
