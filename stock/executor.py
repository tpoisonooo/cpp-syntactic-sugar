from task import BaseTask
from notifier import BaseNotifier
from datetime import datetime
import asyncio
from loguru import logger
# 任务执行器类
class Executor:
    def __init__(self):
        self.tasks = []
        self.notifiers = []

    def register_task(self, task):
        if isinstance(task, BaseTask):
            self.tasks.append(task)
        else:
            raise ValueError("Task must be an instance of BaseTask")

    def register_notifier(self, notifier):
        if isinstance(notifier, BaseNotifier):
            self.notifiers.append(notifier)
        else:
            raise ValueError("Notifier must be an instance of BaseNotifier")

    async def run(self):
        while True:
            logger.info(f"Running tasks at {datetime.now()}")
            messages = []
            for task in self.tasks:
                message, error = await task.execute()
                if error:
                    logger.error(f"Error executing task {task.__class__.__name__}: {error}")
                    continue
                if not message:
                    logger.warning(f"No message returned from task {task.__class__.__name__}")
                    continue
                print(f"Task result: {message}")
                messages.append(message)
            
            for notifier in self.notifiers:
                await notifier.execute(messages)
                
            await asyncio.sleep(8*3600)  # 每小时运行一次
