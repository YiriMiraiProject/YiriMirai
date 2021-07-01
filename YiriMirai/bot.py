import asyncio
import inspect
import logging
from typing import Callable

from YiriMirai.adapters import Adapter, Api
from YiriMirai.bus import EventBus


class SimpleMirai(Api):
    '''基于 adapter 和 bus，处于 model 层之下的机器人对象。'''
    def __init__(self, qq: int = 0, adapter: Adapter = None):
        if qq == 0:
            raise ValueError("请指定有效的 QQ 号！")
        self.qq = qq

        if adapter is None:
            raise ValueError("请指定网络适配器！")
        self._adapter = adapter
        if self._adapter.bus:
            self._bus = self._adapter.bus
        else:
            self._bus = EventBus()
            self._adapter.bus = self._bus

        self.logger = logging.getLogger(__name__)

    async def call_api(self, api: str, **params):
        coro = self._adapter.call_api(api, **params)
        if inspect.isawaitable(coro):
            return await coro
        else:
            return coro

    def on(self, event: str, priority: int = 0) -> Callable:
        return self._bus.on(event, priority=priority)

    async def _run(self, *args, **kwargs):
        await self._adapter.login(self.qq)
        await self._adapter.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        asyncio.run(self._run(*args, **kwargs))


class Mirai(SimpleMirai):
    pass
