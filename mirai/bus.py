# -*- coding: utf-8 -*-
"""
此模块提供基础事件总线相关。

此处的事件总线不包含 model 层封装。包含 model 层封装的版本，请参见模块 `mirai.models.bus`。
"""
import asyncio
import inspect
import logging
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional

from mirai.utils import async_with_exception, async_call_with_exception

logger = logging.getLogger(__name__)


def event_chain_separator(sep: str = '.'):
    """按照分隔符划分事件链，默认按点号划分。

    例如使用 `event_chain_separator('.')` 时，
    `"Event.MyEvent"` 所在事件链为 `["Event.MyEvent", "Event"]`。"""
    def generator(event: str):
        while True:
            yield event
            event, *sub_event = event.rsplit(sep, maxsplit=1) # 由下到上依次触发
            if not sub_event: # 顶层事件触发完成
                break

    return generator


def event_chain_single(event: str):
    """只包含单一事件的事件链。"""
    yield event


class EventBus(object):
    """事件总线。

    事件总线提供了一个简单的方法，用于分发事件。事件处理器可以通过 `subscribe` 或 `on` 注册事件，
    并通过 `emit` 来触发事件。

    事件链（Event Chain）是一种特殊的事件处理机制。事件链包含一系列事件，其中底层事件触发时，上层事件也会响应。

    事件总线的构造函数中的 `event_chain_generator` 参数规定了生成事件链的方式。
    此模块中的 `event_chain_single` 和 `event_chain_separator` 可应用于此参数，分别生成单一事件的事件链和按照分隔符划分的事件链。
    """
    _default_bus = None

    def __init__(
        self,
        event_chain_generator: Callable[[str],
                                        Iterable[str]] = event_chain_single,
    ):
        """
        `event_chain_generator: Callable[[str], Iterable[str]]`
            一个函数，输入事件名，返回一个生成此事件所在事件链的全部事件的事件名的生成器，
            默认行为是事件链只包含单一事件。
        """
        self._subscribers: Dict[str, set] = defaultdict(set)
        self.event_chain_generator = event_chain_generator

    def subscribe(self, event: str, func: Callable) -> None:
        """注册事件处理器。

        `event: str` 事件名。

        `func: Callable` 事件处理器。
        """
        self._subscribers[event].add(func)

    def unsubscribe(self, event: str, func: Callable) -> None:
        """移除事件处理器。

        `event: str` 事件名。

        `func: Callable` 事件处理器。
        """
        try:
            self._subscribers[event].remove(func)
        except KeyError:
            logger.warn(f'试图移除事件 `{event}` 的一个不存在的事件处理器 `{func}`。')

    def on(self, event: str) -> Callable:
        """以装饰器的方式注册事件处理器。

        `event: str` 事件名。

        例如：
        ```py
        @bus.on('Event.MyEvent')
        def my_event_handler(event):
            print(event)
        ```
        """
        def decorator(func: Callable) -> Callable:
            self.subscribe(event, func)
            return func

        return decorator

    async def emit(self, event: str, *args, **kwargs) -> List[Awaitable[Any]]:
        """触发一个事件。

        异步执行说明：`await emit` 时执行事件处理器，所有事件处理器执行完后，并行运行所有快速响应。

        `event: str` 要触发的事件名称。

        `*args, **kwargs` 传递给事件处理器的参数。

        Returns: `List[Awaitable[Any]]`
            所有事件处理器的快速响应协程的 Task。
        """
        async def call(f) -> Optional[Awaitable[Any]]:
            result = await async_call_with_exception(f, *args, **kwargs)
            # 快速响应：如果事件处理器返回一个协程，那么立即运行这个协程。
            if inspect.isawaitable(result):
                return async_with_exception(result)
            else: # 当不使用快速响应时，返回值无意义。
                return None

        coros = []
        for m_event in self.event_chain_generator(event):
            coros += [(await call(f)) for f in self._subscribers[m_event]]

        results = filter(None, coros) # 只保留快速响应的返回值。
        return [asyncio.create_task(coro) for coro in results]

    @classmethod
    def get_default_bus(cls):
        """获取默认事件总线。"""
        if not cls._default_bus:
            cls._default_bus = cls()
        return cls._default_bus


__all__ = ['EventBus', 'event_chain_separator', 'event_chain_single']
