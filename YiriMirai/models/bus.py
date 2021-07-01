import logging
from collections import defaultdict
from typing import Any, Callable, List, Type, Union

from YiriMirai.bus import EventBus, async_call
from YiriMirai.models.events import Event

logger = logging.getLogger(__name__)


def event_chain_parents(event: str):
    '''包含事件及所有父事件的事件链。
    例如：Event.MessageEvent.FriendMessage
    '''
    event_type = Event.get_subtype(event)
    while issubclass(event_type, Event):
        yield event_type.__name__
        event_type = event_type.__base__


class ModelEventBus(EventBus):
    '''模型事件总线，实现底层事件总线上的事件再分发，以支持解析到 Event 对象。'''
    def __init__(self):
        self.base_bus = EventBus(event_chain_generator=event_chain_parents)
        self._middlewares = defaultdict(type(None))

    def subscribe(
        self, event_type: Type[Event], func: Callable, priority: int
    ) -> None:
        async def middleware(event: dict):
            '''中间件。负责与底层 bus 沟通，将 event dict 解析为 Event 对象。
            '''
            event = Event.parse_obj(event)
            logger.debug(f'收到事件{event.type}。')
            return await async_call(func, event)

        self._middlewares[func] = middleware
        self.base_bus.subscribe(event_type.__name__, middleware, priority)
        logger.debug(f'注册事件{event_type.__name__} at {func}。')

    def unsubscribe(self, event_type: Type[Event], func: Callable) -> None:
        self.base_bus.unsubscribe(event_type.__name__, self._middlewares[func])
        del self._middlewares[func]
        logger.debug(f'解除事件注册{event_type.__name__} at {func}。')

    def on(
        self,
        event_type: Union[Type[Event], str],
        priority: int = 0
    ) -> Callable:
        if isinstance(event_type, str):
            event_type = Event.get_subtype(event_type)

        def decorator(func: Callable) -> Callable:
            self.subscribe(event_type, func, priority)
            return func

        return decorator

    async def emit(self, event: Type[Event]) -> List[Any]:
        '''触发一个事件。

        `event: Event` 要触发的事件
        '''
        return await self.base_bus.emit(event.__name__, event.dict())
