import asyncio
import inspect
from collections import defaultdict
from typing import Any, Callable, List

from YiriMirai import exceptions
from YiriMirai.utils import PriorityList


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

    async def _call(self, func: Callable, *args, **kwargs) -> Any:
        '''调用一个函数，此函数可以是同步或异步的，同时处理调用中发生的异常。'''
        try:
            coro = func(*args, **kwargs)
            if inspect.isawaitable(coro):
                return await coro
            else:
                return coro
        except Exception as e:
            exceptions.print_exception(e) # 打印异常信息，但不打断执行流程

    async def emit(self, event: str, *args, **kwargs) -> List[Any]:
        results = []
        while True:
            coros = []
            for _, f in self._subscribers[event]:
                coros.append(self._call(f, *args, **kwargs))
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
