# coding=utf-8

import sys
import pickle
import traceback
from time import mktime
from functools import partial

from celery.five import values
from celery.beat import Scheduler

from celery import current_app

from celery.utils.log import get_logger

logger = get_logger(__name__)
debug, info, error, warning = (logger.debug, logger.info, logger.error,
                               logger.warning)
try:
    MAXINT = sys.maxint
except AttributeError:
    # python3
    MAXINT = sys.maxsize


class SqlalchemyScheduler(Scheduler):

    def __init__(self, *args, **kwargs):
        app = kwargs['app']

        Scheduler.__init__(self, *args, **kwargs)

