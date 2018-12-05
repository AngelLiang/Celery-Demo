# celery demo

Celery 示例代码，主要用于学习。

## 环境

- Windows 10
- Pyhton 3
- Celery 4.1+
- RabbitMQ

> 注意：Celery 4.0 不支持 Windows。Celery 4.1 开始支持。

## 快速开始

### 安装虚拟环境

````PowerShell
pipenv install --dev
pipenv shell
```

### 启动 Celery

Windows 环境下启动 Celery 前需要先设置下面的环境变量，不然后面执行任务时，Celery 后端会报错。

```PowerShell
# PowerShell
$ $env:FORKED_BY_MULTIPROCESSING=1
# check
$ $env:FORKED_BY_MULTIPROCESSING
1

# OR cmd
# set FORKED_BY_MULTIPROCESSING=1
````

也可以在主目录下创建`.env`文件，写入`FORKED_BY_MULTIPROCESSING = 1`并安装`python-dotenv`，当`pipenv shell`进入虚拟环境命令行的时候就会自动加载该变量。

最后启动 celery：

```PowerShell
celery worker -A task_app.celery -l info
```

## 测试

以下命令都是在`pipenv shell`虚拟环境命令行下调用。

### add 任务调用

```PowerShell
python test_add.py
```

### 任务发生异常时的处理

```PowerShell
python test_error.py
```

### 定时任务

```PowerShell
celery -A task_app.celery beat -l info
```
