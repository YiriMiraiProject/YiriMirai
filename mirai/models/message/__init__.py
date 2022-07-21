"""此模块提供消息链与消息元素相关。
"""
from typing import Iterable, Union

from mirai.models.message.base import (
    MessageComponent, Plain, deserialize, serialize
)
from mirai.models.message.chain import MessageChain
from mirai.models.message.components import (
    App, At, AtAll, Dice, Face, File, FlashImage, Forward, ForwardMessageNode,
    Image, Json, MiraiCode, MusicShare, MusicShareKind, Poke, PokeNames,
    Unknown, Voice, Xml
)

TMessage = Union[MessageChain, Iterable[Union[MessageComponent, str]],
                 MessageComponent, str]
"""可以转化为 MessageChain 的类型。"""

__all__ = [
    'MessageChain', 'MessageComponent', 'Plain', 'deserialize', 'serialize',
    'App', 'At', 'AtAll', 'Dice', 'Face', 'File', 'FlashImage', 'Forward',
    'ForwardMessageNode', 'Image', 'Json', 'MiraiCode', 'MusicShare',
    'MusicShareKind', 'Poke', 'PokeNames', 'Unknown', 'Voice', 'Xml',
    'TMessage'
]
