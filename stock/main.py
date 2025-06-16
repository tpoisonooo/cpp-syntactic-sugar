from executor import Executor
from task import IXICTask
from notifier import WeChat
import asyncio

async def main():
    executor = Executor()
    executor.register_task(IXICTask())
    executor.register_notifier(WeChat())
    await executor.run()

# 启动异步主程序
if __name__ == "__main__":
    asyncio.run(main())
