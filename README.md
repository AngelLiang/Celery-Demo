# celery demo

Celery 示例代码，主要用于学习。

## 环境

- Windows 10
- Pyhton 3
- Celery 3.1.25
- RabbitMQ

## 快速开始

```PowerShell
pipenv install --dev
pipenv shell
celery worker -A task_app.celery --loglevel=info
```
