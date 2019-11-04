# coding=utf-8

from celery import Task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class BaseTask(Task):
    abstract = True

    def on_success(self, retval, task_id, args, kwargs):
        """任务成功处理回调函数"""
        logger.debug('task done: {0}'.format(retval))
        return super(BaseTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, error_info):
        """任务失败处理回调函数"""
        logger.debug('task fail, reason: {0}'.format(exc))
        return super(BaseTask, self).on_failure(exc, task_id, args, kwargs, error_info)
