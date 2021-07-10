# -*- coding: utf-8 -*-
"""
此模块提供网络适配器相关。

网络适配器负责与 mirai-api-http 沟通，详见各子模块。
"""
from .base import Adapter, ApiProvider, Method
from .http import HTTPAdapter
from .websocket import WebSocketAdapter

__all__ = [
    'ApiProvider', 'Adapter', 'Method', 'HTTPAdapter', 'WebSocketAdapter'
]
