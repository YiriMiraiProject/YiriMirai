# -*- coding: utf-8 -*-
"""
此模块提供组合适配器，可以将两个适配器组合使用。
"""

from mirai.adapters.base import Adapter
from mirai.api_provider import Method


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

        event_channel.buses = self.buses

        self.verify_key = api_channel.verify_key
        self.single_mode = api_channel.single_mode

    @property
    def adapter_info(self):
        return self.api_channel.adapter_info

    async def login(self, qq: int):
        await self.api_channel.login(qq)
        # 绑定 session
        self.event_channel.session = self.api_channel.session
        self.session = self.api_channel.session
        await self.event_channel.login(qq)

    async def logout(self):
        await self.event_channel.logout()
        await self.api_channel.logout()

    async def call_api(self, api: str, method: Method = Method.GET, **params):
        return await self.api_channel.call_api(api, method, **params)

    async def _background(self):
        await self.event_channel._background()
