# -*- coding: utf-8 -*-
import inspect
from YiriMirai import exceptions
from typing import Callable


async def async_(coro):
    if inspect.isawaitable(coro):
        return await coro
    else:
        return coro


async def async_call(func: Callable, *args, **kwargs):
    '''调用一个函数，此函数可以是同步或异步的。'''
    coro = func(*args, **kwargs)
    return await async_(coro)


async def async_call_with_exception(func: Callable, *args, **kwargs):
    '''调用一个函数，此函数可以是同步或异步的，同时处理调用中发生的异常。'''
    try:
        return await async_call(func, *args, **kwargs)
    except Exception as e:
        exceptions.print_exception(e) # 打印异常信息，但不打断执行流程


class PriorityList(list):
    '''优先级列表。

    根据应用场景优化：改动较慢，读取较快。
    '''
    def add(self, priority, value):
        index = 0
        for i, (prior, data) in enumerate(self):
            if data == value:
                raise RuntimeError("优先级列表不支持重复添加元素!")
            if prior <= priority:
                index = i
        self.insert(index, (priority, value))

    def remove(self, value):
        for i, (_, data) in enumerate(self):
            if data == value:
                self.pop(i)
                return True
        else:
            return False
