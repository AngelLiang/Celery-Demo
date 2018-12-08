# coding=utf-8
"""
Run:

    $ celery beat -A task_app.celery -l debug -S apps.task.database.schedulers.DatabaseScheduler

"""

import datetime as dt
import logging

import sqlalchemy

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
    PeriodicTask, PeriodicTasks,
    CrontabSchedule, IntervalSchedule,
    SolarSchedule,
)
from . import session_cleanup

from apps.task.database import SessionManager
session_manager = SessionManager()
# session = session_manager()

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

    model_schedules = (
        # (schedule_type, model_type, model_field)
        (schedules.crontab, CrontabSchedule, 'crontab'),
        (schedules.schedule, IntervalSchedule, 'interval'),
        (schedules.solar, SolarSchedule, 'solar'),
    )
    # 存储的字段，以下数据库的字段会被本程序修改
    save_fields = ['last_run_at', 'total_run_count', 'no_changes']

    def __init__(self, model, Session, app=None, **kw):
        """Initialize the model entry."""
        self.app = app or current_app._get_current_object()
        self.Session = Session

        self.name = model.name
        self.task = model.task

        try:
            self.schedule = model.schedule
            debug('schedule: {}'.format(self.schedule))
        except Exception:
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
        # 因为从数据库读取的 last_run_at 可能没有时区信息，所以这里必须加上时区信息
        self.last_run_at = self.last_run_at.replace(tzinfo=self.app.timezone)

    def _disable(self, model):
        """禁用"""
        model.no_changes = True
        model.enabled = False
        session = self.Session()
        with session_cleanup(session):
            session.add(model)
            session.commit()

    def is_due(self):
        """是否到期"""
        if not self.model.enabled:
            # 5 second delay for re-enable.
            return schedules.schedstate(False, 5.0)

        # START DATE: only run after the `start_time`, if one exists.
        if self.model.start_time is not None:
            now = maybe_make_aware(self._default_now())
            start_time = self.model.start_time.replace(tzinfo=self.app.timezone)
            if now < start_time:
                # The datetime is before the start date - don't run.
                _, delay = self.schedule.is_due(self.last_run_at)
                # use original delay for re-check
                return schedules.schedstate(False, delay)

        # ONE OFF TASK: Disable one off tasks after they've ran once
        if self.model.one_off and self.model.enabled \
                and self.model.total_run_count > 0:
            self.model.enabled = False
            self.model.total_run_count = 0  # Reset
            self.model.no_changes = False  # Mark the model entry as changed
            # 保存到数据库
            ext_fields = ('enabled',)   # 额外保存的字段
            self.save(ext_fields)
            # 这里数据库改变数据后，可能会因为没有Ssesion导致进程退出
            # session = self.Session()
            # with session_cleanup(session):
            #     session.add(self.model)
            #     session.commit()

            return schedules.schedstate(False, None)  # Don't recheck

        return self.schedule.is_due(self.last_run_at)

    def _default_now(self):
        """当前默认时间"""
        now = self.app.now()
        # The PyTZ datetime must be localised for the Django-Celery-Beat
        # scheduler to work. Keep in mind that timezone arithmatic
        # with a localized timezone may be inaccurate.
        # return now.tzinfo.localize(now.replace(tzinfo=None))
        return now.replace(tzinfo=self.app.timezone)

    def __next__(self):
        self.model.last_run_at = self.app.now()
        self.model.total_run_count += 1
        self.model.no_changes = True
        return self.__class__(self.model, Session=self.Session)
    next = __next__  # for 2to3

    def save(self, fields=tuple()):
        """
        :params fields: tuple, 额外需要保存的字段
        """
        # TODO:
        session = self.Session()
        with session_cleanup(session):
            # Object may not be synchronized, so only
            # change the fields we care about.
            # 对象可能没有同步，所以只修改我们关心的字段。
            obj = session.query(PeriodicTask).get(self.model.id)
            # 获取需要保存的字段并更新model
            for field in self.save_fields:
                setattr(obj, field, getattr(self.model, field))
            for field in fields:
                setattr(obj, field, getattr(self.model, field))
            session.add(obj)
            session.commit()

    @classmethod
    def to_model_schedule(cls, session, schedule):
        for schedule_type, model_type, model_field in cls.model_schedules:
            # 转换为 schedule
            schedule = schedules.maybe_schedule(schedule)
            if isinstance(schedule, schedule_type):
                # TODO:
                model_schedule = model_type.from_schedule(session, schedule)

                session.add(model_schedule)
                session.commit()

                return model_schedule, model_field
        raise ValueError(
            'Cannot convert schedule type {0!r} to model'.format(schedule))

    @classmethod
    def from_entry(cls, name, Session, app=None, **entry):
        """从entry加载数据

        **entry sample:

            {'task': 'celery.backend_cleanup',
             'schedule': <crontab: 0 4 * * * (m/h/d/dM/MY)>,
             'options': {'expires': 43200}}

        """
        session = Session()
        with session_cleanup(session):
            periodic_task = session.query(
                PeriodicTask).filter_by(name=name).first()
            if not periodic_task:
                periodic_task = PeriodicTask()
                periodic_task.name = name
            temp = cls._unpack_fields(session, **entry)
            periodic_task.update(**temp)
            session.add(periodic_task)
            try:
                session.commit()
            except sqlalchemy.exc.IntegrityError as exc:
                logger.error(exc)
                session.rollback()
            except Exception as exc:
                logger.error(exc)
                session.rollback()

        return cls(periodic_task, app=app, Session=Session)

    @classmethod
    def _unpack_fields(cls, session, schedule,
                       args=None, kwargs=None, relative=None, options=None,
                       **entry):
        """解包成字段

        **entry sample:

            {'task': 'celery.backend_cleanup',
             'schedule': <crontab: 0 4 * * * (m/h/d/dM/MY)>,
             'options': {'expires': 43200}}

        """
        model_schedule, model_field = cls.to_model_schedule(session, schedule)
        entry.update(
            # {model_field: model_schedule},  # 需要关联的model
            {model_field + '_id': model_schedule.id},  # 需要关联的model_id
            args=dumps(args or []),
            kwargs=dumps(kwargs or {}),
            **cls._unpack_options(**options or {})  # 解包
        )
        return entry

    @classmethod
    def _unpack_options(cls, queue=None, exchange=None, routing_key=None,
                        priority=None, **kwargs):
        """options解包成dict"""
        return {
            'queue': queue,
            'exchange': exchange,
            'routing_key': routing_key,
            'priority': priority,
            # 'one_off': kwargs.get('one_off') or False
        }

    def __repr__(self):
        return '<ModelEntry: {0} {1}(*{2}, **{3}) {4}>'.format(
            safe_str(self.name), self.task, safe_repr(self.args),
            safe_repr(self.kwargs), self.schedule,
        )


class DatabaseScheduler(Scheduler):

    Entry = ModelEntry
    Model = PeriodicTask
    Changes = PeriodicTasks

    _schedule = None
    _last_timestamp = None
    _initial_read = True
    _heap_invalidated = False

    def __init__(self, *args, **kwargs):
        """Initialize the database scheduler."""
        self.app = kwargs['app']
        self.dburi = kwargs.get('dburi') or self.app.conf.get(
            'beat_dburi') or 'sqlite:///schedule.db'
        self.engine, self.Session = session_manager.create_session(self.dburi)

        self._dirty = set()
        Scheduler.__init__(self, *args, **kwargs)
        self._finalize = Finalize(self, self.sync, exitpriority=5)
        self.max_interval = (
            kwargs.get('max_interval') or
            self.app.conf.beat_max_loop_interval or
            DEFAULT_MAX_INTERVAL)

    def _create_session(self):
        return session_manager.session_factory(dburi=self.dburi)

    def setup_schedule(self):
        """override"""
        self.install_default_entries(self.schedule)
        self.update_from_dict(self.app.conf.beat_schedule)

    def all_as_schedule(self):
        # TODO:
        session = self.Session()
        with session_cleanup(session):
            debug('DatabaseScheduler: Fetching database schedule')
            # 获取所有使能的 PeriodicTask
            models = session.query(self.Model).filter_by(enabled=True).all()
            s = {}
            for model in models:
                try:
                    s[model.name] = self.Entry(model, session=session, Session=self.Session, app=self.app)
                except ValueError:
                    pass
            return s

    def schedule_changed(self):
        # TODO:
        session = self.Session()
        with session_cleanup(session):
            changes = session.query(self.Changes).get(1)
            if not changes:
                changes = self.Changes(id=1)
                session.add(changes)
                session.commit()
                return False

            last, ts = self._last_timestamp, changes.last_update
            try:
                if ts and ts > (last if last else ts):
                    return True
            finally:
                self._last_timestamp = ts
            return False

    def reserve(self, entry):
        """override

        在父类的 tick() 中会调用
        """
        new_entry = next(entry)
        # Need to store entry by name, because the entry may change
        # in the mean time.
        self._dirty.add(new_entry.name)
        return new_entry

    def sync(self):
        """同步"""
        # TODO:
        info('Writing entries...')
        _tried = set()
        _failed = set()
        try:
            while self._dirty:
                name = self._dirty.pop()
                try:
                    self.schedule[name].save()  # 保存到数据库
                    _tried.add(name)
                except (KeyError) as exc:
                    logger.error(exc)
                    _failed.add(name)
        except sqlalchemy.exc.IntegrityError as exc:
            logger.exception('Database error while sync: %r', exc)
        except Exception as exc:
            logger.exception(exc)
        finally:
            # retry later, only for the failed ones
            self._dirty |= _failed

    def update_from_dict(self, mapping):
        s = {}
        for name, entry_fields in items(mapping):
            # {'task': 'celery.backend_cleanup',
            #  'schedule': <crontab: 0 4 * * * (m/h/d/dM/MY)>,
            #  'options': {'expires': 43200}}
            try:
                entry = self.Entry.from_entry(name, Session=self.Session, app=self.app, **entry_fields)
                if entry.model.enabled:
                    s[name] = entry
            except Exception as exc:
                logger.error(ADD_ENTRY_ERROR, name, exc, entry_fields)

        # 更新 self.schedule
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

    def schedules_equal(self, *args, **kwargs):
        if self._heap_invalidated:
            self._heap_invalidated = False
            return False
        return super(DatabaseScheduler, self).schedules_equal(*args, **kwargs)

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
        # debug(self._schedule)
        return self._schedule

    @property
    def info(self):
        """override"""
        # return infomation about Schedule
        return '    . db -> {self.dburi}'.format(self=self)
