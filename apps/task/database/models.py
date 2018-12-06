# coding=utf-8

import datetime as dt

import sqlalchemy as sa
# from sqlalchemy.types import PickleType

# from celery import states
from celery.five import python_2_unicode_compatible

from .session import ModelBase

DAYS = 'days'
HOURS = 'hours'
MINUTES = 'minutes'
SECONDS = 'seconds'
MICROSECONDS = 'microseconds'


def cronexp(field):
    """Representation of cron expression."""
    return field and str(field).replace(' ', '') or '*'


@python_2_unicode_compatible
class SolarSchedule(ModelBase):
    __tablename__ = 'celery_solar_schedule'
    __table_args__ = {'sqlite_autoincrement': True}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    event = sa.Column(sa.String(24))
    latitude = sa.Column(sa.Float())
    longitude = sa.Column(sa.Float())


@python_2_unicode_compatible
class IntervalSchedule(ModelBase):
    __tablename__ = 'celery_interval_schedule'
    __table_args__ = {'sqlite_autoincrement': True}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    every = sa.Column(sa.Integer, nullable=False)
    period = sa.Column(sa.String(24))

    def __str__(self):
        if self.every == 1:
            return 'every {0.period_singular}'.format(self)
        return 'every {0.every} {0.period}'.format(self)

    @property
    def period_singular(self):
        return self.period[:-1]


@python_2_unicode_compatible
class CrontabSchedule(ModelBase):
    __tablename__ = 'celery_crontab_schedule'
    __table_args__ = {'sqlite_autoincrement': True}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    minute = sa.Column(sa.String(60 * 4), default='*')
    hour = sa.Column(sa.String(24 * 4), default='*')
    day_of_week = sa.Column(sa.String(64), default='*')
    day_of_month = sa.Column(sa.String(31 * 4), default='*')
    month_of_year = sa.Column(sa.String(64), default='*')
    timezone = sa.Column(sa.String(64), default='UTC')

    def __str__(self):
        return '{0} {1} {2} {3} {4} (m/h/d/dM/MY) {5}'.format(
            cronexp(self.minute), cronexp(self.hour),
            cronexp(self.day_of_week), cronexp(self.day_of_month),
            cronexp(self.month_of_year), str(self.timezone)
        )

    @classmethod
    def from_schedule(cls, schedule):
        pass


@python_2_unicode_compatible
class PeriodicTask(ModelBase):

    __tablename__ = 'celery_periodic_task'
    __table_args__ = {'sqlite_autoincrement': True}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    # 名称
    name = sa.Column(sa.String(200), unique=True)
    # 任务名称
    task_name = sa.Column(sa.String(200), unique=True)

    interval = sa.Column(sa.ForeignKey(IntervalSchedule.id), nullable=True)

    crontab = sa.Column(sa.ForeignKey(CrontabSchedule.id), nullable=True)

    solar = sa.Column(sa.ForeignKey(SolarSchedule.id), nullable=True)

    # 参数
    args = sa.Column(sa.Text(), default='[]')
    kwargs = sa.Column(sa.Text(), default='{}')
    # 队列
    queue = sa.Column(sa.String(200), nullable=True)
    # 交换器
    exchange = sa.Column(sa.String(200), nullable=True)
    # 路由键
    routing_key = sa.Column(sa.String(200), nullable=True)
    # 优先级
    priority = sa.Column(sa.Integer(), nullable=True)

    expires = sa.Column(sa.DateTime(), nullable=True)

    one_off = sa.Column(sa.Boolean(), default=False)

    # 开始时间
    start_time = sa.Column(sa.DateTime(), nullable=True)
    # 使能/禁能
    enabled = sa.Column(sa.Boolean(), default=True)
    # 最后运行时间
    last_run_at = sa.Column(sa.DateTime(), nullable=True)
    # 总运行次数
    total_run_count = sa.Column(sa.Integer(), default=0)
    # 修改时间
    date_changed = sa.Column(
        sa.DateTime(), default=dt.datetime.now, onupdate=dt.datetime.now)
    # 说明
    description = sa.Column(sa.Text(), default='')

    no_changes = False

    def __str__(self):
        fmt = '{0.name}: {{no schedule}}'
        if self.interval:
            fmt = '{0.name}: {0.interval}'
        if self.crontab:
            fmt = '{0.name}: {0.crontab}'
        if self.solar:
            fmt = '{0.name}: {0.solar}'
        return fmt.format(self)

    @property
    def schedule(self):
        if self.interval:
            return self.interval.schedule
        if self.crontab:
            return self.crontab.schedule
        if self.solar:
            return self.solar.schedule
