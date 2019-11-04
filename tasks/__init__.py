# coding=utf-8
# flake8: noqa
"""
Run:
    celery worker -A apps.task.celery --loglevel=info
"""

import os
import sys

BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, BASEDIR)


from celery import Celery
# settings
from tasks.settings import config_dict


celery = Celery(__name__)
celery.conf.update(config_dict)

from . import tasks
