import re
from typing import List, cast

from mirai.models.base import MiraiIndexedMetaclass, MiraiIndexedModel


class MessageComponentMetaclass(MiraiIndexedMetaclass):
    """消息组件元类。"""
    __parameter_names__: List[str]
    __message_component__ = None

    def __new__(cls, name, bases, *args, **kwargs):
        new_cls = cast(
            MessageComponentMetaclass,
            super().__new__(cls, name, bases, *args, **kwargs)
        )
        if name == 'MessageComponent':
            cls.__message_component__ = new_cls

        if not cls.__message_component__:
            return new_cls

        for base in bases:
            if issubclass(base, cls.__message_component__):
                # 获取字段名
                if hasattr(new_cls, '__fields__'):
                    # 忽略 type 字段
                    new_cls.__parameter_names__ = list(new_cls.__fields__)[1:]
                else:
                    new_cls.__parameter_names__ = []
                break

        return new_cls


class MessageComponent(MiraiIndexedModel, metaclass=MessageComponentMetaclass):
    """消息组件。"""
    type: str
    """消息组件类型。"""
    def __str__(self) -> str:
        return ''

    def as_mirai_code(self) -> str:
        """转化为 mirai 码。"""
        return ''

    def __repr_args__(self):
        return [(k, v) for k, v in self.__dict__.items() if k != 'type' and v]

    def __init__(self, *args, **kwargs):
        # 解析参数列表，将位置参数转化为具名参数
        parameter_names = self.__class__.__parameter_names__
        if len(args) > len(parameter_names):
            raise TypeError(
                f'`{self.type}`需要{len(parameter_names)}个参数，但传入了{len(args)}个。'
            )
        for name, value in zip(parameter_names, args):
            if name in kwargs:
                raise TypeError(f'在 `{self.type}` 中，具名参数 `{name}` 与位置参数重复。')
            kwargs[name] = value

        super().__init__(**kwargs)


class Plain(MessageComponent):
    """纯文本。"""
    type: str = "Plain"
    """消息组件类型。"""
    text: str
    """文字消息。"""
    def __str__(self):
        return self.text

    def as_mirai_code(self) -> str:
        return serialize(self.text)

    def __eq__(self, other: object):
        if isinstance(other, Plain):
            return self.text == other.text
        if isinstance(other, str):
            return self.text == other
        return NotImplemented

    def __repr_str__(self, _):
        return repr(self.text)


def serialize(s: str) -> str:
    """mirai 码转义。

    Args:
        s: 待转义的字符串。

    Returns:
        str: 去转义后的字符串。
    """
    return re.sub(r'[\[\]:,\\]', lambda match: '\\' + match.group(0),
                  s).replace('\n', '\\n').replace('\r', '\\r')


def deserialize(s: str) -> str:
    """mirai 码去转义。

    Args:
        s: 待去转义的字符串。

    Returns:
        str: 去转义后的字符串。
    """
    return re.sub(
        r'\\([\[\]:,\\])', lambda match: match.group(1),
        s.replace('\\n', '\n').replace('\\r', '\r')
    )
