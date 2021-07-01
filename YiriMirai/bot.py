import asyncio
import inspect
import logging
from typing import Callable, Union, Type

from YiriMirai.adapters.base import Adapter, Api
from YiriMirai.bus import EventBus
from YiriMirai.models.bus import ModelEventBus
from YiriMirai.models.events import Event


class SimpleMirai(Api):
    '''基于 adapter 和 bus，处于 model 层之下的机器人类。'''
    def __init__(self, qq: int, adapter: Adapter):
        '''基于 adapter 和 bus，处于 model 层之下的机器人类。

        `qq: int` QQ 号
        `adapter: Adapter` 适配器，见`YiriMirai.adapters`
        '''
        self.qq = qq
        self._adapter = adapter
        self._bus = EventBus()
        self._adapter.register_event_bus(self._bus)

        self.logger = logging.getLogger(__name__)

    async def call_api(self, api: str, **params):
        coro = self._adapter.call_api(api, **params)
        if inspect.isawaitable(coro):
            return await coro
        else:
            return coro

    def on(self, event: str, priority: int = 0) -> Callable:
        '''注册事件处理器。

        `event: str` 事件名
        `priority: int = 0` 优先级，较小者优先

        用法举例：
        ```python
        @bot.on('FriendMessage')
        async def on_friend_message(event: dict):
            print(f"收到来自{event['sender']['nickname']}的消息。")
        ```
        '''
        return self._bus.on(event, priority=priority)

    async def _run(self, *args, **kwargs):
        await self._adapter.login(self.qq)
        await self._adapter.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        '''开始运行机器人。

        一般情况下，此函数会进入主循环，不再返回。
        '''
        asyncio.run(self._run(*args, **kwargs))


class Mirai(SimpleMirai):
    '''机器人主类。'''
    def __init__(self, qq: int, adapter: Adapter):
        '''机器人主类。

        `qq: int` QQ 号
        `adapter: Adapter` 适配器，见`YiriMirai.adapters`
        '''
        super().__init__(qq=qq, adapter=adapter)
        # 将 bus 更换为 ModelEventBus
        adapter.unregister_event_bus(self._bus)
        self._bus = ModelEventBus()
        adapter.register_event_bus(self._bus.base_bus)

    def on(self,
           event_type: Union[Type[Event], str],
           priority: int = 0) -> Callable:
        '''注册事件处理器。

        `event_type: Union[Type[Event], str]` 事件类或事件名
        `priority: int = 0` 优先级，较小者优先

        用法举例：
        ```python
        @bot.on(FriendMessage)
        async def on_friend_message(event: FriendMessage):
            print(f"收到来自{event.sender.nickname]}的消息。")
        ```
        '''
        return self._bus.on(event_type=event_type, priority=priority)
