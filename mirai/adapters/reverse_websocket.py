# -*- coding: utf-8 -*-
"""
此模块提供反向 WebSocket 适配器，适用于 mirai-api-http 的 reverse websocket adapter。
"""
from mirai.adapters.base import Adapter
from mirai.api_provider import Method


class ReverseWebSocketAdapter(Adapter):
    """反向 WebSocket 适配器。作为 WebSocket 服务器与 mirai-api-http 沟通。
    """
    async def login(self, qq: int):
        raise NotImplementedError(
            "由于 mirai-api-http 的反向 WebSocket 尚不完善，该适配器尚未实现。"
        )

    async def logout(self):
        pass

    async def _call_api(self, api: str, method: Method = Method.GET, **params):
        pass

    async def _background(self):
        pass

    @property
    def asgi(self):
        pass
