# -*- coding: utf-8 -*-
"""
此模块提供事件总线的默认实现。
"""
import asyncio
import functools
import inspect
import logging
from typing import (
    Any, Awaitable, Callable, Coroutine, Dict, List, Optional, cast
)

from mirai.exceptions import (
    SkipExecution, StopExecution, StopPropagation, print_exception
)
from mirai.interface import EventInterface
from mirai.utils import PriorityDict, async_with_exception

logger = logging.getLogger(__name__)

TEventHandler = Callable[[Any], Optional[Awaitable[Any]]]


class EventBus(EventInterface[object]):
    """事件总线。

    事件总线提供了一个简单的方法，用于分发事件。事件处理器可以通过 `subscribe` 或 `on` 注册事件，
    并通过 `emit` 来触发事件。

    默认的事件总线可以处理以类包装的事件，并按照类的继承传播事件。
    """
    def __init__(self):
        """"""
        self._subscribers: Dict[type, PriorityDict[TEventHandler]] = {}
        self._topological_order: List[type] = []

    def subscribe(
        self,
        event_type: type,
        func: TEventHandler,
        priority: int = 0
    ) -> None:
        """注册事件处理器。

        Args:
            event_type: 事件类型。
            func: 事件处理器。
            priority: 优先级，小者优先。
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = PriorityDict()
            # 更新拓扑排序的缓存
            l = -1
            for i, sub_event in enumerate(self._topological_order):
                if issubclass(sub_event, event_type):
                    l = i
            self._topological_order.insert(l + 1, event_type)
            self._topological_sort.cache_clear()

        self._subscribers[event_type].add(priority, func)

    def unsubscribe(self, event_type: type, func: TEventHandler) -> None:
        """移除事件处理器。

        Args:
            event_type: 事件类型。
            func: 事件处理器。
        """
        try:
            self._subscribers[event_type].remove(func)
        except KeyError:
            logger.warning(f'试图移除事件 `{event_type}` 的一个不存在的事件处理器 `{func}`。')

    def on(self, *event_types: type, priority: int = 0) -> Callable:
        """以装饰器的方式注册事件处理器。

        例如：
        ```py
        @bus.on(MyEvent)
        def my_event_handler(event: MyEvent):
            print(event)
        ```

        Args:
            *event_types: 事件类型。
            priority: 优先级，小者优先。
        """
        def decorator(func: TEventHandler) -> Callable:
            for event in event_types:
                self.subscribe(event, func, priority)
            return func

        return decorator

    @functools.lru_cache()
    def _topological_sort(self, event_type: type) -> List[type]:
        """拓扑排序。"""
        result: List[type] = []
        for base_event in self._topological_order:
            if issubclass(event_type, base_event):
                result.append(base_event)
        return result

    async def _emit(self, event: object, safe: bool) -> List[Awaitable]:
        """触发一个事件。

        Args:
            event: 要触发的事件。
            safe: 是否处理事件处理器中的异常。

        Returns:
            List[Awaitable[Any]]: 所有事件处理器的快速响应协程的 Task。
        """
        error_handler = functools.partial(
            self._emit, safe=False
        ) if safe else print_exception

        # 在 safe 为 False 时，不触发异常事件，直接打印异常。
        async def call(f) -> Optional[Awaitable]:
            result = await async_with_exception(f(event), error_handler)
            # 快速响应：如果事件处理器返回一个协程，那么立即运行这个协程。
            if inspect.isawaitable(result):
                return async_with_exception(result, error_handler)
            # 当不使用快速响应时，返回值无意义。
            return None

        coros: List[Optional[Awaitable]] = []
        try:
            for m_event_type in self._topological_sort(type(event)):
                try:
                    # 使用 list 避免 _subscribers 被改变引起错误。
                    for listeners in list(self._subscribers[m_event_type]):
                        try:
                            callee = (call(f) for f in listeners)
                            coros += await asyncio.gather(*callee)
                        except SkipExecution:
                            continue
                except StopExecution:
                    continue
        except StopPropagation:
            pass

        # 只保留快速响应的返回值。
        return [
            asyncio.create_task(cast(Coroutine, coro))
            for coro in filter(None, coros)
        ]

    async def emit(self, event: object) -> List[Awaitable]:
        """触发一个事件。

        异步执行说明：`await emit` 时执行事件处理器，所有事件处理器执行完后，并行运行所有快速响应。

        Args:
            event: 要触发的事件。

        Returns:
            List[Awaitable[Any]]: 所有事件处理器的快速响应协程的 Task。
        """
        return await self._emit(event, safe=True)


__all__ = ['EventBus', 'TEventHandler']
