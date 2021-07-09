# -*- coding: utf-8 -*-
"""
此模块提供消息链相关。
"""
import logging
import re
from datetime import datetime
from json import loads as json_loads
from typing import List, Optional

from mirai.models.base import MiraiBaseModel, MiraiIndexedModel
from mirai.utils import KMP
from pydantic import Field, HttpUrl, validator

logger = logging.getLogger(__name__)


def serialize(s: str) -> str:
    """mirai 码转义。

    `s: str` 待转义的字符串。
    """
    return re.sub(r'[\[\]:,\\\n\r]', lambda match: '\\' + match.group(0), s)


def deserialize(s: str) -> str:
    """mirai 码去转义。

    `s: str` 待去转义的字符串。
    """
    return re.sub(r'\\([\[\]:,\\nr])', lambda match: match.group(1), s)


class MessageComponent(MiraiIndexedModel):
    """消息组件。"""
    type: str

    def __str__(self):
        return ''


class MessageChain(MiraiBaseModel):
    """消息链。

    一个构造消息链的例子：
    ```py
    message_chain = MessageChain([
        AtAll(),
        Plain("Hello World!"),
    ])
    ```

    在调用 API 时，参数中需要 MessageChain 的，也可以使用`List[MessageComponent]`代替。
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

    可以使用`==`运算符比较两个消息链是否相同。
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

    可以使用`in`运算检查消息链中：
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

    也可以使用`>=`和`<=`运算符：
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

    以`类型: 数量`为索引，获取前至多多少个该类型的消息组件。
    ```py
    plain_list_first = message_chain[Plain: 1]
    '[Plain("Hello World!")]'
    ```
    """
    __root__: List[MessageComponent]

    @staticmethod
    def _parse_message_chain(msg_chain: list):
        result = []
        for msg in msg_chain:
            if isinstance(msg, dict):
                result.append(MessageComponent.parse_obj(msg))
            elif isinstance(msg, MessageComponent):
                result.append(msg)
            else:
                raise TypeError(
                    f"消息链中元素需为 dict 或 MessageComponent，当前类型：{type(msg)}"
                )
        return result

    @validator('__root__', always=True, pre=True)
    def _parse_component(cls, msg_chain):
        if not msg_chain:
            msg_chain = []
        return cls._parse_message_chain(msg_chain)

    @classmethod
    def parse_obj(cls, msg_chain: list):
        """通过列表形式的消息链，构造对应的`MessageChain`对象。

        `msg_chain: list` 列表形式的消息链。
        """
        result = cls._parse_message_chain(msg_chain)
        return cls(__root__=result)

    def __init__(self, __root__: List[MessageComponent] = None):
        super().__init__(__root__=__root__)

    def __str__(self):
        return "".join((str(component) for component in self.__root__))

    def __iter__(self):
        yield from self.__root__

    def __getitem__(self, index):
        # 正常索引
        if isinstance(index, int):
            return self.__root__[index]
        # 索引对象为 MessageComponent 类，返回所有对应 component
        elif isinstance(index, type):
            return [
                component for component in self if type(component) == index
            ]
        # 索引对象为 MessageComponent 和 int 构成的 slice， 返回指定数量的 component
        elif isinstance(index, slice):
            components = (
                component for component in self
                if type(component) == index.start
            )
            return [
                component
                for component, _ in zip(components, range(index.stop))
            ]

    def __contains__(self, sub) -> bool:
        if isinstance(sub, type):  # 检测消息链中是否有某种类型的对象
            for i in self:
                if type(i) == sub:
                    return True
            else:
                return False
        elif isinstance(sub, MessageComponent):  # 检查消息链中是否有某个组件
            for i in self:
                if i == sub:
                    return True
            else:
                return False
        elif isinstance(sub, MessageChain):  # 检查消息链中是否有某个子消息链
            return bool(KMP(self, sub))
        elif isinstance(sub, str):  # 检查消息中有无指定字符串子串
            return sub in deserialize(str(self))

    def __ge__(self, other):
        return other in self

    def __len__(self) -> int:
        return len(self.__root__)

    @property
    def source(self) -> 'Source':
        """获取消息链中的`Source`对象。"""
        return self[Source:1][0]


class Source(MessageComponent):
    """源。包含消息的基本信息。"""
    type: str = "Source"
    id: int
    time: datetime


class Plain(MessageComponent):
    """纯文本。"""
    type: str = "Plain"
    text: str

    def __init__(self, text: str = '', **_):
        if len(text) > 128:
            logger.warn(f"Plain 文本过长。当前长度： {len(text)}。")
        super().__init__(text=text)

    def __str__(self):
        return serialize(self.text)


class Quote(MessageComponent):
    """引用。"""
    type: str = "Quote"
    id: Optional[int]
    group_id: Optional[int] = Field(alias='groupId')
    sender_id: Optional[int] = Field(alias='senderId')
    target_id: Optional[int] = Field(alias='targetId')
    origin: MessageChain

    @validator("origin", always=True, pre=True)
    @classmethod
    def origin_formater(cls, v):
        return MessageChain.parse_obj(v)

    def __init__(
        self,
        id: Optional[int] = None,
        group_id: Optional[int] = None,
        sender_id: Optional[int] = None,
        target_id: Optional[int] = None,
        origin: MessageChain = None,
        groupId: Optional[int] = None,
        senderId: Optional[int] = None,
        targetId: Optional[int] = None,
        **_
    ):
        super().__init__(
            id=id,
            groupId=group_id or groupId,
            senderId=sender_id or senderId,
            targetId=target_id or targetId,
            origin=origin
        )


class At(MessageComponent):
    """At某人。"""
    type: str = "At"
    target: int
    display: Optional[str] = None

    def __init__(self, target: int, **_):
        super().__init__(target=target)

    def __eq__(self, other):
        return isinstance(other, At) and self.target == other.target

    def __str__(self):
        return f"[mirai:at:{self.target}]"


class AtAll(MessageComponent):
    """At全体。"""
    type: str = "AtAll"

    def __str__(self):
        return f"[mirai:atall]"


class Face(MessageComponent):
    """表情。"""
    type: str = "Face"
    face_id: int = Field(..., alias='faceId')
    name: Optional[str]

    def __init__(
        self,
        face_id: Optional[int] = None,
        name: Optional[str] = None,
        faceId: Optional[int] = None,
        **_
    ):
        super().__init__(faceId=face_id or faceId, name=name)

    def __eq__(self, other):
        return isinstance(other, Face) and self.face_id == other.face_id

    def __str__(self):
        return f"[mirai:face:{self.face_id}]"


class Image(MessageComponent):
    """图片。"""
    type: str = "Image"
    image_id: Optional[str] = Field(alias='imageId')
    url: Optional[HttpUrl] = None

    def __init__(
        self,
        image_id: Optional[str] = None,
        url: Optional[str] = None,
        imageId: Optional[str] = None,
        **_
    ):
        super().__init__(imageId=image_id or imageId, url=url)

    def __eq__(self, other):
        return isinstance(
            other, Image
        ) and self.type == other.type and self.uuid == other.uuid

    def __str__(self):
        return f"[mirai:image:{self.image_id}]"

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
        return FlashImage(self.image_id, self.url)

    # @staticmethod
    # async def fromRemote(url, **extra) -> BytesImage:
    #     async with ClientSession() as session:
    #         async with session.get(url, **extra) as response:
    #             return BytesImage(await response.read())

    # @staticmethod
    # def fromFileSystem(path: Union[Path, str]) -> LocalImage:
    #     return LocalImage(path)

    # async def toBytes(self, chunk_size=256) -> BytesIO:
    #     async with ClientSession() as session:
    #         async with session.get(self.url) as response:
    #             result = BytesIO()
    #             while True:
    #                 chunk = await response.content.read(chunk_size)
    #                 if not chunk:
    #                     break
    #                 result.write(chunk)
    #         return result

    # @staticmethod
    # def fromBytes(data) -> BytesImage:
    #     return BytesImage(data)

    # @staticmethod
    # def fromBase64(base64_str) -> Base64Image:
    #     return Base64Image(base64_str)

    # @staticmethod
    # def fromIO(IO) -> IOImage:
    #     return IOImage(IO)


class Xml(MessageComponent):
    """XML。"""
    type: str = "Xml"
    xml: str

    def __init__(self, xml: str, **_):
        super().__init__(xml=xml)


class Json(MessageComponent):
    """JSON。"""
    type: str = "Json"
    json_: dict = Field(..., alias='json')

    def __init__(self, json: dict):
        super().__init__(json=json)


class App(MessageComponent):
    """应用。"""
    type: str = "App"
    content: str

    def __init__(self, content: str, **_):
        super().__init__(content=content)

    def as_json(self):
        return json_loads(self.content)

    def __str__(self):
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


class Poke(MessageComponent):
    """戳一戳。"""
    type: str = "Poke"
    name: str

    def __init__(self, name: str, **_):
        super().__init__(name=name)

    @property
    def poke_type(self):
        return POKE_TYPE[self.name]

    @property
    def poke_id(self):
        return POKE_ID[self.name]

    def __str__(self):
        return f'[mirai:poke:{self.name},{self.poke_type},{self.poke_id}]'


class Unknown(MessageComponent):
    """未知。"""
    type: str = "Unknown"
    text: str


class FlashImage(Image):
    """闪照。"""
    type: str = "FlashImage"

    def __init__(self, imageId, url=None, **_):
        super().__init__(imageId=imageId, url=url)

    def __str__(self):
        return f"[mirai:flash:{self.image_id}]"

    def as_image(self) -> Image:
        return Image(self.image_id, self.url)


class Voice(MessageComponent):
    """语音。"""
    type: str = "Voice"
    voice_id: Optional[str] = Field(alias="voiceId")
    url: Optional[str]
    path: Optional[str]
    base64: Optional[str]


class Dice(MessageComponent):
    """骰子。"""
    type: str = "Dice"
    value: int

    def __init__(self, value: int, **_):
        super().__init__(value=value)

    def __str__(self):
        return f'[mirai:dice:{self.value}]'


class MusicShare(MessageComponent):
    """音乐分享。"""
    type: str = "MusicShare"
    kind: str
    title: str
    summary: str
    jump_url: HttpUrl = Field(..., alias='jumpUrl')
    picture_url: HttpUrl = Field(..., alias='pictureUrl')
    music_url: HttpUrl = Field(..., alias='musicUrl')
    brief: str


class ForwardMessageNode(MiraiBaseModel):
    """合并转发中的一条消息。"""
    sender_id: int = Field(..., alias='senderId')
    time: datetime
    sender_name: str = Field(..., alias='senderName')
    source_id: Optional[int] = Field(alias='sourceId')
    message_chain: MessageChain = Field(..., alias='messageChain')


class Forward(MessageComponent):
    """合并转发。"""
    type: str = "Forward"
    node_list: List[ForwardMessageNode] = Field(..., alias='nodeList')


class File(MessageComponent):
    """文件。"""
    type: str = "File"
    id: str
    name: str
    size: int


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
    'MessageChain',
    'MessageComponent',
    'MusicShare',
    'Plain',
    'Poke',
    'Quote',
    'Source',
    'Unknown',
    'Voice',
    'Xml',
    'serialize',
    'deserialize',
]
