# coding=utf-8


class TaskRouter(object):
    def route_for_task(self, task, args=None, kwargs=None):
        if task == 'task1':
            return {
                'exchange': 'celery-demo-broadcast',
                'exchange_type': 'fanout',
                'routing_key': ''
            }
        return None
