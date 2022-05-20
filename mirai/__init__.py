# -*- coding: utf-8 -*-
"""
# YiriMirai
一个轻量级、低耦合的基于 mirai-api-http 的 Python SDK。

更多信息请看[文档](https://yiri-mirai.wybxc.cc/)。
"""
__version__ = '0.3.0'
__author__ = '忘忧北萱草'

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mirai.adapters import (Adapter, ComposeAdapter, HTTPAdapter,
                                WebHookAdapter, WebSocketAdapter)
else:
    from mirai.adapters import Adapter

from mirai.bot import LifeSpan, Mirai, MiraiRunner, Shutdown, Startup
from mirai.bus import EventBus
from mirai.colorlog import ColoredFormatter
from mirai.exceptions import (ApiError, NetworkError, SkipExecution,
                              StopExecution, StopPropagation)
from mirai.interface import ApiMethod
from mirai.models.events import (Event, FriendMessage, GroupMessage,
                                 MessageEvent, StrangerMessage, TempMessage)
from mirai.models.message import (App, At, AtAll, Dice, Face, File, FlashImage,
                                  Forward, ForwardMessageNode, Image, Json,
                                  MessageChain, MiraiCode, MusicShare,
                                  MusicShareKind, Plain, Poke, PokeNames,
                                  Unknown, Voice, Xml, deserialize, serialize)

__all__ = [
    'Adapter', 'ApiError', 'ApiMethod', 'App', 'At', 'AtAll', 'ComposeAdapter',
    'Dice', 'Event', 'EventBus', 'Face', 'File', 'FlashImage', 'Forward',
    'ForwardMessageNode', 'FriendMessage', 'GroupMessage', 'HTTPAdapter',
    'Image', 'Json', 'LifeSpan', 'MessageChain', 'MessageEvent', 'Mirai',
    'MiraiCode', 'MiraiRunner', 'MusicShare', 'MusicShareKind', 'NetworkError',
    'Plain', 'Poke', 'PokeNames', 'Shutdown', 'SkipExecution', 'Startup',
    'StopExecution', 'StopPropagation', 'StrangerMessage', 'TempMessage',
    'Unknown', 'Voice', 'WebHookAdapter', 'WebSocketAdapter', 'Xml',
    'deserialize', 'get_logger', 'serialize'
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = ColoredFormatter(
    '%(asctime)s - %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)
ch.setFormatter(formatter)

logger.addHandler(ch)


def get_logger() -> logging.Logger:
    """获取 YiriMirai 的模块 Logger。

    所有的模块的 Logger 都是此 Logger 的子 Logger，修改此 Logger 的属性以应用到 YiriMirai 全局。

    Returns:
        logging.Logger: 模块 Logger。
    """
    return logger


def __getattr__(name: str):
    if name in (
        'HTTPAdapter', 'WebSocketAdapter', 'WebHookAdapter', 'ComposeAdapter'
    ):
        import mirai.adapters
        return getattr(mirai.adapters, name)
    raise AttributeError(f'Module {__name__} has no attribute {name}')
