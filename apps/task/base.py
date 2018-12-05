# coding=utf-8

from celery import Task


class BaseTask(Task):
    abstract = True

    def on_success(self, retval, task_id, args, kwargs):
        print('task done: {0}'.format(retval))
        return super(BaseTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, error_info):
        print('task fail, reason: {0}'.format(exc))
        return super(BaseTask, self).on_failure(exc, task_id, args, kwargs, error_info)
