# coding=utf-8

from pytest import raises
from unittest.mock import patch

from tasks.tasks import add


def test_add_task():
    assert add.delay(4, 4).get(timeout=10) == 8


if __name__ == "__main__":
    test_add_task()
