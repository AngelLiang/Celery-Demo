# coding=utf-8

# import logging

from multiprocessing.util import Finalize

from celery import current_app
from celery import schedules
from celery.beat import Scheduler, ScheduleEntry
from celery.five import values, items
from celery.utils.encoding import safe_str, safe_repr
from celery.utils.log import get_logger
from celery.utils.time import maybe_make_aware
from kombu.utils.json import dumps, loads


from .models import (
    PeriodicTask,
    CrontabSchedule, IntervalSchedule,
    SolarSchedule,
)

# This scheduler must wake up more frequently than the
# regular of 5 minutes because it needs to take external
# changes to the schedule into account.
DEFAULT_MAX_INTERVAL = 5  # seconds

ADD_ENTRY_ERROR = """\
Cannot add entry %r to database schedule: %r. Contents: %r
"""

logger = get_logger(__name__)
debug, info, warning = logger.debug, logger.info, logger.warning


class ModelEntry(ScheduleEntry):
    """Scheduler entry taken from database row."""

    def __init__(self, model, app=None):
        """Initialize the model entry."""
        self.app = app or current_app._get_current_object()
        self.name = model.name
        self.task = model.task_name
        try:
            self.schedule = model.schedule
        except model.DoesNotExist:
            logger.error(
                'Disabling schedule %s that was removed from database',
                self.name,
            )
            self._disable(model)
        try:
            self.args = loads(model.args or '[]')
            self.kwargs = loads(model.kwargs or '{}')
        except ValueError as exc:
            logger.exception(
                'Removing schedule %s for argument deseralization error: %r',
                self.name, exc,
            )
            self._disable(model)

        self.options = {}
        for option in ['queue', 'exchange', 'routing_key', 'expires',
                       'priority']:
            value = getattr(model, option)
            if value is None:
                continue
            self.options[option] = value

        self.total_run_count = model.total_run_count
        self.model = model

        if not model.last_run_at:
            model.last_run_at = self._default_now()
        self.last_run_at = model.last_run_at

    def _disable(self, model):
        """禁用"""
        model.no_changes = True
        model.enabled = False
        # model.save()

    def is_due(self):
        """是否到期"""
        pass

    def __next__(self):
        self.model.last_run_at = self.app.now()
        self.model.total_run_count += 1
        self.model.no_changes = True
        return self.__class__(self.model)
    next = __next__  # for 2to3

    def __repr__(self):
        return '<ModelEntry: {0} {1}(*{2}, **{3}) {4}>'.format(
            safe_str(self.name), self.task, safe_repr(self.args),
            safe_repr(self.kwargs), self.schedule,
        )


class DatabaseScheduler(Scheduler):

    Entry = ModelEntry
    Model = PeriodicTask
    # Changes = PeriodicTasks

    _schedule = None
    _last_timestamp = None
    _initial_read = True
    _heap_invalidated = False

    def __init__(self, *args, **kwargs):
        """Initialize the database scheduler."""
        self._dirty = set()
        Scheduler.__init__(self, *args, **kwargs)
        self._finalize = Finalize(self, self.sync, exitpriority=5)
        self.max_interval = (
            kwargs.get('max_interval')
            or self.app.conf.beat_max_loop_interval
            or DEFAULT_MAX_INTERVAL)

    def setup_schedule(self):
        self.install_default_entries(self.schedule)
        self.update_from_dict(self.app.conf.beat_schedule)

    def all_as_schedule(self):
        debug('DatabaseScheduler: Fetching database schedule')
        s = {}
        for model in self.Model.objects.enabled():
            try:
                s[model.name] = self.Entry(model, app=self.app)
            except ValueError:
                pass
        return s

    def schedule_changed(self):
        try:
            close_old_connections()

            # If MySQL is running with transaction isolation level
            # REPEATABLE-READ (default), then we won't see changes done by
            # other transactions until the current transaction is
            # committed (Issue #41).
            try:
                transaction.commit()
            except transaction.TransactionManagementError:
                pass  # not in transaction management.

            last, ts = self._last_timestamp, self.Changes.last_change()
        except DatabaseError as exc:
            logger.exception('Database gave error: %r', exc)
            return False
        except InterfaceError:
            warning(
                'DatabaseScheduler: InterfaceError in schedule_changed(), '
                'waiting to retry in next call...'
            )
            return False

        try:
            if ts and ts > (last if last else ts):
                return True
        finally:
            self._last_timestamp = ts
        return False

    def sync(self):
        """同步"""
        info('Writing entries...')

    def update_from_dict(self, mapping):
        s = {}
        for name, entry_fields in items(mapping):
            try:
                entry = self.Entry.from_entry(name,
                                              app=self.app,
                                              **entry_fields)
                if entry.model.enabled:
                    s[name] = entry

            except Exception as exc:
                logger.error(ADD_ENTRY_ERROR, name, exc, entry_fields)
        self.schedule.update(s)

    def install_default_entries(self, data):
        entries = {}
        if self.app.conf.result_expires:
            entries.setdefault(
                'celery.backend_cleanup', {
                    'task': 'celery.backend_cleanup',
                    'schedule': schedules.crontab('0', '4', '*'),
                    'options': {'expires': 12 * 3600},
                },
            )
        self.update_from_dict(entries)

    @property
    def schedule(self):
        initial = update = False
        if self._initial_read:
            debug('DatabaseScheduler: initial read')
            initial = update = True
            self._initial_read = False
        elif self.schedule_changed():
            info('DatabaseScheduler: Schedule changed.')
            update = True

        if update:
            self.sync()
            self._schedule = self.all_as_schedule()
            # the schedule changed, invalidate the heap in Scheduler.tick
            if not initial:
                self._heap = []
                self._heap_invalidated = True
            if logger.isEnabledFor(logging.DEBUG):
                debug('Current schedule:\n%s', '\n'.join(
                    repr(entry) for entry in values(self._schedule)),
                )
        return self._schedule
