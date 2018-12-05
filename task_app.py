# cofing=utf-8
# flake8: noqa
"""
Run:

```
$ celery worker -A task_app.celery --loglevel=info
```

Usage:

```
$ pipenv shell
$ python
>>> from apps.task import tasks
>>> t = tasks.add.delay(1, 2)
>>> t.get()
```

启动定期任务：

```
$ celery -A task_app.celery beat -l info
```

查看任务激活的队列：

```
$ celery -A task_app.celery inspect active_queues
```

"""

from apps.task import celery
