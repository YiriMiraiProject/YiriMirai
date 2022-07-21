"""此模块提供消息链相关。"""
import itertools
import logging
from datetime import datetime
from typing import (
    Iterable, List, Optional, Tuple, Type, TypeVar, Union, cast, overload
)

from pydantic import validator

from mirai.models.base import MiraiBaseModel
from mirai.models.message.base import MessageComponent, Plain, deserialize

logger = logging.getLogger(__name__)

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

    消息链对这些操作进行了拓展。在传入元素的地方，一般都可以传入元素的类型。
    """

    class Source(MessageComponent):
        """源。包含消息的基本信息。"""
        type: str = "Source"
        """消息组件类型。"""
        id: int
        """消息的识别号，用于引用回复（Source 类型永远为 MessageChain 的第一个元素）。"""
        time: datetime
        """消息时间。"""

    class Quote(MessageComponent):
        """引用。"""
        type: str = "Quote"
        """消息组件类型。"""
        id: int
        """被引用回复的原消息的 message_id。"""
        group_id: int
        """被引用回复的原消息所接收的群号，当为好友消息时为0。"""
        sender_id: int
        """被引用回复的原消息的发送者的QQ号。"""
        target_id: int
        """被引用回复的原消息的接收者者的QQ号（或群号）。"""
        origin: 'MessageChain'
        """被引用回复的原消息的消息链对象。"""

    __root__: List[MessageComponent]
    _source: Optional[Source]
    _quote: Optional[Quote]

    @staticmethod
    def _parse_message_chain(msg_chain: Iterable):
        result = []
        for msg in msg_chain:
            if isinstance(msg, dict):
                result.append(MessageComponent.parse_obj(msg))
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
        return MessageChain._parse_message_chain(msg_chain)

    @classmethod
    def parse_obj(cls, obj: Iterable):
        """通过列表形式的消息链，构造对应的 `MessageChain` 对象。

        Args:
            msg_chain: 列表形式的消息链。
        """
        result = MessageChain._parse_message_chain(obj)
        return cls(__root__=result)

    def __init__(
        self,
        __root__: Iterable[Union[MessageComponent, str]],
        source: Optional[Source] = None,
        quote: Optional[Quote] = None
    ):
        super().__init__(__root__=__root__)
        chain = self.__root__

        if chain and isinstance(chain[0], MessageChain.Source):
            self._source, chain = chain[0], chain[1:]
        else:
            self._source = source

        if chain and isinstance(chain[0], MessageChain.Quote):
            self._quote, chain = chain[0], chain[1:]
        else:
            self._quote = quote

        self.__root__ = chain

    @property
    def source(self):
        return self._source

    @property
    def quote(self):
        return self._quote

    def dict(self, **kwargs):  # type: ignore
        """转为字典。"""
        result = [component.dict(**kwargs) for component in self.__root__]
        if self.source:
            result.insert(0, self.source.dict(**kwargs))
        return result

    def __str__(self):
        return "".join(str(component) for component in self)

    def as_mirai_code(self) -> str:
        """将消息链转换为 mirai 码字符串。

        该方法会自动转换消息链中的元素。

        Returns:
            mirai 码字符串。
        """
        return "".join(component.as_mirai_code() for component in self)

    def __repr_str__(self, _):
        s = repr(self.__root__)
        if self.source:
            s += f', source={self.source!r}'
        if self.quote:
            s += f', quote={self.quote!r}'
        return s

    def __iter__(self):  # type: ignore
        yield from self.__root__

    @overload
    def get(self, index: int) -> MessageComponent:
        ...

    @overload
    def get(self, index: slice) -> List[MessageComponent]:
        ...

    @overload
    def get(self,
            index: Type[TMessageComponent],
            count: Optional[int] = None) -> List[TMessageComponent]:
        ...

    @overload
    def get(
        self,
        index: Tuple[Type[TMessageComponent], int],
        count: Optional[int] = None
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
        # 正常索引、切片索引
        if isinstance(index, (int, slice)):
            return self.__root__[index]
        # 索引对象为 MessageComponent 和 int 构成的 tuple，返回指定数量的 component
        if isinstance(index, tuple):
            if count:
                return self.get(
                    index[0], count if count < index[1] else index[1]
                )
            return self.get(*index)

        # 索引对象为 MessageComponent 类，返回所有对应 component
        if isinstance(index, type):
            # 特殊处理 Source 和 Quote
            if index is MessageChain.Source:
                return cast(index, [self.source] if self.source else [])
            elif index is MessageChain.Quote:
                return cast(index, [self.quote] if self.quote else [])

            components = (
                component for component in self if type(component) is index
            )
            if count:
                return [c for c, _ in zip(components, range(count))]
            return list(components)

        raise TypeError(f"消息链索引需为 int 或 MessageComponent，当前类型：{type(index)}")

    def get_first(self,
                  t: Type[TMessageComponent]) -> Optional[TMessageComponent]:
        """获取消息链中第一个符合类型的消息组件。"""
        return next(
            (component for component in self if isinstance(component, t)), None
        )

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

    def __reversed__(self) -> "MessageChain":
        return self.__class__(
            reversed(
                [
                    Plain(''.join(reversed(c.text)))
                    if isinstance(c, Plain) else c for c in self.__root__
                ]
            )
        )

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
            # 特殊处理 Source 和 Quote
            if sub is MessageChain.Source:
                return bool(self.source)
            elif sub is MessageChain.Quote:
                return bool(self.quote)
            return any(type(c) is sub for c in self)
        if isinstance(sub, MessageComponent):  # 检查消息链中是否有某个组件
            return sub in self.__root__
        if isinstance(sub, MessageChain):  # 检查消息链中是否有某个子消息链
            return list(sub) in self.__root__
        if isinstance(sub, str):  # 检查消息中有无指定字符串子串
            return sub in deserialize(str(self))
        raise TypeError(f"类型不匹配，当前类型：{type(sub)}")

    def __contains__(self, sub) -> bool:
        return self.has(sub)

    def __len__(self) -> int:
        return len(self.__root__)

    def __add__(
        self, other: Union['MessageChain', MessageComponent, str,
                           Iterable[Union[MessageComponent, str]]]
    ) -> 'MessageChain':
        if isinstance(other, MessageChain):
            return self.__class__(self.__root__ + other.__root__)
        if isinstance(other, str):
            return self.__class__(self.__root__ + [Plain(other)])
        if isinstance(other, MessageComponent):
            return self.__class__(self.__root__ + [other])
        if isinstance(other, list):
            return self + MessageChain(other)
        return NotImplemented

    def __radd__(
        self, other: Union[MessageComponent, str,
                           Iterable[Union[MessageComponent, str]]]
    ) -> 'MessageChain':
        if isinstance(other, MessageComponent):
            return self.__class__([other] + self.__root__)
        if isinstance(other, str):
            return self.__class__(
                [cast(MessageComponent, Plain(other))] + self.__root__
            )
        if isinstance(other, list):
            return MessageChain(other) + self
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (MessageChain, list)):
            return all(a == b for a, b in zip(self, other))
        return NotImplemented

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

    @classmethod
    def join(cls, *args: Iterable[Union[str, MessageComponent]]):
        return cls(
            Plain(c) if isinstance(c, str) else c
            for c in itertools.chain(*args)
        )

    @property
    def message_id(self) -> int:
        """获取消息链的 message_id，若无法获取，返回 -1。"""
        source = self.source
        return source.id if source else -1


MessageChain.Quote.update_forward_refs()
