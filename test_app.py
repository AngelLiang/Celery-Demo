
from tests.test_add import test_add_task
from tests.test_add_periodic_task import add_periodic_task
from tests.test_database import create_session, create_periodic_task, get_all_periodic_task

if __name__ == "__main__":
    # test_add_task()
    # add_periodic_task()
    session = create_session()
    create_periodic_task(session)
    all_periodic_task = get_all_periodic_task(session)
    print(all_periodic_task)
