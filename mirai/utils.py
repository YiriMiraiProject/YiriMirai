# -*- coding: utf-8 -*-
"""
此模块提供一些实用的辅助方法。
"""
import inspect
from collections import defaultdict
from typing import Dict, Generic, List, Set, TypeVar, cast

from mirai.exceptions import print_exception


async def async_(obj):
    """将一个对象包装为 `Awaitable`。"""
    return (await obj) if inspect.isawaitable(obj) else obj


async def async_with_exception(obj):
    """异步包装一个对象，同时处理调用中发生的异常。"""
    try:
        return await async_(obj)
    except Exception as e:
        print_exception(e)  # 打印异常信息，但不打断执行流程


T = TypeVar('T')


class PriorityDict(Generic[T]):
    """以优先级为键的字典。"""
    def __init__(self):
        self._data: Dict[int, Set[T]] = defaultdict(set)
        self._priorities = {}

    def add(self, priority: int, value: T) -> None:
        """增加一个元素。

        Args:
            priority: 优先级，小者优先。
            value: 元素。
        """
        self._data[priority].add(value)
        self._priorities[value] = priority

    def remove(self, value: T) -> None:
        """移除一个元素。

        Args:
            value: 元素。
        """
        priority = self._priorities.get(value)
        if priority is None:
            raise KeyError(value)

        self._data[priority].remove(value)
        del self._priorities[value]

    def __iter__(self):
        if self._data:
            _, data = zip(*sorted(self._data.items()))
            yield from cast(List[Set[T]], data)
        else:
            yield from cast(List[Set[T]], ())


class SingletonMetaclass(type):
    """单例类元类。修改了单例类的 `__init__` 方法，使之只会被调用一次。"""
    def __new__(cls, name, bases, attrs, **kwargs):
        new_cls = super().__new__(cls, name, bases, attrs, **kwargs)

        # noinspection PyTypeChecker
        __init__ = new_cls.__init__

        def __init__new(self, *args, **kwargs_):
            if self._instance is None:
                __init__(self, *args, **kwargs_)

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
        if cls._args == (args, kwargs):
            return cls._instance
        raise RuntimeError(f"只能创建 {cls.__name__} 的一个实例！")
