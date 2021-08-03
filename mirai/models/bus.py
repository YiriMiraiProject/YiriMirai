# -*- coding: utf-8 -*-
"""
此模块提供模型事件总线相关。

关于一般的事件总线，参看模块 `mirai.bus`。
"""
import logging
from collections import defaultdict
from typing import Any, Awaitable, Callable, List, Type, Union, cast

from mirai.bus import EventBus
from mirai.models.events import Event
from mirai.utils import async_call_with_exception

logger = logging.getLogger(__name__)


def event_chain_parents(event: str):
    """包含事件及所有父事件的事件链。

    例如：`FriendMessage` 的事件链为 `['FriendMessage', 'MessageEvent', 'Event']`。
    """
    event_type = Event.get_subtype(event)
    while issubclass(event_type, Event):
        yield event_type.__name__
        event_type = event_type.__base__


class ModelEventBus(EventBus):
    """模型事件总线，实现底层事件总线上的事件再分发，以将事件解析到 Event 对象。

    `ModelEventBus` 在注册事件处理器时，可使用 `Event` 类或事件名。关于可用的 `Event` 类，
    参见模块 `mirai.models.events`。

    模型事件总线支持的事件处理器接受唯一的参数`event`，该参数是一个 `Event` 对象，包含触发的事件的信息。

    事件触发时，会自动按照 `Event` 类的继承关系向上级传播。
    """
    def __init__(self):
        self.base_bus = EventBus(event_chain_generator=event_chain_parents)
        self._middlewares = defaultdict(type(None))

    def subscribe(
        self, event_type: Union[Type[Event], str], func: Callable
    ) -> None:
        """注册事件处理器。

        `event: Type[Event]` 事件类型。

        `func: Callable` 事件处理器。
        """
        if isinstance(event_type, str):
            event_type = cast(Type[Event], Event.get_subtype(event_type))

        async def middleware(event: dict):
            """中间件。负责与底层 bus 沟通，将 event dict 解析为 Event 对象。
            """
            event_model = cast(Event, Event.parse_obj(event))
            logger.debug(f'收到事件 {event_model.type}。')
            return await async_call_with_exception(func, event_model)

        self._middlewares[func] = middleware
        self.base_bus.subscribe(event_type.__name__, middleware)
        logger.debug(f'注册事件 {event_type.__name__} at {func}。')

    def unsubscribe(
        self, event_type: Union[Type[Event], str], func: Callable
    ) -> None:
        """移除事件处理器。

        `event_type: Type[Event]` 事件类型。

        `func: Callable` 事件处理器。
        """
        if isinstance(event_type, str):
            event_type = cast(Type[Event], Event.get_subtype(event_type))

        self.base_bus.unsubscribe(event_type.__name__, self._middlewares[func])
        del self._middlewares[func]
        logger.debug(f'解除事件注册 {event_type.__name__} at {func}。')

    def on(
        self,
        event_type: Union[Type[Event], str],
    ) -> Callable:
        """以装饰器的方式注册事件处理器。

        `event_type: Union[Type[Event], str]` 事件类型或事件名。

        例如：
        ```py
        @bus.on(FriendMessage)
        def my_event_handler(event: FriendMessage):
            print(event.sender.id)
        ```
        """
        def decorator(func: Callable) -> Callable:
            self.subscribe(event_type, func)
            return func

        return decorator

    async def emit(self, event: Union[Event, str], *args,
                   **kwargs) -> List[Awaitable[Any]]:
        """触发一个事件。

        `event: Event` 要触发的事件。
        """
        if isinstance(event, str):
            return await super().emit(event, *args, **kwargs)
        else:
            return await self.base_bus.emit(
                event.type, event.dict(by_alias=True, exclude_none=True)
            )
