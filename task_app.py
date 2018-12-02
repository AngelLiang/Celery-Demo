# cofing=utf-8
# flake8: noqa
"""
Run:
    celery worker -A task_app.celery --loglevel=info

启动定期任务：
    celery -A task_app.celery beat -l info
"""

from apps.task import celery
