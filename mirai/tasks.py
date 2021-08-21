# -*- coding: utf-8 -*-
"""
此模块提供了管理多个异步任务的一种方式。
"""
import asyncio
from typing import Set


class Tasks:
    """管理多个异步任务的类。"""
    def __init__(self):
        self._tasks: Set[asyncio.Task] = set()

    def _done_callback(self, task):
        # 完成时，移除任务。
        self._tasks.remove(task)

    def create_task(self, coro) -> asyncio.Task:
        """创建一个异步任务。

        Args:
            coro: 异步任务的coroutine。

        Returns:
            asyncio.Task: 创建的任务。
        """
        task = asyncio.create_task(coro)
        self._tasks.add(task)

        task.add_done_callback(self._done_callback)
        return task

    def __iter__(self):
        """迭代可得到的任务。"""
        yield from self._tasks

    @staticmethod
    async def cancel(task: asyncio.Task):
        """取消一个任务。此方法会等待到任务取消成功。

        Args:
            task: 任务。
        """
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    async def cancel_all(self):
        """取消所有任务。此方法会等待到所有任务取消成功。"""
        for task in list(self._tasks):
            await self.cancel(task)
