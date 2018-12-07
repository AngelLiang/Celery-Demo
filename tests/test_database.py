
from apps.task.database import SessionManager

from apps.task.database.models import SolarSchedule
from apps.task.database.models import IntervalSchedule
from apps.task.database.models import CrontabSchedule
from apps.task.database.models import PeriodicTask


def create_session():
    session_manager = SessionManager()
    session = session_manager.session_factory(dburi='sqlite:///schedule.db')
    return session


def create_periodic_task(session):
    periodic_task = PeriodicTask()
    session.add(periodic_task)
    session.commit()


def get_all_periodic_task(session):
    return session.query(PeriodicTask).all()
