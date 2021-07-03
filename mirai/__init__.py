# -*- coding: utf-8 -*-
"""
# YiriMirai
一个轻量级、低耦合的基于 mirai-api-http 的 Python SDK。

更多信息参看[文档](https://yiri-mirai.vercel.app/)
"""
__version__ = '0.1.0'
__author__ = '忘忧北萱草'

import logging

from mirai.adapters import Adapter, HTTPAdapter, Method
from mirai.bot import Mirai, SimpleMirai
from mirai.bus import EventBus
from mirai.colorlog import ColoredFormatter
from mirai.models import (
    At, AtAll, Dice, Event, Face, FriendMessage, GroupMessage, MessageChain,
    MessageEvent, Plain, Poke, StrangerMessage, TempMessage, deserialize,
    serialize
)

__all__ = [
    'Mirai', 'SimpleMirai', 'Adapter', 'Method', 'HTTPAdapter', 'EventBus',
    'get_logger', 'Event', 'MessageEvent', 'FriendMessage', 'GroupMessage',
    'TempMessage', 'StrangerMessage', 'MessageChain', 'Plain', 'At', 'AtAll',
    'Dice', 'Face', 'Poke', 'serialize', 'deserialize'
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
    """
    return logger
