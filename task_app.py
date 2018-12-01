# cofing=utf-8
# flake8: noqa
"""
Run:
    celery worker -A task_app.celery --loglevel=info
"""

from apps.task import celery
