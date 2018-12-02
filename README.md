# celery demo

Celery 示例代码，主要用于学习。

## 环境

- Windows 10
- Pyhton 3
- Celery 3.1.25
- RabbitMQ

## 快速开始

```PowerShell
# PowerShell 1
pipenv install --dev
pipenv shell
celery worker -A task_app.celery --loglevel=info
```

### 任务发生异常时的处理

```PowerShell
# PowerShell 2
pipenv shell
python test.py
```

### 定时任务

```PowerShell
celery -A task_app.celery beat -l info
```
