
from apps.task.database import SessionManager


def create_session():
    session_manager = SessionManager()
    session_manager.session_factory(dburi='sqlite:///schedule.db')
    return session_manager
