# cofing=utf-8

"""
启动Work:

    $ celery worker -A task_app:celery -l info

    OR

    $ python task_app.py worker -l info

简单任务调度示例:

    $ pipenv shell
    $ python task_app.py shell
    >>> add.delay(1, 2).get(timeout=3)
    >>> echo.apply_async(('data', ), countdown=3)

启动定时任务心跳：

    $ celery beat -A task_app:celery -l info

    OR

    $ python task_app.py beat -l info

查看Celery状态：

    $ python task_app.py status

查看任务激活的队列：

    $ python task_app.py inspect active_queues

关闭Celery：

    $ python task_app.py control shutdown

"""

from tasks import celery

if __name__ == "__main__":
    celery.start()
