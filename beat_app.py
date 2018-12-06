# coding=utf-8

from apps.task import celery

if __name__ == "__main__":
    celery.start(argv=[__name__, 'beat', '-l', 'info'])
