# -*- coding: utf-8 -*-
"""
此模块提供一些实用的辅助方法。
"""
import inspect
from typing import Callable, List

from mirai import exceptions


async def async_(obj):
    """将一个对象包装为 `Awaitable`。
    """
    if inspect.isawaitable(obj):
        return await obj
    else:
        return obj


async def async_with_exception(obj):
    """异步包装一个对象，同时处理调用中发生的异常。"""
    try:
        return await async_(obj)
    except Exception as e:
        exceptions.print_exception(e)  # 打印异常信息，但不打断执行流程


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


class SingletonMetaclass(type):
    """单例类元类。修改了单例类的 `__init__` 方法，使之只会被调用一次。"""
    def __new__(mcs, name, bases, attrs, **kwargs):
        new_cls = super().__new__(mcs, name, bases, attrs, **kwargs)

        # noinspection PyTypeChecker
        __init__ = new_cls.__init__

        def __init__new(self, *args, **kwargs):
            if self._instance is None:
                __init__(self, *args, **kwargs)

        new_cls.__init__ = __init__new
        return new_cls


class Singleton(metaclass=SingletonMetaclass):
    """单例模式。"""
    _instance = None
    _args = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            _instance = super().__new__(cls)

            # 保存参数
            cls._args = (args, kwargs)

            # 初始化
            # noinspection PyArgumentList
            _instance.__init__(*args, **kwargs)
            cls._instance = _instance
            return _instance
        elif cls._args == (args, kwargs):
            return cls._instance
        else:
            raise RuntimeError(f"只能创建 {cls.__name__} 的一个实例！")
