"""此模块提供消息元素相关。"""
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

from pydantic import HttpUrl, validator

from mirai.models.base import MiraiBaseModel
from mirai.models.entities import Friend, GroupMember
from mirai.models.message.base import MessageComponent, serialize
from mirai.models.message.chain import MessageChain

logger = logging.getLogger(__name__)


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
        return "[mirai:atall]"


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
        return f'[{self.name}]' if self.name else '[表情]'

    def as_mirai_code(self):
        return f"[mirai:face:{self.face_id}]"


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

    def __str__(self) -> str:
        return '[图片]'

    def as_mirai_code(self) -> str:
        return f"[mirai:image:{self.image_id}]"

    @validator('path')
    def validate_path(cls, path: Union[str, Path, None]):
        """修复 path 参数的行为，使之相对于 YiriMirai 的启动路径。"""
        if not path:
            return path
        try:
            return str(Path(path).resolve(strict=True))
        except FileNotFoundError as e:
            raise ValueError(f"无效路径：{path}") from e

    @property
    def uuid(self):
        if not self.image_id:
            return None
        image_id = self.image_id
        if image_id[0] == '{':  # 群图片
            image_id = image_id[1:37]
        elif image_id[0] == '/':  # 好友图片
            image_id = image_id[1:]
        return image_id

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
                        f'.{str(imghdr.what(None, content))}'
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
        from json import JSONDecodeError
        try:
            json = self.as_json()
            return json.get('prompt', '[应用消息]')
        except (JSONDecodeError, AttributeError):
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
        if not path:
            return path
        try:
            return str(Path(path).resolve(strict=True))
        except FileNotFoundError as e:
            raise ValueError(f"无效路径：{path}") from e

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
    def __init__(
        self,
        sender_id: int,
        time: datetime,
        message: Union[int, MessageChain],
        sender_name: Optional[str] = None
    ):
        if isinstance(message, int):
            message_chain, message_id = None, message
        else:
            message_chain, message_id = message, None
        super().__init__(
            sender_id=sender_id,
            sender_name=sender_name,
            message_chain=message_chain,
            message_id=message_id,
            time=time
        )

    @validator('message_chain')
    def _validate_message_chain(cls, value: Union[MessageChain, list]):
        return MessageChain.parse_obj(value
                                      ) if isinstance(value, list) else value

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
        time = message.source.time if message.source else datetime.now()
        return ForwardMessageNode(sender.id, time, message, sender.get_name())


class Forward(MessageComponent):
    """合并转发。"""
    type: str = "Forward"
    """消息组件类型。"""
    node_list: List[ForwardMessageNode]
    """转发消息节点列表。"""
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], list):
            node_list = args[0]
        else:
            node_list = [*args]
        super().__init__(node_list=node_list, **kwargs)

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

    def __repr_str__(self, _):
        return repr(self.code)
