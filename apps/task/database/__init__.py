# coding=utf-8
# flake8:noqa
"""SQLAlchemy result store backend."""
from __future__ import absolute_import, unicode_literals

import logging

from contextlib import contextmanager

from vine.utils import wraps

# from celery import states
# from celery.backends.base import BaseBackend
from celery.exceptions import ImproperlyConfigured
from celery.five import range
from celery.utils.time import maybe_timedelta

from .models import SolarSchedule
from .models import IntervalSchedule
from .models import CrontabSchedule
from .models import PeriodicTask

from .session import SessionManager

try:
    from sqlalchemy.exc import DatabaseError, InvalidRequestError
    from sqlalchemy.orm.exc import StaleDataError
except ImportError:  # pragma: no cover
    raise ImproperlyConfigured(
        'The database result backend requires SQLAlchemy to be installed.'
        'See https://pypi.org/project/SQLAlchemy/')

logger = logging.getLogger(__name__)


@contextmanager
def session_cleanup(session):
    try:
        yield
    except Exception:
        # 发生异常则回滚
        session.rollback()
        raise
    finally:
        # 无论是否发生异常都关闭连接
        session.close()


def retry(fun):

    @wraps(fun)
    def _inner(*args, **kwargs):
        max_retries = kwargs.pop('max_retries', 3)

        for retries in range(max_retries):
            try:
                return fun(*args, **kwargs)
            except (DatabaseError, InvalidRequestError, StaleDataError):
                logger.warning(
                    'Failed operation %s.  Retrying %s more times.',
                    fun.__name__, max_retries - retries - 1,
                    exc_info=True)
                if retries + 1 >= max_retries:
                    raise

    return _inner


class DatabaseBackend(object):
    """The database result backend."""

    def __init__(self, dburi=None, engine_options=None, url=None, **kwargs):
        self.url = url or dburi

        if not self.url:
            raise ImproperlyConfigured(
                'Missing connection string! Do you have the'
                ' database_url setting set to a real value?')

    def CreateSession(self, session_manager=SessionManager()):
        return session_manager.session_factory(
            dburi=self.url,
            short_lived_sessions=self.short_lived_sessions,
            **self.engine_options)
