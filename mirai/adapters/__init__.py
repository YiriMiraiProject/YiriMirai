# -*- coding: utf-8 -*-
"""
此模块提供网络适配器相关。

网络适配器负责与 mirai-api-http 沟通，详见各子模块。
"""
from typing import TYPE_CHECKING
from .base import Adapter
if TYPE_CHECKING:
    from .compose import ComposeAdapter
    from .http import HTTPAdapter
    from .webhook import WebHookAdapter
    from .websocket import WebSocketAdapter


def __getattr__(name):
    import importlib
    MODULES = {
        'Adapter': '.base',
        'ComposeAdapter': '.compose',
        'HTTPAdapter': '.http',
        'WebHookAdapter': '.webhook',
        'WebSocketAdapter': '.websocket',
    }
    if name in MODULES:
        module_name = MODULES[name]
        module = importlib.import_module(module_name, __name__)
        return getattr(module, name)


__all__ = [
    'Adapter',
    'HTTPAdapter',
    'WebSocketAdapter',
    'WebHookAdapter',
    'ComposeAdapter',
]
