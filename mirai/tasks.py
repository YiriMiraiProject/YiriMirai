import asyncio


class Tasks():
    """管理多个异步任务的类。"""
    def __init__(self):
        self._tasks = set()

    def create_task(self, coro):
        """创建一个异步任务。"""
        task = asyncio.create_task(coro)
        self._tasks.add(task)

        def done_callback(task):
            # 完成时，移除任务。
            self._tasks.remove(task)

        task.add_done_callback(done_callback)
        return task

    def __iter__(self):
        """迭代可得到的任务。"""
        yield from self._tasks

    def cancel_all(self):
        """取消所有任务。"""
        for task in self._tasks:
            task.cancel()
