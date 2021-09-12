# -*- coding: utf-8 -*-
"""
此模块提供 API 调用与返回数据解析相关。
"""
import logging
from datetime import datetime
from enum import Enum, Flag
from pathlib import Path
from typing import (
    TYPE_CHECKING, Any, Generic, Iterable, List, Optional, Type, TypeVar,
    Union, cast
)

if TYPE_CHECKING:
    from typing_extensions import Literal
else:
    try:
        from typing import Literal
    except ImportError:
        from typing_extensions import Literal

from pydantic import validator

from mirai.api_provider import ApiProvider, Method
from mirai.models.base import (
    MiraiBaseModel, MiraiIndexedMetaclass, MiraiIndexedModel
)
from mirai.models.entities import (
    Friend, Group, GroupConfigModel, GroupMember, MemberInfoModel
)
from mirai.models.events import (
    FriendMessage, GroupMessage, OtherClientMessage, RequestEvent,
    StrangerMessage, TempMessage
)
from mirai.models.message import (
    Image, MessageChain, MessageComponent, TMessage, Voice
)
from mirai.utils import async_

logger = logging.getLogger(__name__)


class Response(MiraiBaseModel):
    """响应对象。"""
    code: int
    """状态码。"""
    msg: str
    """消息。"""
    data: Optional[Any] = None
    """返回数据。"""
    def __getattr__(self, item):
        return getattr(self.data, item)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, item):
        return self.data[item]


class AboutResponse(Response):
    """插件信息。"""
    data: dict


class SessionInfoResponse(Response):
    """机器人信息。"""
    data: 'SessionInfoResponse.Data'

    class Data(MiraiBaseModel):
        session_key: str = 'SINGLE_SESSION'
        """session_key。"""
        qq: Friend
        """机器人信息。"""

    @property
    def qq(self):
        return self.data.qq.id

    @property
    def nickname(self):
        return self.data.qq.nickname


SessionInfoResponse.update_forward_refs()


class MessageFromIdResponse(Response):
    '''通过 message_id 获取的消息。'''
    data: Union[FriendMessage, GroupMessage, TempMessage, StrangerMessage,
                OtherClientMessage]
    """获取的消息，以消息事件的形式返回。"""


class FriendListResponse(Response):
    """好友列表。"""
    data: List[Friend]
    """好友列表。"""
    def __iter__(self):
        yield from self.data


class GroupListResponse(Response):
    """群组列表。"""
    data: List[Group]
    """群组列表。"""
    def __iter__(self):
        yield from self.data


class MemberListResponse(Response):
    """群成员列表。"""
    data: List[GroupMember]
    """群成员列表。"""
    def __iter__(self):
        yield from self.data


class Sex(str, Enum):
    """性别。"""
    Unknown = 'UNKNOWN'
    Male = 'MALE'
    Female = 'FEMALE'

    def __repr__(self) -> str:
        return repr(self.value)


class ProfileResponse(MiraiBaseModel):
    """好友资料。"""
    nickname: str
    """昵称。"""
    email: str
    """邮箱地址。"""
    age: int
    """年龄。"""
    level: int
    """QQ 等级。"""
    sign: str
    """个性签名。"""
    sex: Sex
    """性别。"""


class MessageResponse(Response):
    """发送消息的响应。"""
    message_id: int
    """消息的 message_id。"""


class DownloadInfo(MiraiBaseModel):
    """文件的下载信息。"""
    sha1: str
    """文件的 SHA1。"""
    md5: str
    """文件的 MD5。"""
    url: str
    """文件的下载地址。"""
    downloadTimes: Optional[int]
    """文件被下载过的次数。"""
    uploaderId: Optional[int]
    """上传者的 QQ 号。"""
    uploadTime: Optional[datetime]
    """上传时间。"""
    lastModifyTime: Optional[datetime]
    """最后修改时间。"""


class FileProperties(MiraiBaseModel):
    """文件对象。"""
    name: str
    """文件名。"""
    id: Optional[str]
    """文件 ID。"""
    path: str
    """所在目录路径。"""
    parent: Optional['FileProperties'] = None
    """父文件对象，递归类型。None 为存在根目录。"""
    contact: Union[Group, Friend]
    """群信息或好友信息。"""
    is_file: bool
    """是否是文件。"""
    is_directory: bool
    """是否是文件夹。"""
    download_info: Optional[DownloadInfo] = None
    """文件的下载信息。"""


FileProperties.update_forward_refs()  # 支持 model 引用自己的类型


class FileListResponse(Response):
    """文件列表。"""
    data: List[FileProperties]

    def __iter__(self):
        yield from self.data

    def files(self):
        """返回文件列表。"""
        return [item for item in self if item.is_file]

    def directories(self):
        """返回文件夹列表。"""
        return [item for item in self if item.is_directory]


class FileInfoResponse(Response):
    """文件信息。"""
    data: FileProperties


class FileMkdirResponse(Response):
    """创建文件夹的响应。"""
    data: FileProperties


class ApiMetaclass(MiraiIndexedMetaclass):
    """API 模型的元类。"""
    __apimodel__ = None

    def __new__(cls, name, bases, attrs, **kwargs):
        new_cls = super().__new__(cls, name, bases, attrs, **kwargs)

        if name == 'ApiModel':
            cls.__apimodel__ = new_cls
            new_cls.__indexes__ = {}
            return new_cls

        if not cls.__apimodel__:  # ApiBaseModel 构造时，ApiModel 还未构造
            return new_cls

        for base in bases:
            if issubclass(base, cls.__apimodel__):
                info = new_cls.Info
                if hasattr(info, 'name') and info.name:
                    base.__indexes__[info.name] = new_cls
                if hasattr(info, 'alias') and info.alias:
                    base.__indexes__[info.alias] = new_cls

                # 获取 API 参数名
                if hasattr(new_cls, '__fields__'):
                    info.parameter_names = list(new_cls.__fields__)
                else:
                    info.parameter_names = []
                break

        return new_cls


class ApiBaseModel(MiraiIndexedModel, metaclass=ApiMetaclass):
    """API 模型基类。

    直接继承此类，不会被 ApiMetaclass 索引，也不会引起 metaclass 冲突。
    用于实现 API 类型之间的方法复用。
    """


TModel = TypeVar('TModel', bound=MiraiBaseModel)


class ApiModel(ApiBaseModel):
    """API 模型。"""
    class Info():
        """API 的信息。"""
        name = ""
        alias = ""
        response_type: Type[MiraiBaseModel] = Response
        parameter_names: List[str] = []

    def __init__(self, *args, **kwargs):
        # 解析参数列表，将位置参数转化为具名参数
        parameter_names = self.Info.parameter_names
        if len(args) > len(parameter_names):
            raise TypeError(
                f'`{self.Info.alias}`需要{len(parameter_names)}个参数，' +
                '但传入了{len(args)}个。'
            )
        for name, value in zip(parameter_names, args):
            if name in kwargs:
                raise TypeError(
                    f'在 `{self.Info.alias}` 中，具名参数 `{name}` 与位置参数重复。'
                )
            kwargs[name] = value

        super().__init__(**kwargs)

    @classmethod
    def get_subtype(cls, name: str) -> Type['ApiModel']:
        try:
            return cast(Type['ApiModel'], super().get_subtype(name))
        except ValueError as e:
            raise ValueError(f'`{name}` 不是可用的 API！') from e

    async def call(
        self,
        api_provider: ApiProvider,
        method: Method = Method.GET,
        response_type: Optional[Type[TModel]] = None,
    ) -> Optional[TModel]:
        """调用 API。"""
        info = self.Info
        logger.debug(f'调用 API：{repr(self)}')
        raw_response = await api_provider.call_api(
            api=info.name,
            method=method,
            **self.dict(by_alias=True, exclude_none=True)
        )

        # 如果 API 无法调用，raw_response 为空
        if not raw_response:
            return None
        # 解析 API 返回数据
        response_type = cast(Type[TModel], response_type or info.response_type)
        return response_type.parse_obj(raw_response)

    class Proxy(Generic[TModel]):
        """API 代理类。由 API 构造，提供对适配器的访问。

            Proxy: 提供更加简便的调用 API 的写法。`Proxy` 对象一般由 `Mirai.__getattr__` 获得，
        这个方法依托于 `MiraiIndexedModel` 的子类获取机制，支持按照命名规范转写的 API，
        所有的 API 全部使用小写字母及下划线命名。

        对于 GET 方法的 API，可以使用 `get` 方法：
        ```py
        profile = await bot.friend_profile.get(12345678)
        ```

        或者直接调用：
        ```py
        profile = await bot.friend_profile(12345678)
        ```

        对于 POST 方法的 API，推荐直接调用：
        ```
        await bot.send_friend_message(12345678, [Plain('Hello World!')])
        ```

        `set` 方法也可用，但由于语义不准确，不推荐使用。

        对于 RESTful 的 API，首先应直接调用，传入基本参数，然后使用 `get` 或 `set`：
        ```py
        config = await bot.group_config(12345678).get()
        await bot.group_config(12345678).set(config.modify(announcement='测试'))
        ```

        `ApiProxy` 同时提供位置参数支持。比如上面的例子中，没有使用具名参数，而是使用位置参数，
        这可以让 API 调用更简洁。参数的顺序可参照 mirai-api-http
        的[文档](https://project-mirai.github.io/mirai-api-http/api/API.html)。
        除去`sessionKey`由适配器自动指定外，其余参数可按顺序传入。具名参数仍然可用，适当地使用具名参数可增强代码的可读性。
        """
        def __init__(
            self, api_provider: ApiProvider, api_type: Type['ApiModel']
        ):
            self.api_provider = api_provider
            self.api_type = api_type

        async def _call_api(
            self,
            method: Method = Method.GET,
            response_type: Optional[Type[TModel]] = None,
            args: Union[list, tuple, None] = None,
            kwargs: Optional[dict] = None
        ) -> Optional[TModel]:
            """调用 API。

            将结果解析为 Model。
            """
            args = args or []
            kwargs = kwargs or {}

            api = self.api_type(*args, **kwargs)
            return await api.call(self.api_provider, method, response_type)

        async def get(self, *args, **kwargs) -> Optional[TModel]:
            """获取。对于 GET 方法的 API，调用此方法。"""
            return await self._call_api(
                method=Method.GET, args=args, kwargs=kwargs
            )

        async def set(self, *args, **kwargs) -> Optional[TModel]:
            """设置。对于 POST 方法的 API，可调用此方法。"""
            return await self._call_api(
                method=Method.POST, args=args, kwargs=kwargs
            )

        async def __call__(self, *args, **kwargs):
            return await self.get(*args, **kwargs)


class ApiGet(ApiModel):
    class Proxy(ApiModel.Proxy[TModel]):
        async def set(self, *args, **kwargs):
            """GET 方法的 API 不具有 `set`。

            调用此方法会报错 `TypeError`。
            """
            raise TypeError(f'`{self.command}` 不支持 `set` 方法。')

        async def __call__(self, *args, **kwargs) -> Optional[TModel]:
            return await self.get(*args, **kwargs)


class ApiPost(ApiModel):
    class Proxy(ApiModel.Proxy[TModel]):
        """POST 方法的 API 代理对象。"""
        async def get(self, *args, **kwargs):
            """POST 方法的 API 不具有 `get`。

            调用此方法会报错 `TypeError`。
            """
            raise TypeError(f'`{self.command}` 不支持 `get` 方法。')

        async def __call__(self, *args, **kwargs) -> Optional[TModel]:
            return await self.set(*args, **kwargs)


class ApiRest(ApiModel):
    class Info(ApiModel.Info):
        """API 的信息。"""
        name = ""
        alias = ""
        method = Method.GET
        response_type = MiraiBaseModel
        response_type_post = Response

    class Proxy(ApiModel.Proxy[TModel]):
        """RESTful 的 API 代理对象。

        直接调用时，传入 GET 和 POST 的公共参数，返回一个 `ApiRest.Proxy.Partial` 对象，
        由此对象提供实际调用支持。
        """
        def __call__(self, *args, **kwargs) -> 'ApiRest.Proxy.Partial':
            return ApiRest.Proxy.Partial(
                self.api_provider, cast(Type['ApiRest'], self.api_type), args,
                kwargs
            )

        class Partial(ApiModel.Proxy[TModel]):
            """RESTful 的 API 代理对象（已传入公共参数）。"""
            def __init__(
                self, api_provider: ApiProvider, api_type: Type['ApiRest'],
                partial_args: Union[list, tuple], partial_kwargs: dict
            ):
                super().__init__(api_provider=api_provider, api_type=api_type)
                self.partial_args = partial_args
                self.partial_kwargs = partial_kwargs

            async def get(self, *args, **kwargs) -> Optional[TModel]:
                """获取。"""
                return await self._call_api(
                    method=Method.RESTGET,
                    args=[*self.partial_args, *args],
                    kwargs={
                        **self.partial_kwargs,
                        **kwargs
                    }
                )

            async def set(self, *args, **kwargs) -> Optional[TModel]:
                """设置。"""
                return await self._call_api(
                    method=Method.RESTPOST,
                    response_type=cast(
                        Type[TModel],
                        cast(Type[ApiRest],
                             self.api_type).Info.response_type_post
                    ),
                    args=[*self.partial_args, *args],
                    kwargs={
                        **self.partial_kwargs,
                        **kwargs
                    }
                )


class About(ApiGet):
    """获取插件信息。"""
    class Info(ApiGet.Info):
        name = "about"
        alias = "about"
        response_type = AboutResponse


class SessionInfo(ApiGet):
    """获取机器人信息。"""
    class Info(ApiGet.Info):
        name = "sessionInfo"
        alias = "session_info"
        response_type = SessionInfoResponse


class MessageFromId(ApiGet):
    """通过 message_id 获取消息。"""
    id: int
    """获取消息的 message_id。"""
    class Info(ApiGet.Info):
        name = "messageFromId"
        alias = "message_from_id"
        response_type = MessageFromIdResponse


class FriendList(ApiGet):
    """获取好友列表。"""
    class Info(ApiGet.Info):
        name = "friendList"
        alias = "friend_list"
        response_type = FriendListResponse


class GroupList(ApiGet):
    """获取群列表。"""
    class Info(ApiGet.Info):
        name = "groupList"
        alias = "group_list"
        response_type = GroupListResponse


class MemberList(ApiGet):
    """获取群成员列表。"""
    target: int
    """指定群的群号。"""
    class Info(ApiGet.Info):
        name = "memberList"
        alias = "member_list"
        response_type = MemberListResponse


class BotProfile(ApiGet):
    """获取 Bot 资料。"""
    class Info(ApiGet.Info):
        name = "botProfile"
        alias = "bot_profile"
        response_type = ProfileResponse


class FriendProfile(ApiGet):
    """获取好友资料。"""
    target: int
    """好友 QQ 号。"""
    class Info(ApiGet.Info):
        name = "friendProfile"
        alias = "friend_profile"
        response_type = ProfileResponse


class MemberProfile(ApiGet):
    """获取群成员资料。"""
    target: int
    """指定群的群号。"""
    member_id: int
    """指定群成员的 QQ 号。"""
    class Info(ApiGet.Info):
        name = "memberProfile"
        alias = "member_profile"
        response_type = ProfileResponse


class SendMessage(ApiBaseModel):
    """发送消息的 API 的方法复用，不作为 API 使用。"""
    # message_chain: TMessage

    @validator('message_chain', check_fields=False)
    def _validate_message_chain(cls, value: Union[MessageChain, list]):
        if isinstance(value, list):
            return MessageChain.parse_obj(value)
        return value


class SendFriendMessage(ApiPost, SendMessage):
    """发送好友消息。"""
    target: int
    """发送消息目标好友的 QQ 号。"""
    message_chain: TMessage
    """消息链。"""
    quote: Optional[int] = None
    """可选。引用一条消息的 message_id 进行回复。"""
    class Info(ApiPost.Info):
        name = "sendFriendMessage"
        alias = "send_friend_message"
        response_type = MessageResponse


class SendGroupMessage(ApiPost, SendMessage):
    """发送群消息。"""
    target: int
    """发送消息目标群的群号。"""
    message_chain: TMessage
    """消息链。"""
    quote: Optional[int] = None
    """可选。引用一条消息的 message_id 进行回复。"""
    class Info(ApiPost.Info):
        name = "sendGroupMessage"
        alias = "send_group_message"
        response_type = MessageResponse


class SendTempMessage(ApiPost, SendMessage):
    """发送临时消息。"""
    qq: int
    """临时会话对象 QQ 号。"""
    group: int
    """临时会话对象群号。"""
    message_chain: TMessage
    """消息链。"""
    quote: Optional[int] = None
    """可选。引用一条消息的 message_id 进行回复。"""
    class Info(ApiPost.Info):
        name = "sendTempMessage"
        alias = "send_temp_message"
        response_type = MessageResponse


class SendNudge(ApiPost):
    """发送头像戳一戳消息。"""
    target: int
    """戳一戳的目标 QQ 号，可以为 bot QQ 号。"""
    subject: int
    """戳一戳接受主体（上下文），戳一戳信息会发送至该主体，为群号或好友 QQ 号。"""
    kind: Literal['Friend', 'Group', 'Stranger']
    """上下文类型，可选值 `Friend`, `Group`, `Stranger`。"""
    class Info(ApiPost.Info):
        name = "sendNudge"
        alias = "send_nudge"
        response_type = Response


class Recall(ApiPost):
    """撤回消息。"""
    target: int
    """需要撤回的消息的 message_id。"""
    class Info(ApiPost.Info):
        name = "recall"
        alias = "recall"
        response_type = Response


class FileList(ApiGet):
    """查看文件列表。"""
    id: str
    """文件夹 id，空串为根目录。"""
    target: int
    """群号或好友 QQ 号。"""
    with_download_info: Optional[bool] = None
    """是否携带下载信息。"""
    path: Optional[str] = None
    """可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id。"""
    offset: Optional[int] = None
    """可选。分页偏移。"""
    size: Optional[int] = None
    """可选。分页大小。"""
    class Info(ApiGet.Info):
        name = "file/list"
        alias = "file_list"
        response_type = FileListResponse


class FileInfo(ApiGet):
    """查看文件信息。"""
    id: str
    """文件 id。"""
    target: int
    """群号或好友 QQ 号。"""
    with_download_info: Optional[bool] = None
    """是否携带下载信息。"""
    path: Optional[str] = None
    """可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id。"""
    class Info(ApiGet.Info):
        name = "file/info"
        alias = "file_info"
        response_type = FileInfoResponse


class FileMkdir(ApiPost):
    """创建文件夹。"""
    id: str
    """父目录 id。"""
    target: int
    """群号或好友 QQ 号。"""
    directory_name: str
    """新建文件夹名。"""
    path: Optional[str] = None
    """可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id。"""
    class Info(ApiPost.Info):
        name = "file/mkdir"
        alias = "file_mkdir"
        response_type = FileMkdirResponse


class FileDelete(ApiPost):
    """删除文件。"""
    id: str
    """欲删除的文件 id。"""
    target: int
    """群号或好友 QQ 号。"""
    path: Optional[str] = None
    """可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id。"""
    class Info(ApiPost.Info):
        name = "file/delete"
        alias = "file_delete"
        response_type = Response


class FileMove(ApiPost):
    """移动文件。"""
    id: str
    """欲移动的文件 id。"""
    target: int
    """群号或好友 QQ 号。"""
    move_to: str
    """移动目标文件夹 id。"""
    path: Optional[str] = None
    """可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id。"""
    move_to_path: Optional[str] = None
    """可选。移动目标文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id。"""
    class Info(ApiPost.Info):
        name = "file/move"
        alias = "file_move"
        response_type = Response


class FileRename(ApiPost):
    """重命名文件。"""
    id: str
    """欲重命名的文件 id。"""
    target: int
    """群号或好友 QQ 号。"""
    rename_to: str
    """新文件名。"""
    path: Optional[str] = None
    """可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id。"""
    class Info(ApiPost.Info):
        name = "file/rename"
        alias = "file_rename"
        response_type = Response


class FileUpload(ApiPost):
    """文件上传。（暂时不可用）"""
    type: Literal["group"]
    """上传的文件类型。"""
    target: int
    """群号。"""
    file: Union[str, Path]
    """上传的文件的本地路径。"""
    path: str = ''
    """上传目录的 id，空串为上传到根目录。"""
    async def call(
        self,
        api_provider: ApiProvider,
        method: Method = Method.GET,
        response_type: Optional[Type[TModel]] = None,
    ):
        import aiofiles
        async with aiofiles.open(self.file, 'rb') as f:
            file = await f.read()
        return await api_provider.call_api(
            'file/upload',
            method=Method.MULTIPART,
            data={
                'type': self.type,
                'target': self.target,
                'path': self.path,
            },
            files={'file': file}
        )

    class Info(ApiPost.Info):
        name = "file/upload"
        alias = "file_upload"
        response_type = FileProperties


class UploadImage(ApiPost):
    """图片文件上传。"""
    type: Literal["friend", "group", "temp"]
    """上传的图片类型。"""
    img: Union[str, Path]
    """上传的图片的本地路径。"""
    async def call(
        self,
        api_provider: ApiProvider,
        method: Method = Method.GET,
        response_type: Optional[Type[TModel]] = None,
    ):
        import aiofiles
        async with aiofiles.open(self.img, 'rb') as f:
            img = await f.read()
        return await api_provider.call_api(
            'uploadImage',
            method=Method.MULTIPART,
            data={'type': self.type},
            files={'img': img}
        )

    class Info(ApiPost.Info):
        name = "uploadImage"
        alias = "upload_image"
        response_type = Image


class UploadVoice(ApiPost):
    """语音文件上传。"""
    type: Literal["group", "friend", "temp"]
    """上传的语音类型。"""
    voice: Union[str, Path]
    """上传的语音的本地路径。"""
    async def call(
        self,
        api_provider: ApiProvider,
        method: Method = Method.GET,
        response_type: Optional[Type[TModel]] = None,
    ):
        import aiofiles
        async with aiofiles.open(self.voice, 'rb') as f:
            voice = await f.read()
        return await api_provider.call_api(
            'uploadVoice',
            method=Method.MULTIPART,
            data={'type': self.type},
            files={'voice': voice}
        )

    class Info(ApiPost.Info):
        name = "uploadVoice"
        alias = "upload_voice"
        response_type = Voice


class DeleteFriend(ApiPost):
    """删除好友。"""
    target: int
    """需要删除的好友 QQ 号。"""
    class Info(ApiPost.Info):
        name = "deleteFriend"
        alias = "delete_friend"
        response_type = Response


class Mute(ApiPost):
    """禁言群成员。"""
    target: int
    """指定群的群号。"""
    member_id: int
    """指定群成员的 QQ 号。"""
    time: int
    """禁言时间，单位为秒，最多30天，默认为0。"""
    class Info(ApiPost.Info):
        name = "mute"
        alias = "mute"
        response_type = Response


class Unmute(ApiPost):
    """解除群成员禁言。"""
    target: int
    """指定群的群号。"""
    member_id: int
    """指定群成员的 QQ 号。"""
    class Info(ApiPost.Info):
        name = "unmute"
        alias = "unmute"
        response_type = Response


class Kick(ApiPost):
    """移出群成员。"""
    target: int
    """指定群的群号。"""
    member_id: int
    """指定群成员的 QQ 号。"""
    msg: str = ""
    """可选。信息。"""
    class Info(ApiPost.Info):
        name = "kick"
        alias = "kick"
        response_type = Response


class Quit(ApiPost):
    """退出群聊。"""
    target: int
    """指定群的群号。"""
    class Info(ApiPost.Info):
        name = "quit"
        alias = "quit"
        response_type = Response


class MuteAll(ApiPost):
    """全体禁言。"""
    target: int
    """指定群的群号。"""
    class Info(ApiPost.Info):
        name = "muteAll"
        alias = "mute_all"
        response_type = Response


class UnmuteAll(ApiPost):
    """解除全体禁言。"""
    target: int
    """指定群的群号。"""
    class Info(ApiPost.Info):
        name = "unmuteAll"
        alias = "unmute_all"
        response_type = Response


class SetEssence(ApiPost):
    """设置群精华消息。"""
    target: int
    """精华消息的 message_id。"""
    class Info(ApiPost.Info):
        name = "setEssence"
        alias = "set_essence"
        response_type = Response


class GroupConfig(ApiRest):
    """获取或修改群设置。"""
    target: int
    """群号。"""
    config: Optional[GroupConfigModel] = None
    """仅修改时可用。群设置。"""
    class Info(ApiRest.Info):
        name = "groupConfig"
        alias = "group_config"
        response_type = GroupConfigModel
        response_type_post = Response


class MemberInfo(ApiRest):
    """获取或修改群成员资料。"""
    target: int
    """群号。"""
    member_id: int
    """指定群成员的 QQ 号。"""
    info: Optional[MemberInfoModel] = None
    """仅修改时可用。群成员资料。"""
    class Info(ApiRest.Info):
        name = "memberInfo"
        alias = "member_info"
        response_type = MemberInfoModel
        response_type_post = Response


class MemberAdmin(ApiPost):
    """设置或取消群成员管理员。"""
    target: int
    """群号。"""
    member_id: int
    """指定群成员的 QQ 号。"""
    assign: bool
    """是否设置管理员。"""
    class Info(ApiPost.Info):
        name = "memberAdmin"
        alias = "member_admin"
        response_type = Response


class RespOperate(Flag):
    """事件响应操作。

    使用例：

    `RespOperate.ALLOW` 允许请求

    `RespOperate.DECLINE & RespOpearte.BAN` 拒绝并拉黑
    """
    ALLOW = 1
    """允许请求。"""
    DECLINE = 2
    """拒绝请求。"""
    IGNORE = 3
    """忽略请求。"""
    BAN = 4
    """拉黑。与前三个选项组合。"""


class RespEvent(ApiBaseModel):
    """事件处理的 API 的方法复用，不作为 API 使用。"""
    event_id: int
    """响应申请事件的标识。"""
    from_id: int
    """事件对应申请人 QQ 号。"""
    group_id: int
    """事件对应申请人的群号，可能为0。"""
    operate: Union[int, RespOperate]
    """响应的操作类型。"""
    message: str
    """回复的信息。"""
    @classmethod
    def from_event(
        cls, event: RequestEvent, operate: Union[int, RespOperate],
        message: str
    ):
        """从事件构造响应。"""
        return cls(
            event_id=event.event_id,
            from_id=event.from_id,
            group_id=event.group_id,
            operate=operate,
            message=message
        )


class RespNewFriendRequestEvent(ApiPost, RespEvent):
    """响应添加好友申请。"""
    event_id: int
    """响应申请事件的标识。"""
    from_id: int
    """事件对应申请人 QQ 号。"""
    group_id: int
    """事件对应申请人的群号，可能为0。"""
    operate: Union[int, RespOperate]
    """响应的操作类型。"""
    message: str
    """回复的信息。"""
    @validator('operate')
    def _validate_operate(cls, v):
        if isinstance(v, RespOperate):
            if v == RespOperate.ALLOW:
                return 0
            if v == RespOperate.DECLINE:
                return 1
            if v == RespOperate.DECLINE & RespOperate.BAN:
                return 2
            raise ValueError(f'无效操作{v}。')
        return v

    class Info(ApiPost.Info):
        name = "resp/newFriendRequestEvent"
        alias = "resp_new_friend_request_event"
        response_type = MiraiBaseModel


class RespMemberJoinRequestEvent(ApiPost, RespEvent):
    """响应用户入群申请。"""
    event_id: int
    """响应申请事件的标识。"""
    from_id: int
    """事件对应申请人 QQ 号。"""
    group_id: int
    """事件对应申请人的群号。"""
    operate: Union[int, RespOperate]
    """响应的操作类型。"""
    message: str
    """回复的信息。"""
    @validator('operate')
    def _validate_operate(cls, v):
        if isinstance(v, RespOperate):
            if v == RespOperate.ALLOW:
                return 0
            if v == RespOperate.DECLINE:
                return 1
            if v == RespOperate.IGNORE:
                return 2
            if v == RespOperate.DECLINE & RespOperate.BAN:
                return 3
            if v == RespOperate.IGNORE & RespOperate.BAN:
                return 4
            raise ValueError(f'无效操作{v}。')
        return v

    class Info(ApiPost.Info):
        name = "resp/memberJoinRequestEvent"
        alias = "resp_member_join_request_event"
        response_type = MiraiBaseModel


class RespBotInvitedJoinGroupRequestEvent(ApiPost, RespEvent):
    """响应被邀请入群申请。"""
    event_id: int
    """响应申请事件的标识。"""
    from_id: int
    """事件对应申请人 QQ 号。"""
    group_id: int
    """事件对应申请人的群号，可能为0。"""
    operate: Union[int, RespOperate]
    """响应的操作类型。"""
    message: str
    """回复的信息。"""
    @validator('operate')
    def _validate_operate(cls, v):
        if isinstance(v, RespOperate):
            if v == RespOperate.ALLOW:
                return 0
            if v == RespOperate.DECLINE:
                return 1
            raise ValueError(f'无效操作{v}。')
        return v

    class Info(ApiPost.Info):
        name = "resp/botInvitedJoinGroupRequestEvent"
        alias = "resp_bot_invited_join_group_request_event"
        response_type = MiraiBaseModel


class CmdExecute(ApiPost):
    """执行命令。"""
    command: Union[MessageChain, Iterable[Union[MessageComponent, str]], str]
    """命令。"""
    @validator('command')
    def _validate_command(cls, value):
        if isinstance(value, list):
            return MessageChain.parse_obj(value)
        return value

    class Info(ApiPost.Info):
        name = "cmd/execute"
        alias = "cmd_execute"
        response_type = Response


class CmdRegister(ApiPost):
    """注册命令。"""
    name: str
    """命令名称。"""
    usage: str
    """使用说明。"""
    description: str
    """命令描述。"""
    alias: Optional[List[str]] = None
    """可选。命令别名。"""
    class Info(ApiPost.Info):
        name = "cmd/register"
        alias = "cmd_register"
        response_type = Response


__all__ = [
    'About',
    'AboutResponse',
    'ApiBaseModel',
    'ApiGet',
    'ApiMetaclass',
    'ApiModel',
    'ApiPost',
    'ApiProvider',
    'ApiRest',
    'BotProfile',
    'CmdExecute',
    'CmdRegister',
    'DeleteFriend',
    'DownloadInfo',
    'FileDelete',
    'FileInfo',
    'FileInfoResponse',
    'FileList',
    'FileListResponse',
    'FileMkdir',
    'FileMkdirResponse',
    'FileMove',
    'FileProperties',
    'FileRename',
    'FileUpload',
    'FriendList',
    'FriendListResponse',
    'FriendMessage',
    'FriendProfile',
    'GroupConfig',
    'GroupConfigModel',
    'GroupList',
    'GroupListResponse',
    'GroupMember',
    'GroupMessage',
    'Kick',
    'MemberAdmin',
    'MemberInfo',
    'MemberInfoModel',
    'MemberList',
    'MemberListResponse',
    'MemberProfile',
    'MessageFromId',
    'MessageFromIdResponse',
    'MessageResponse',
    'Mute',
    'MuteAll',
    'OtherClientMessage',
    'ProfileResponse',
    'Quit',
    'Recall',
    'RequestEvent',
    'RespBotInvitedJoinGroupRequestEvent',
    'RespEvent',
    'RespMemberJoinRequestEvent',
    'RespNewFriendRequestEvent',
    'RespOperate',
    'Response',
    'SendFriendMessage',
    'SendGroupMessage',
    'SendMessage',
    'SendNudge',
    'SendTempMessage',
    'SessionInfo',
    'SessionInfoResponse',
    'SetEssence',
    'Sex',
    'StrangerMessage',
    'TempMessage',
    'Unmute',
    'UnmuteAll',
    'UploadImage',
    'UploadVoice',
]
