# -*- coding: utf-8 -*-
"""
此模块提供网络适配器相关。

网络适配器负责与 mirai-api-http 沟通，详见各子模块。
"""
from typing import TYPE_CHECKING

from mirai.adapters.base import Adapter

if TYPE_CHECKING:
    from mirai.adapters.compose import ComposeAdapter
    from mirai.adapters.http import HTTPAdapter
    from mirai.adapters.webhook import WebHookAdapter
    from mirai.adapters.websocket import WebSocketAdapter


def __getattr__(name:str):
    import importlib
    MODULES = {
        'ComposeAdapter': '.compose',
        'HTTPAdapter': '.http',
        'WebHookAdapter': '.webhook',
        'WebSocketAdapter': '.websocket',
    }
    if name in MODULES:
        module_name = MODULES[name]
        module = importlib.import_module(module_name, __name__)
        return getattr(module, name)
    raise AttributeError(f'Module {__name__} has no attribute {name}')


__all__ = [
    'Adapter',
    'HTTPAdapter',
    'WebSocketAdapter',
    'WebHookAdapter',
    'ComposeAdapter',
]
