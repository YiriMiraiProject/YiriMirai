# -*- coding: utf-8 -*-
"""
此模块提供消息链相关。
"""
import itertools
import logging
import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Iterable, List, Optional, Tuple, Type, TypeVar, Union, cast, overload
)

from pydantic import HttpUrl, validator

from mirai.models.base import (
    MiraiBaseModel, MiraiIndexedMetaclass, MiraiIndexedModel
)
from mirai.models.entities import Friend, GroupMember
from mirai.utils import kmp

logger = logging.getLogger(__name__)


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


class MessageComponentMetaclass(MiraiIndexedMetaclass):
    """消息组件元类。"""
    __message_component__ = None

    def __new__(cls, name, bases, attrs, **kwargs):
        new_cls = super().__new__(cls, name, bases, attrs, **kwargs)
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
    def __str__(self):
        return ''

    def as_mirai_code(self) -> str:
        """转化为 mirai 码。"""
        return ''

    def __repr__(self):
        return self.__class__.__name__ + '(' + ', '.join(
            (
                f'{k}={repr(v)}'
                for k, v in self.__dict__.items() if k != 'type' and v
            )
        ) + ')'

    def __init__(self, *args, **kwargs):
        # 解析参数列表，将位置参数转化为具名参数
        parameter_names = self.__parameter_names__
        if len(args) > len(parameter_names):
            raise TypeError(
                f'`{self.type}`需要{len(parameter_names)}个参数，但传入了{len(args)}个。'
            )
        for name, value in zip(parameter_names, args):
            if name in kwargs:
                raise TypeError(f'在 `{self.type}` 中，具名参数 `{name}` 与位置参数重复。')
            kwargs[name] = value

        super().__init__(**kwargs)


TMessageComponent = TypeVar('TMessageComponent', bound=MessageComponent)


class MessageChain(MiraiBaseModel):
    """消息链。

    一个构造消息链的例子：
    ```py
    message_chain = MessageChain([
        AtAll(),
        Plain("Hello World!"),
    ])
    ```

    `Plain` 可以省略。
    ```py
    message_chain = MessageChain([
        AtAll(),
        "Hello World!",
    ])
    ```

    在调用 API 时，参数中需要 MessageChain 的，也可以使用 `List[MessageComponent]` 代替。
    例如，以下两种写法是等价的：
    ```py
    await bot.send_friend_message(12345678, [
        Plain("Hello World!")
    ])
    ```
    ```py
    await bot.send_friend_message(12345678, MessageChain([
        Plain("Hello World!")
    ]))
    ```

    使用`str(message_chain)`获取消息链的字符串表示，字符串采用 mirai 码格式，
    并自动按照 mirai 码的规定转义。
    参看 mirai 的[文档](https://github.com/mamoe/mirai/blob/dev/docs/Messages.md#mirai-%E7%A0%81)。
    获取未转义的消息链字符串，可以使用`deserialize(str(message_chain))`。

    可以使用 for 循环遍历消息链中的消息组件。
    ```py
    for component in message_chain:
        print(repr(component))
    ```

    可以使用 `==` 运算符比较两个消息链是否相同。
    ```py
    another_msg_chain = MessageChain([
        {
            "type": "AtAll"
        }, {
            "type": "Plain",
            "text": "Hello World!"
        },
    ])
    print(message_chain == another_msg_chain)
    'True'
    ```

    可以使用 `in` 运算检查消息链中：
    1. 是否有某个消息组件。
    2. 是否有某个类型的消息组件。
    3. 是否有某个子消息链。
    4. 对应的 mirai 码中是否有某子字符串。

    ```py
    if AtAll in message_chain:
        print('AtAll')

    if At(bot.qq) in message_chain:
        print('At Me')

    if MessageChain([At(bot.qq), Plain('Hello!')]) in message_chain:
        print('Hello!')

    if 'Hello' in message_chain:
        print('Hi!')
    ```

    消息链的 `has` 方法和 `in` 等价。
    ```py
    if message_chain.has(AtAll):
        print('AtAll')
    ```

    也可以使用 `>=` 和 `<= `运算符：
    ```py
    if MessageChain([At(bot.qq), Plain('Hello!')]) <= message_chain:
        print('Hello!')
    ```

    需注意，此处的子消息链匹配会把 Plain 看成一个整体，而不是匹配其文本的一部分。
    如需对文本进行部分匹配，请采用 mirai 码字符串匹配的方式。

    消息链对索引操作进行了增强。以消息组件类型为索引，获取消息链中的全部该类型的消息组件。
    ```py
    plain_list = message_chain[Plain]
    '[Plain("Hello World!")]'
    ```

    以 `类型, 数量` 为索引，获取前至多多少个该类型的消息组件。
    ```py
    plain_list_first = message_chain[Plain, 1]
    '[Plain("Hello World!")]'
    ```

    消息链的 `get` 方法和索引操作等价。
    ```py
    plain_list_first = message_chain.get(Plain)
    '[Plain("Hello World!")]'
    ```

    消息链的 `get` 方法还可指定第二个参数 `count`，这相当于以 `类型, 数量` 为索引。
    ```py
    plain_list_first = message_chain.get(Plain, 1)
    # 这等价于
    plain_list_first = message_chain[Plain, 1]
    ```

    可以用加号连接两个消息链。
    ```py
    MessageChain(['Hello World!']) + MessageChain(['Goodbye World!'])
    # 返回 MessageChain([Plain("Hello World!"), Plain("Goodbye World!")])
    ```

    可以用 `*` 运算符复制消息链。
    ```py
    MessageChain(['Hello World!']) * 2
    # 返回 MessageChain([Plain("Hello World!"), Plain("Hello World!")])
    ```

    除此之外，消息链还支持很多 list 拥有的操作，比如 `index` 和 `count`。
    ```py
    message_chain = MessageChain([
        AtAll(),
        "Hello World!",
    ])
    message_chain.index(Plain)
    # 返回 0
    message_chain.count(Plain)
    # 返回 1
    ```

    消息链对这些操作进行了拓展。在传入元素的地方，一般都可以传入元素的类型。
    """
    __root__: List[MessageComponent]

    @staticmethod
    def _parse_message_chain(msg_chain: Iterable):
        result = []
        for msg in msg_chain:
            if isinstance(msg, dict):
                result.append(MessageComponent.parse_subtype(msg))
            elif isinstance(msg, MessageComponent):
                result.append(msg)
            elif isinstance(msg, str):
                result.append(Plain(msg))
            else:
                raise TypeError(
                    f"消息链中元素需为 dict 或 str 或 MessageComponent，当前类型：{type(msg)}"
                )
        return result

    @validator('__root__', always=True, pre=True)
    def _parse_component(cls, msg_chain):
        if isinstance(msg_chain, (str, MessageComponent)):
            msg_chain = [msg_chain]
        if not msg_chain:
            msg_chain = []
        return cls._parse_message_chain(msg_chain)

    @classmethod
    def parse_obj(cls, msg_chain: Iterable):
        """通过列表形式的消息链，构造对应的 `MessageChain` 对象。

        Args:
            msg_chain: 列表形式的消息链。
        """
        result = cls._parse_message_chain(msg_chain)
        return cls(__root__=result)

    def __init__(self, __root__: Iterable[MessageComponent] = None):
        super().__init__(__root__=__root__)

    def __str__(self):
        return "".join(str(component) for component in self.__root__)

    def as_mirai_code(self) -> str:
        """将消息链转换为 mirai 码字符串。

        该方法会自动转换消息链中的元素。

        Returns:
            mirai 码字符串。
        """
        return "".join(
            component.as_mirai_code() for component in self.__root__
        )

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__root__!r})'

    def __iter__(self):
        yield from self.__root__

    @overload
    def get(self, index: int) -> MessageComponent:
        ...

    @overload
    def get(self, index: slice) -> List[MessageComponent]:
        ...

    @overload
    def get(self, index: Type[TMessageComponent]) -> List[TMessageComponent]:
        ...

    @overload
    def get(
        self, index: Tuple[Type[TMessageComponent], int]
    ) -> List[TMessageComponent]:
        ...

    def get(
        self,
        index: Union[int, slice, Type[TMessageComponent],
                     Tuple[Type[TMessageComponent], int]],
        count: Optional[int] = None
    ) -> Union[MessageComponent, List[MessageComponent],
               List[TMessageComponent]]:
        """获取消息链中的某个（某些）消息组件，或某类型的消息组件。

        Args:
            index (`Union[int, slice, Type[TMessageComponent], Tuple[Type[TMessageComponent], int]]`):
                如果为 `int`，则返回该索引处的消息组件。
                如果为 `slice`，则返回该索引范围处的消息组件。
                如果为 `Type[TMessageComponent]`，则返回该类型的全部消息组件。
                如果为 `Tuple[Type[TMessageComponent], int]`，则返回该类型的至多 `index[1]` 个消息组件。

            count: 如果为 `int`，则返回至多 `count` 个消息组件。

        Returns:
            MessageComponent: 返回指定索引处的消息组件。
            List[MessageComponent]: 返回指定索引范围的消息组件。
            List[TMessageComponent]: 返回指定类型的消息组件构成的列表。
        """
        # 正常索引
        if isinstance(index, int):
            return self.__root__[index]
        # 切片索引
        if isinstance(index, slice):
            return self.__root__[index]
        # 指定 count
        if count:
            if isinstance(index, type):
                index = (index, count)
            elif isinstance(index, tuple):
                index = (index[0], count if count < index[1] else index[1])
        # 索引对象为 MessageComponent 类，返回所有对应 component
        if isinstance(index, type):
            return [
                component for component in self if type(component) is index
            ]
        # 索引对象为 MessageComponent 和 int 构成的 tuple， 返回指定数量的 component
        if isinstance(index, tuple):
            components = (
                component for component in self if type(component) is index[0]
            )
            return [
                component for component, _ in zip(components, range(index[1]))
            ]
        raise TypeError(f"消息链索引需为 int 或 MessageComponent，当前类型：{type(index)}")

    def get_first(self,
                  t: Type[TMessageComponent]) -> Optional[TMessageComponent]:
        """获取消息链中第一个符合类型的消息组件。"""
        for component in self:
            if isinstance(component, t):
                return component
        return None

    @overload
    def __getitem__(self, index: int) -> MessageComponent:
        ...

    @overload
    def __getitem__(self, index: slice) -> List[MessageComponent]:
        ...

    @overload
    def __getitem__(self,
                    index: Type[TMessageComponent]) -> List[TMessageComponent]:
        ...

    @overload
    def __getitem__(
        self, index: Tuple[Type[TMessageComponent], int]
    ) -> List[TMessageComponent]:
        ...

    def __getitem__(
        self, index: Union[int, slice, Type[TMessageComponent],
                           Tuple[Type[TMessageComponent], int]]
    ) -> Union[MessageComponent, List[MessageComponent],
               List[TMessageComponent]]:
        return self.get(index)

    def __setitem__(
        self, key: Union[int, slice],
        value: Union[MessageComponent, str, Iterable[Union[MessageComponent,
                                                           str]]]
    ):
        if isinstance(value, str):
            value = Plain(value)
        if isinstance(value, Iterable):
            value = (Plain(c) if isinstance(c, str) else c for c in value)
        self.__root__[key] = value  # type: ignore

    def __delitem__(self, key: Union[int, slice]):
        del self.__root__[key]

    def __reversed__(self) -> Iterable[MessageComponent]:
        return reversed(self.__root__)

    def has(
        self, sub: Union[MessageComponent, Type[MessageComponent],
                         'MessageChain', str]
    ) -> bool:
        """判断消息链中：
        1. 是否有某个消息组件。
        2. 是否有某个类型的消息组件。
        3. 是否有某个子消息链。
        4. 对应的 mirai 码中是否有某子字符串。

        Args:
            sub (`Union[MessageComponent, Type[MessageComponent], 'MessageChain', str]`):
                若为 `MessageComponent`，则判断该组件是否在消息链中。
                若为 `Type[MessageComponent]`，则判断该组件类型是否在消息链中。
                若为 `MessageChain`，则判断该子消息链是否在消息链中。
                若为 `str`，则判断对应的 mirai 码中是否有某子字符串。

        Returns:
            bool: 是否找到。
        """
        if isinstance(sub, type):  # 检测消息链中是否有某种类型的对象
            for i in self:
                if type(i) is sub:
                    return True
            return False
        if isinstance(sub, MessageComponent):  # 检查消息链中是否有某个组件
            for i in self:
                if i == sub:
                    return True
            return False
        if isinstance(sub, MessageChain):  # 检查消息链中是否有某个子消息链
            return bool(kmp(self, sub))
        if isinstance(sub, str):  # 检查消息中有无指定字符串子串
            return sub in deserialize(str(self))
        raise TypeError(f"类型不匹配，当前类型：{type(sub)}")

    def __contains__(self, sub) -> bool:
        return self.has(sub)

    def __ge__(self, other):
        return other in self

    def __len__(self) -> int:
        return len(self.__root__)

    def __add__(
        self, other: Union['MessageChain', MessageComponent, str]
    ) -> 'MessageChain':
        if isinstance(other, MessageChain):
            return self.__class__(self.__root__ + other.__root__)
        if isinstance(other, str):
            return self.__class__(self.__root__ + [Plain(other)])
        if isinstance(other, MessageComponent):
            return self.__class__(self.__root__ + [other])
        return NotImplemented

    def __radd__(self, other: Union[MessageComponent, str]) -> 'MessageChain':
        if isinstance(other, MessageComponent):
            return self.__class__([other] + self.__root__)
        if isinstance(other, str):
            return self.__class__(
                [cast(MessageComponent, Plain(other))] + self.__root__
            )
        return NotImplemented

    def __mul__(self, other: int):
        if isinstance(other, int):
            return self.__class__(self.__root__ * other)
        return NotImplemented

    def __rmul__(self, other: int):
        return self.__mul__(other)

    def __iadd__(self, other: Iterable[Union[MessageComponent, str]]):
        self.extend(other)

    def __imul__(self, other: int):
        if isinstance(other, int):
            self.__root__ *= other
        return NotImplemented

    def index(
        self,
        x: Union[MessageComponent, Type[MessageComponent]],
        i: int = 0,
        j: int = -1
    ) -> int:
        """返回 x 在消息链中首次出现项的索引号（索引号在 i 或其后且在 j 之前）。

        Args:
            x (`Union[MessageComponent, Type[MessageComponent]]`):
                要查找的消息元素或消息元素类型。
            i: 从哪个位置开始查找。
            j: 查找到哪个位置结束。

        Returns:
            int: 如果找到，则返回索引号。

        Raises:
            ValueError: 没有找到。
            TypeError: 类型不匹配。
        """
        if isinstance(x, type):
            l = len(self)
            if i < 0:
                i += l
            if i < 0:
                i = 0
            if j < 0:
                j += l
            if j > l:
                j = l
            for index in range(i, j):
                if type(self[index]) is x:
                    return index
            raise ValueError("消息链中不存在该类型的组件。")
        if isinstance(x, MessageComponent):
            return self.__root__.index(x, i, j)
        raise TypeError(f"类型不匹配，当前类型：{type(x)}")

    def count(self, x: Union[MessageComponent, Type[MessageComponent]]) -> int:
        """返回消息链中 x 出现的次数。

        Args:
            x (`Union[MessageComponent, Type[MessageComponent]]`):
                要查找的消息元素或消息元素类型。

        Returns:
            int: 次数。
        """
        if isinstance(x, type):
            return sum(1 for i in self if type(i) is x)
        if isinstance(x, MessageComponent):
            return self.__root__.count(x)
        raise TypeError(f"类型不匹配，当前类型：{type(x)}")

    def extend(self, x: Iterable[Union[MessageComponent, str]]):
        """将另一个消息链中的元素添加到消息链末尾。

        Args:
            x: 另一个消息链，也可为消息元素或字符串元素的序列。
        """
        self.__root__.extend(Plain(c) if isinstance(c, str) else c for c in x)

    def append(self, x: Union[MessageComponent, str]):
        """将一个消息元素或字符串元素添加到消息链末尾。

        Args:
            x: 消息元素或字符串元素。
        """
        self.__root__.append(Plain(x) if isinstance(x, str) else x)

    def insert(self, i: int, x: Union[MessageComponent, str]):
        """将一个消息元素或字符串添加到消息链中指定位置。

        Args:
            i: 插入位置。
            x: 消息元素或字符串元素。
        """
        self.__root__.insert(i, Plain(x) if isinstance(x, str) else x)

    def pop(self, i: int = -1) -> MessageComponent:
        """从消息链中移除并返回指定位置的元素。

        Args:
            i: 移除位置。默认为末尾。

        Returns:
            MessageComponent: 移除的元素。
        """
        return self.__root__.pop(i)

    def remove(self, x: Union[MessageComponent, Type[MessageComponent]]):
        """从消息链中移除指定元素或指定类型的一个元素。

        Args:
            x: 指定的元素或元素类型。
        """
        if isinstance(x, type):
            self.pop(self.index(x))
        if isinstance(x, MessageComponent):
            self.__root__.remove(x)

    def exclude(
        self,
        x: Union[MessageComponent, Type[MessageComponent]],
        count: int = -1
    ) -> 'MessageChain':
        """返回移除指定元素或指定类型的元素后剩余的消息链。

        Args:
            x: 指定的元素或元素类型。
            count: 至多移除的数量。默认为全部移除。

        Returns:
            MessageChain: 剩余的消息链。
        """
        def _exclude():
            nonlocal count
            x_is_type = isinstance(x, type)
            for c in self:
                if count > 0 and ((x_is_type and type(c) is x) or c == x):
                    count -= 1
                    continue
                yield c

        return self.__class__(_exclude())

    def reverse(self):
        """将消息链原地翻转。"""
        self.__root__.reverse()

    @classmethod
    def join(cls, *args: Iterable[Union[str, MessageComponent]]):
        return cls(
            Plain(c) if isinstance(c, str) else c
            for c in itertools.chain(*args)
        )

    @property
    def source(self) -> Optional['Source']:
        """获取消息链中的 `Source` 对象。"""
        return self.get_first(Source)

    @property
    def message_id(self) -> int:
        """获取消息链的 message_id，若无法获取，返回 -1。"""
        source = self.source
        return source.id if source else -1


TMessage = Union[MessageChain, Iterable[Union[MessageComponent, str]],
                 MessageComponent, str]
"""可以转化为 MessageChain 的类型。"""


class Source(MessageComponent):
    """源。包含消息的基本信息。"""
    type: str = "Source"
    """消息组件类型。"""
    id: int
    """消息的识别号，用于引用回复（Source 类型永远为 MessageChain 的第一个元素）。"""
    time: datetime
    """消息时间。"""


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

    def __repr__(self):
        return f'Plain({self.text!r})'


class Quote(MessageComponent):
    """引用。"""
    type: str = "Quote"
    """消息组件类型。"""
    id: Optional[int] = None
    """被引用回复的原消息的 message_id。"""
    group_id: Optional[int] = None
    """被引用回复的原消息所接收的群号，当为好友消息时为0。"""
    sender_id: Optional[int] = None
    """被引用回复的原消息的发送者的QQ号。"""
    target_id: Optional[int] = None
    """被引用回复的原消息的接收者者的QQ号（或群号）。"""
    origin: MessageChain
    """被引用回复的原消息的消息链对象。"""
    @validator("origin", always=True, pre=True)
    def origin_formater(cls, v):
        return MessageChain.parse_obj(v)


class At(MessageComponent):
    """At某人。"""
    type: str = "At"
    """消息组件类型。"""
    target: int
    """群员 QQ 号。"""
    display: Optional[str] = None
    """At时显示的文字，发送消息时无效，自动使用群名片。"""
    def __eq__(self, other):
        return isinstance(other, At) and self.target == other.target

    def __str__(self):
        return f"@{self.display or self.target}"

    def as_mirai_code(self) -> str:
        return f"[mirai:at:{self.target}]"


class AtAll(MessageComponent):
    """At全体。"""
    type: str = "AtAll"
    """消息组件类型。"""
    def __str__(self):
        return "@全体成员"

    def as_mirai_code(self) -> str:
        return f"[mirai:atall]"


class Face(MessageComponent):
    """表情。"""
    type: str = "Face"
    """消息组件类型。"""
    face_id: Optional[int] = None
    """QQ 表情编号，可选，优先度高于 name。"""
    name: Optional[str] = None
    """QQ表情名称，可选。"""
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            if isinstance(args[0], str):
                self.name = args[0]
            elif isinstance(args[0], int):
                self.face_id = args[0]
            super().__init__(**kwargs)
        super().__init__(*args, **kwargs)

    def __eq__(self, other):
        return isinstance(other, Face) and \
            (self.face_id == other.face_id or self.name == other.name)

    def __str__(self):
        if self.name:
            return f'[{self.name}]'
        return '[表情]'

    def as_mirai_code(self):
        return f"[mirai:face:{self.face_id}]"


class MarketFace(MessageComponent):
    """商店表情（目前只支持接收）。"""
    type: str = "MarketFace"
    """消息组件类型。"""
    id: int
    """商店表情编号。"""
    name: str
    """商店表情名称。"""


class Image(MessageComponent):
    """图片。"""
    type: str = "Image"
    """消息组件类型。"""
    image_id: Optional[str] = None
    """图片的 image_id，群图片与好友图片格式不同。不为空时将忽略 url 属性。"""
    url: Optional[HttpUrl] = None
    """图片的 URL，发送时可作网络图片的链接；接收时为腾讯图片服务器的链接，可用于图片下载。"""
    path: Union[str, Path, None] = None
    """图片的路径，发送本地图片。"""
    base64: Optional[str] = None
    """图片的 Base64 编码。"""
    def __eq__(self, other):
        return isinstance(
            other, Image
        ) and self.type == other.type and self.uuid == other.uuid

    def __str__(self):
        return '[图片]'

    def as_mirai_code(self) -> str:
        return f"[mirai:image:{self.image_id}]"

    @validator('path')
    def validate_path(cls, path: Union[str, Path, None]):
        """修复 path 参数的行为，使之相对于 YiriMirai 的启动路径。"""
        if path:
            try:
                return str(Path(path).resolve(strict=True))
            except FileNotFoundError:
                raise ValueError(f"无效路径：{path}")
        else:
            return path

    @property
    def uuid(self):
        image_id = self.image_id
        if image_id[0] == '{':  # 群图片
            image_id = image_id[1:37]
        elif image_id[0] == '/':  # 好友图片
            image_id = image_id[1:]
        return image_id

    def as_group_image(self) -> str:
        return f"{{{self.uuid.upper()}}}.jpg"

    def as_friend_image(self) -> str:
        return f"/{self.uuid.lower()}"

    def as_flash_image(self) -> "FlashImage":
        return FlashImage(
            image_id=self.image_id,
            url=self.url,
            path=self.path,
            base64=self.base64
        )

    async def download(
        self,
        filename: Union[str, Path, None] = None,
        directory: Union[str, Path, None] = None,
        determine_type: bool = True
    ):
        """下载图片到本地。

        Args:
            filename: 下载到本地的文件路径。与 `directory` 二选一。
            directory: 下载到本地的文件夹路径。与 `filename` 二选一。
            determine_type: 是否自动根据图片类型确定拓展名，默认为 True。
        """
        if not self.url:
            logger.warning(f'图片 `{self.uuid}` 无 url 参数，下载失败。')
            return

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url)
            response.raise_for_status()
            content = response.content

            if filename:
                path = Path(filename)
                if determine_type:
                    import imghdr
                    path = path.with_suffix(
                        '.' + str(imghdr.what(None, content))
                    )
                path.parent.mkdir(parents=True, exist_ok=True)
            elif directory:
                import imghdr
                path = Path(directory)
                path.mkdir(parents=True, exist_ok=True)
                path = path / f'{self.uuid}.{imghdr.what(None, content)}'
            else:
                raise ValueError("请指定文件路径或文件夹路径！")

            import aiofiles
            async with aiofiles.open(path, 'wb') as f:
                await f.write(content)

            return path

    @classmethod
    async def from_local(
        cls,
        filename: Union[str, Path, None] = None,
        content: Optional[bytes] = None,
    ) -> "Image":
        """从本地文件路径加载图片，以 base64 的形式传递。

        Args:
            filename: 从本地文件路径加载图片，与 `content` 二选一。
            content: 从本地文件内容加载图片，与 `filename` 二选一。

        Returns:
            Image: 图片对象。
        """
        if content:
            pass
        elif filename:
            path = Path(filename)
            import aiofiles
            async with aiofiles.open(path, 'rb') as f:
                content = await f.read()
        else:
            raise ValueError("请指定图片路径或图片内容！")
        import base64
        img = cls(base64=base64.b64encode(content).decode())
        return img

    @classmethod
    def from_unsafe_path(cls, path: Union[str, Path]) -> "Image":
        """从不安全的路径加载图片。

        Args:
            path: 从不安全的路径加载图片。

        Returns:
            Image: 图片对象。
        """
        return cls.construct(path=str(path))


class Xml(MessageComponent):
    """XML。"""
    type: str = "Xml"
    """消息组件类型。"""
    xml: str
    """XML文本。"""


class Json(MessageComponent):
    """JSON。"""
    type: str = "Json"
    """消息组件类型。"""
    json_: str
    """JSON 文本。"""


class App(MessageComponent):
    """应用。"""
    type: str = "App"
    """消息组件类型。"""
    content: str
    """内容。"""
    def as_json(self):
        from json import loads as json_loads
        return json_loads(self.content)

    def __str__(self):
        try:
            json = self.as_json()
            return json.get('prompt', '[应用消息]')
        except:
            return '[应用消息]'

    def as_mirai_code(self) -> str:
        return f'[mirai:app:{serialize(self.content)}]'


POKE_TYPE = {
    "ChuoYiChuo": 1,
    "BiXin": 2,
    "DianZan": 3,
    "XinSui": 4,
    "LiuLiuLiu": 5,
    "FangDaZhao": 6,
    "BaoBeiQiu": 126,
    "Rose": 126,
    "ZhaoHuanShu": 126,
    "RangNiPi": 126,
    "JeiYin": 126,
    "ShouLei": 126,
    "GouYin": 126,
    "ZhuaYiXia": 126,
    "SuiPing": 126,
    "QiaoMen": 126,
}
POKE_ID = {
    "ChuoYiChuo": -1,
    "BiXin": -1,
    "DianZan": -1,
    "XinSui": -1,
    "LiuLiuLiu": -1,
    "FangDaZhao": -1,
    "BaoBeiQiu": 2011,
    "Rose": 2007,
    "ZhaoHuanShu": 2006,
    "RangNiPi": 2009,
    "JeiYin": 2005,
    "ShouLei": 2004,
    "GouYin": 2003,
    "ZhuaYiXia": 2001,
    "SuiPing": 2002,
    "QiaoMen": 2002,
}
POKE_NAME = {
    "ChuoYiChuo": '戳一戳',
    "BiXin": '比心',
    "DianZan": '点赞',
    "XinSui": '心碎',
    "LiuLiuLiu": '666',
    "FangDaZhao": '放大招',
    "BaoBeiQiu": '宝贝球',
    "Rose": '玫瑰花',
    "ZhaoHuanShu": '召唤术',
    "RangNiPi": '让你皮',
    "JeiYin": '结印',
    "ShouLei": '手雷',
    "GouYin": '勾引',
    "ZhuaYiXia": '抓一下',
    "SuiPing": '碎屏',
    "QiaoMen": '敲门',
}


class PokeNames(str, Enum):
    """戳一戳名称。"""
    ChuoYiChuo = "ChuoYiChuo"
    BiXin = "BiXin"
    DianZan = "DianZan"
    XinSui = "XinSui"
    LiuLiuLiu = "LiuLiuLiu"
    FangDaZhao = "FangDaZhao"
    BaoBeiQiu = "BaoBeiQiu"
    Rose = "Rose"
    ZhaoHuanShu = "ZhaoHuanShu"
    RangNiPi = "RangNiPi"
    JeiYin = "JeiYin"
    ShouLei = "ShouLei"
    GouYin = "GouYin"
    ZhuaYiXia = "ZhuaYiXia"
    SuiPing = "SuiPing"
    QiaoMen = "QiaoMen"

    def as_component(self) -> 'Poke':
        return Poke(name=self.value)


class Poke(MessageComponent):
    """戳一戳。"""
    type: str = "Poke"
    """消息组件类型。"""
    name: PokeNames
    """名称。"""
    @property
    def poke_type(self):
        return POKE_TYPE[self.name]

    @property
    def poke_id(self):
        return POKE_ID[self.name]

    def __str__(self):
        return f'[{POKE_NAME[self.name]}]'

    def as_mirai_code(self) -> str:
        return f'[mirai:poke:{self.name},{self.poke_type},{self.poke_id}]'


class Unknown(MessageComponent):
    """未知。"""
    type: str = "Unknown"
    """消息组件类型。"""
    text: str
    """文本。"""


class FlashImage(Image):
    """闪照。"""
    type: str = "FlashImage"
    """消息组件类型。"""
    image_id: Optional[str] = None
    """图片的 image_id，群图片与好友图片格式不同。不为空时将忽略 url 属性。"""
    url: Optional[HttpUrl] = None
    """图片的 URL，发送时可作网络图片的链接；接收时为腾讯图片服务器的链接，可用于图片下载。"""
    path: Optional[str] = None
    """图片的路径，发送本地图片，路径相对于 `plugins/MiraiAPIHTTP/images`。"""
    base64: Optional[str] = None
    """图片的 Base64 编码。"""
    def __str__(self):
        return '[闪照]'

    def as_mirai_code(self) -> str:
        return f"[mirai:flash:{self.image_id}]"

    def as_image(self) -> Image:
        return Image(self.image_id, self.url)


class Voice(MessageComponent):
    """语音。"""
    type: str = "Voice"
    """消息组件类型。"""
    voice_id: Optional[str] = None
    """语音的 voice_id，不为空时将忽略 url 属性。"""
    url: Optional[str] = None
    """语音的 URL，发送时可作网络语音的链接；接收时为腾讯语音服务器的链接，可用于语音下载。"""
    path: Optional[str] = None
    """语音的路径，发送本地语音。"""
    base64: Optional[str] = None
    """语音的 Base64 编码。"""
    length: Optional[int] = None
    """语音的长度，单位为秒。"""
    @validator('path')
    def validate_path(cls, path: Optional[str]):
        """修复 path 参数的行为，使之相对于 YiriMirai 的启动路径。"""
        if path:
            try:
                return str(Path(path).resolve(strict=True))
            except FileNotFoundError:
                raise ValueError(f"无效路径：{path}")
        else:
            return path

    def __str__(self):
        return '[语音]'

    async def download(
        self,
        filename: Union[str, Path, None] = None,
        directory: Union[str, Path, None] = None
    ):
        """下载语音到本地。

        语音采用 silk v3 格式，silk 格式的编码解码请使用 [graiax-silkcoder](https://pypi.org/project/graiax-silkcoder/)。

        Args:
            filename: 下载到本地的文件路径。与 `directory` 二选一。
            directory: 下载到本地的文件夹路径。与 `filename` 二选一。
        """
        if not self.url:
            logger.warning(f'语音 `{self.voice_id}` 无 url 参数，下载失败。')
            return

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url)
            response.raise_for_status()
            content = response.content

            if filename:
                path = Path(filename)
                path.parent.mkdir(parents=True, exist_ok=True)
            elif directory:
                path = Path(directory)
                path.mkdir(parents=True, exist_ok=True)
                path = path / f'{self.voice_id}.silk'
            else:
                raise ValueError("请指定文件路径或文件夹路径！")

            import aiofiles
            async with aiofiles.open(path, 'wb') as f:
                await f.write(content)

    @classmethod
    async def from_local(
        cls,
        filename: Union[str, Path, None] = None,
        content: Optional[bytes] = None,
    ) -> "Voice":
        """从本地文件路径加载语音，以 base64 的形式传递。

        Args:
            filename: 从本地文件路径加载语音，与 `content` 二选一。
            content: 从本地文件内容加载语音，与 `filename` 二选一。
        """
        if content:
            pass
        if filename:
            path = Path(filename)
            import aiofiles
            async with aiofiles.open(path, 'rb') as f:
                content = await f.read()
        else:
            raise ValueError("请指定语音路径或语音内容！")
        import base64
        img = cls(base64=base64.b64encode(content).decode())
        return img


class Dice(MessageComponent):
    """骰子。"""
    type: str = "Dice"
    """消息组件类型。"""
    value: int
    """点数。"""
    def __str__(self):
        return f'[骰子{self.value}]'

    def as_mirai_code(self) -> str:
        return f'[mirai:dice:{self.value}]'


class MusicShareKind(str, Enum):
    """音乐分享的来源。"""
    NeteaseCloudMusic = "NeteaseCloudMusic"
    QQMusic = "QQMusic"
    MiguMusic = "MiguMusic"
    KugouMusic = "KugouMusic"
    KuwoMusic = "KuwoMusic"


class MusicShare(MessageComponent):
    """音乐分享。"""
    type: str = "MusicShare"
    """消息组件类型。"""
    kind: MusicShareKind
    """音乐分享的来源。"""
    title: str
    """标题。"""
    summary: str
    """歌手。"""
    jump_url: HttpUrl
    """跳转路径。"""
    picture_url: HttpUrl
    """封面路径。"""
    music_url: HttpUrl
    """音源路径。"""
    brief: str = ""
    """在消息列表中显示的内容。"""
    def __str__(self):
        return self.brief


class ForwardMessageNode(MiraiBaseModel):
    """合并转发中的一条消息。"""
    sender_id: Optional[int] = None
    """发送人QQ号。"""
    sender_name: Optional[str] = None
    """显示名称。"""
    message_chain: Optional[MessageChain] = None
    """消息内容。"""
    message_id: Optional[int] = None
    """消息的 message_id，可以只使用此属性，从缓存中读取消息内容。"""
    time: Optional[datetime] = None
    """发送时间。"""
    @validator('message_chain', check_fields=False)
    def _validate_message_chain(cls, value: Union[MessageChain, list]):
        if isinstance(value, list):
            return MessageChain.parse_obj(value)
        return value

    @classmethod
    def create(
        cls, sender: Union[Friend, GroupMember], message: MessageChain
    ) -> 'ForwardMessageNode':
        """从消息链生成转发消息。

        Args:
            sender: 发送人。
            message: 消息内容。

        Returns:
            ForwardMessageNode: 生成的一条消息。
        """
        return ForwardMessageNode(
            sender_id=sender.id,
            sender_name=sender.get_name(),
            message_chain=message
        )


class Forward(MessageComponent):
    """合并转发。"""
    type: str = "Forward"
    """消息组件类型。"""
    node_list: List[ForwardMessageNode]
    """转发消息节点列表。"""
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            self.node_list = args[0]
            super().__init__(**kwargs)
        super().__init__(*args, **kwargs)

    def __str__(self):
        return '[聊天记录]'


class File(MessageComponent):
    """文件。"""
    type: str = "File"
    """消息组件类型。"""
    id: str
    """文件识别 ID。"""
    name: str
    """文件名称。"""
    size: int
    """文件大小。"""
    def __str__(self):
        return f'[文件]{self.name}'


class MiraiCode(MessageComponent):
    """Mirai 码。"""
    type: str = "MiraiCode"
    """消息组件类型。"""
    code: str
    """Mirai 码。"""
    def __str__(self):
        return serialize(self.code)

    def __repr__(self):
        return f'MiraiCode({self.code!r})'


__all__ = [
    'App',
    'At',
    'AtAll',
    'Dice',
    'Face',
    'File',
    'FlashImage',
    'Forward',
    'ForwardMessageNode',
    'Image',
    'Json',
    'MarketFace',
    'MessageChain',
    'MessageComponent',
    'MusicShareKind',
    'MusicShare',
    'Plain',
    'PokeNames',
    'Poke',
    'Quote',
    'Source',
    'Unknown',
    'Voice',
    'Xml',
    'serialize',
    'deserialize',
    'TMessage',
]
