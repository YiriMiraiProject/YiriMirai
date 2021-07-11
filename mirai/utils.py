# -*- coding: utf-8 -*-
"""
此模块提供一些实用的辅助方法。
"""
import sys
import inspect
from typing import Callable, List, Union

from mirai import exceptions


async def async_(obj):
    """将一个对象包装为 `Awaitable`。
    """
    if inspect.isawaitable(obj):
        return await obj
    else:
        return obj


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


def KMP(string, pattern, count: int = 1) -> List[int]:
    """KMP算法。

    `string` 待匹配字符串。

    `pattern` 模式字符串。

    `count` 至多匹配的次数。
    """
    if len(string) < len(pattern) or count < 1:
        return []

    # 生成下一个匹配子串的next数组。
    next_array = [0] * len(pattern)
    next_array[0] = 0
    j = 0
    for i in range(1, len(pattern)):
        while j > 0 and pattern[j] != pattern[i]:
            j = next_array[j - 1]
        if pattern[j] == pattern[i]:
            j += 1
        next_array[i] = j

    # 开始匹配。
    matches = []
    j = 0
    for i in range(0, len(string)):
        while j > 0 and pattern[j] != string[i]:
            j = next_array[j - 1]
        if pattern[j] == string[i]:
            j += 1
        if j == len(pattern):
            matches.append(i - j + 1)
            j = next_array[j - 1]
        if len(matches) == count:
            break
    return matches


def asgi_serve(
    app: Union[Callable, str],
    host: str = '127.0.0.1',
    port: int = 8000,
    asgi_server: str = 'auto',
    **kwargs
):
    """运行一个 ASGI 服务器。

    `app: Union[Callable, str]` ASGI 应用程序。

    `host: str = '127.0.0.1'` 服务器地址。

    `port: int = 8000` 服务器端口。

    `asgi_server='auto'` ASGI 服务器，可选的有 `hypercorn` `uvicorn` 和 `auto`。
        如果设置为 `auto`，自动寻找是否已安装可用的 ASGI 服务（`unicorn` 或 `hypercorn`），并运行。
    """

    if asgi_server == 'auto':
        try:
            from uvicorn import run
            asgi = 'uvicorn'
        except ImportError:
            try:
                from hypercorn.asyncio import serve
                from hypercorn.config import Config
                asgi = 'hypercorn'
            except ImportError:
                asgi = 'none'
    else:
        asgi = asgi_server

    if asgi == 'uvicorn':
        run(app, host=host, port=port, **kwargs)
        return True
    elif asgi == 'hypercorn':
        import asyncio
        config = Config().from_mapping(bind=f'{host}:{port}', **kwargs)
        asyncio.run(serve(app, config))
        return True
    else:
        return False