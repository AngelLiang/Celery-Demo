# coding=utf-8
"""
Run::
    celery worker -A tasks:celery --loglevel=info
"""

import os
import sys

BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, BASEDIR)


from celery import Celery
# settings
from tasks.settings import config


celery = Celery(__name__)
celery.conf.update(config)
print(celery.conf)

from . import tasks  # noqa
