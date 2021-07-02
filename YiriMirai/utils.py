# -*- coding: utf-8 -*-
"""
此模块提供一些实用的辅助方法。
"""
import inspect
from YiriMirai import exceptions
from typing import Callable


async def async_(coro):
    """将一个对象包装为`Awaitable`。
    """
    if inspect.isawaitable(coro):
        return await coro
    else:
        return coro


async def async_call(func: Callable, *args, **kwargs):
    """以异步的方式调用一个函数，此函数可以是同步或异步的。"""
    coro = func(*args, **kwargs)
    return await async_(coro)


async def async_call_with_exception(func: Callable, *args, **kwargs):
    """以异步的方式调用一个函数，此函数可以是同步或异步的，同时处理调用中发生的异常。"""
    try:
        return await async_call(func, *args, **kwargs)
    except Exception as e:
        exceptions.print_exception(e) # 打印异常信息，但不打断执行流程


class PriorityList(list):
    """优先级列表。

    根据应用场景优化：改动较慢，读取较快。
    """
    def add(self, priority, value):
        """添加元素。

        `priority` 优先级，小者优先。

        `value` 元素。
        """
        index = 0
        for i, (prior, data) in enumerate(self):
            if data == value:
                raise RuntimeError("优先级列表不支持重复添加元素!")
            if prior <= priority:
                index = i
        self.insert(index, (priority, value))

    def remove(self, value):
        """删除元素。

        `value` 元素。
        """
        for i, (_, data) in enumerate(self):
            if data == value:
                self.pop(i)
                return True
        else:
            return False
