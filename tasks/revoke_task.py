# coding=utf-8

from . import celery


def revoke_task(task_id):
    """通过task_id取消任务"""
    celery.control.revoke(task_id)
