# -*- coding: utf-8 -*-
"""
此模块提供模型事件总线相关。

关于一般的事件总线，参看模块 `mirai.bus`。
"""
import logging
from typing import Any, Awaitable, List

from mirai.interface import EventInterface
from mirai.models.events import Event

logger = logging.getLogger(__name__)


class ModelEventBus(EventInterface[dict]):
    """模型事件总线，将事件解析到 Event 对象，并传递给指定的事件总线实现。

    模型事件总线支持的事件处理器接受唯一的参数`event`，该参数是一个 `Event` 对象，包含触发的事件的信息。

    事件触发时，会按照指定的具体事件总线实现传播。
    """
    base_bus: EventInterface[object]
    """模型事件总线基于的事件总线实现。"""
    def __init__(self, base_bus: EventInterface[object]):
        self.base_bus = base_bus

    async def emit(self, event: dict) -> List[Awaitable[Any]]:
        """触发一个事件。

        Args:
            event: 要触发的事件。
        """
        return await self.base_bus.emit(Event.parse_obj(event))
