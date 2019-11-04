# coding=utf-8

from tasks.tasks import error_task, error_handler

if __name__ == "__main__":
    # 当任务发生错误时，调用错误处理任务
    error_task.apply_async(link_error=error_handler.s())
