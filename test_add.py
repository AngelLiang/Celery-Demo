# coding=utf-8

from apps.task.tasks import add

if __name__ == "__main__":
    add.delay(1, 2)
