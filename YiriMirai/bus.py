import asyncio
from collections import defaultdict
import inspect
from typing import Callable, List, Any

from .utils import PriorityList


class EventBus(object):
    '''事件总线。
    '''
    _default_bus = None

    def __init__(self):
        self._subscribers = defaultdict(PriorityList)

    def subscribe(self, event: str, func: Callable, priority: int) -> None:
        self._subscribers[event].add(priority, func)

    def unsubscribe(self, event: str, func: Callable) -> None:
        self._subscribers[event].remove(func)

    def on(self, event: str, priority: int = 0) -> Callable:
        def decorator(func: Callable) -> Callable:
            self.subscribe(event, func, priority)
            return func

        return decorator

    async def emit(self, event: str, *args, **kwargs) -> List[Any]:
        results = []
        while True:
            coros = []
            for _, f in self._subscribers[event]:
                coro = f(*args, **kwargs)
                # 同时支持同步和异步的事件处理函数
                if inspect.isawaitable(coro):
                    coros.append(coro)
                else:
                    results.append(coro)
            if coros:
                results += await asyncio.gather(*coros)
            event, *sub_event = event.rsplit('.', maxsplit=1)  # 由下到上依次触发
            if not sub_event:
                # 顶层事件触发完成
                break
        return results

    @classmethod
    def get_default_bus(cls):
        '''获取默认事件总线。'''
        if not cls._default_bus:
            cls._default_bus = cls()
        return cls._default_bus
