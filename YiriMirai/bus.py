# -*- coding: utf-8 -*-
import asyncio

import logging
from collections import defaultdict
from typing import Any, Callable, Iterable, List

from YiriMirai.utils import PriorityList, async_call_with_exception

logger = logging.getLogger(__name__)


def event_chain_separator(sep: str = '.'):
    '''按照分隔符划分事件链，默认按点号划分。

    比如：`"Event.MyEvent"` 所在事件链为 `["Event.MyEvent", "Event"]`。'''
    def generator(event: str):
        while True:
            yield event
            event, *sub_event = event.rsplit(sep, maxsplit=1) # 由下到上依次触发
            if not sub_event: # 顶层事件触发完成
                break

    return generator


def event_chain_single(event: str):
    '''只包含单一事件的事件链。'''
    yield event


class EventBus(object):
    '''事件总线。'''
    _default_bus = None

    def __init__(
        self,
        event_chain_generator: Callable[[str],
                                        Iterable[str]] = event_chain_single
    ):
        '''事件总线。
        `event_chain_generator: Callable[[str], Iterable[str]]`
            一个函数，输入时间名，返回一个生成此事件所在事件链的全部事件的事件名的生成器，
            默认行为是事件链只包含单一事件。
        '''
        self._subscribers = defaultdict(PriorityList)
        self.event_chain_generator = event_chain_generator

    def subscribe(self, event: str, func: Callable, priority: int) -> None:
        '''注册事件处理器。'''
        self._subscribers[event].add(priority, func)

    def unsubscribe(self, event: str, func: Callable) -> None:
        '''移除事件处理器。'''
        if not self._subscribers[event].remove(func):
            logger.warn(f'试图移除事件`{event}`的一个不存在的事件处理器`{func}`。')

    def on(self, event: str, priority: int = 0) -> Callable:
        '''注册事件处理器。'''
        def decorator(func: Callable) -> Callable:
            self.subscribe(event, func, priority)
            return func

        return decorator

    async def emit(self, event: str, *args, **kwargs) -> List[Any]:
        '''触发一个事件。

        `event: str` 要触发的事件名称
        `*args, **kwargs` 传递给事件处理器的参数
        '''
        results = []
        for m_event in self.event_chain_generator(event):
            coros = [
                async_call_with_exception(f, *args, **kwargs)
                for _, f in self._subscribers[m_event]
            ]
            if coros:
                results += await asyncio.gather(*coros)
        return results

    @classmethod
    def get_default_bus(cls):
        '''获取默认事件总线。'''
        if not cls._default_bus:
            cls._default_bus = cls()
        return cls._default_bus
