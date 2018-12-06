# coding=utf-8

import sys
import pickle
import traceback
from time import mktime
from functools import partial

from celery.five import values
from celery.beat import Scheduler
from redis import StrictRedis
from celery import current_app

from celery.utils.log import get_logger
from redis.exceptions import LockError

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
        self.key = app.conf.get("CELERY_REDIS_SCHEDULER_KEY",
                                "celery:beat:order_tasks")
        self.schedule_url = app.conf.get("CELERY_REDIS_SCHEDULER_URL",
                                         "redis://localhost:6379")
        self.rdb = StrictRedis.from_url(self.schedule_url)
        Scheduler.__init__(self, *args, **kwargs)
        app.add_task = partial(self.add, self)

        self.multi_node = app.conf.get("CELERY_REDIS_MULTI_NODE_MODE", False)
        # how long we should hold on to the redis lock in seconds
        if self.multi_node:
            self.lock_ttl = current_app.conf.get(
                "CELERY_REDIS_SCHEDULER_LOCK_TTL", 30)
            self._lock_acquired = False
            self._lock = self.rdb.lock(
                'celery:beat:task_lock', timeout=self.lock_ttl)
            self._lock_acquired = self._lock.acquire(blocking=False)
