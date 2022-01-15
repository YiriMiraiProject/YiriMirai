# -*- coding: utf-8 -*-
"""
此模块提供组合适配器，可以将两个适配器组合使用。
"""

from mirai.adapters.base import Adapter, Session
from mirai.interface import ApiMethod


class ComposeSession(Session):
    """组合适配器的会话。"""
    api_channel: Session
    event_channel: Session

    def __init__(self, api_channel: Session, event_channel: Session):
        super().__init__(api_channel.qq)
        self.api_channel = api_channel
        self.event_channel = event_channel
        self.buses = event_channel.buses

    async def _background(self):
        await self.event_channel._background()

    async def call_api(
        self, api: str, method: ApiMethod = ApiMethod.GET, *_, **params
    ):
        return await self.api_channel.call_api(api, method, **params)


class ComposeAdapter(Adapter):
    """组合适配器。使用一个适配器提供 API 调用，另一个适配器提供事件处理。"""
    api_channel: Adapter
    """提供 API 调用的适配器。"""
    event_channel: Adapter
    """提供事件处理的适配器。"""
    def __init__(self, api_channel: Adapter, event_channel: Adapter):
        """
        Args:
            api_channel: 提供 API 调用的适配器。
            event_channel: 提供事件处理的适配器。
        """
        super().__init__(
            verify_key=api_channel.verify_key,
            single_mode=api_channel.single_mode
        )
        if api_channel.verify_key != event_channel.verify_key:
            raise ValueError('组合适配器应使用相同的 verify_key。')

        self.api_channel = api_channel
        self.event_channel = event_channel

        self.verify_key = api_channel.verify_key
        self.single_mode = api_channel.single_mode

    @property
    def adapter_info(self):
        return self.api_channel.adapter_info

    async def _login(self, qq: int) -> ComposeSession:
        api = await self.api_channel.login(qq)
        ev = await self.event_channel.login(qq)
        return ComposeSession(api, ev)
