"""
具体的 API 实现和定义。
"""
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, List, Optional, Union
from mirai.api_provider import ApiProvider, Method

if TYPE_CHECKING:
    from typing_extensions import Literal
else:
    try:
        from typing import Literal
    except ImportError:
        from typing_extensions import Literal

from mirai.models.api import ApiBaseModel, ApiGet, ApiPost, ApiResponse, ApiRest
from mirai.models.base import MiraiBaseModel
from mirai.models.entities import FileProperties, Friend, Group, GroupConfigModel, GroupMember, MemberInfoModel, Profile, RespOperate, Sex
from mirai.models.events import (
    FriendMessage, GroupMessage, OtherClientMessage, RequestEvent,
    StrangerMessage, TempMessage
)
from mirai.models.message import (
    Image, MessageChain, MessageComponent, TMessage, Voice
)
from pydantic import Field, validator


class About(ApiGet):
    """获取插件信息。"""
    class Info(ApiGet.Info):
        name = "about"
        alias = "about"

    class Response(ApiResponse):
        data: dict


class SessionInfo(ApiGet):
    """获取机器人信息。"""
    class Info(ApiGet.Info):
        name = "sessionInfo"
        alias = "session_info"

    class Response(ApiResponse):
        data: 'SessionInfo.Response.Data'

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


SessionInfo.Response.update_forward_refs()


class MessageFromId(ApiGet):
    """通过 message_id 获取消息。"""
    id: int
    """获取消息的 message_id。"""
    class Info(ApiGet.Info):
        name = "messageFromId"
        alias = "message_from_id"

    class Response(ApiResponse):
        data: Union[FriendMessage, GroupMessage, TempMessage, StrangerMessage,
                    OtherClientMessage]
        """获取的消息，以消息事件的形式返回。"""


class FriendList(ApiGet):
    """获取好友列表。"""
    class Info(ApiGet.Info):
        name = "friendList"
        alias = "friend_list"

    class Response(ApiResponse):
        data: List[Friend]
        """好友列表。"""
        def __iter__(self):
            yield from self.data


class GroupList(ApiGet):
    """获取群列表。"""
    class Info(ApiGet.Info):
        name = "groupList"
        alias = "group_list"

    class Response(ApiResponse):
        data: List[Group]
        """群组列表。"""
        def __iter__(self):
            yield from self.data


class MemberList(ApiGet):
    """获取群成员列表。"""
    target: int
    """指定群的群号。"""
    class Info(ApiGet.Info):
        name = "memberList"
        alias = "member_list"

    class Response(ApiResponse):
        data: List[GroupMember]
        """群成员列表。"""
        def __iter__(self):
            yield from self.data


class BotProfile(ApiGet):
    """获取 Bot 资料。"""
    class Info(ApiGet.Info):
        name = "botProfile"
        alias = "bot_profile"

    class Response(ApiResponse):
        data: Profile


class FriendProfile(ApiGet):
    """获取好友资料。"""
    target: int
    """好友 QQ 号。"""
    class Info(ApiGet.Info):
        name = "friendProfile"
        alias = "friend_profile"

    class Response(ApiResponse):
        data: Profile


class MemberProfile(ApiGet):
    """获取群成员资料。"""
    target: int
    """指定群的群号。"""
    member_id: int
    """指定群成员的 QQ 号。"""
    class Info(ApiGet.Info):
        name = "memberProfile"
        alias = "member_profile"

    class Response(ApiResponse):
        data: Profile


class _SendMessage(ApiBaseModel):
    """发送消息的 API 的方法复用，不作为 API 使用。"""
    # message_chain: TMessage

    @validator('message_chain', check_fields=False)
    def _validate_message_chain(cls, value: Union[MessageChain, list]):
        if isinstance(value, list):
            return MessageChain.parse_obj(value)
        return value


class SendFriendMessage(ApiPost, _SendMessage):
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

    class Response(ApiResponse):
        data: int = Field(-1, alias='messageId')
        """消息的 message_id。"""


class SendGroupMessage(ApiPost, _SendMessage):
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

    class Response(ApiResponse):
        data: int = Field(..., alias='messageId')
        """消息的 message_id。"""


class SendTempMessage(ApiPost, _SendMessage):
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

    class Response(ApiResponse):
        data: int = Field(..., alias='messageId')
        """消息的 message_id。"""


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


class Recall(ApiPost):
    """撤回消息。"""
    target: int
    """需要撤回的消息的 message_id。"""
    class Info(ApiPost.Info):
        name = "recall"
        alias = "recall"


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

    class Response(ApiResponse):
        data: List[FileProperties]

        def __iter__(self):
            yield from self.data

        def files(self):
            """返回文件列表。"""
            return [item for item in self if item.is_file]

        def directories(self):
            """返回文件夹列表。"""
            return [item for item in self if item.is_directory]


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

    class Response(ApiResponse):
        data: FileProperties


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

    class Response(ApiResponse):
        data: FileProperties


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

    class Response(ApiResponse):
        pass


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

    class Response(ApiResponse):
        pass


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

    class Response(ApiResponse):
        pass


class FileUpload(ApiPost):
    """文件上传。"""
    type: Literal["group"]
    """上传的文件类型。"""
    target: int
    """群号。"""
    file: Union[str, Path]
    """上传的文件的本地路径。"""
    path: str = ''
    """上传目录的 id，空串为上传到根目录。"""
    async def _call(
        self,
        api_provider: ApiProvider,
        method: Method = Method.GET,
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

    class Response(ApiResponse):
        data: FileProperties


class UploadImage(ApiPost):
    """图片文件上传。"""
    type: Literal["friend", "group", "temp"]
    """上传的图片类型。"""
    img: Union[str, Path]
    """上传的图片的本地路径。"""
    async def _call(
        self,
        api_provider: ApiProvider,
        method: Method = Method.GET,
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

    class Response(ApiResponse):
        data: Image


class UploadVoice(ApiPost):
    """语音文件上传。"""
    type: Literal["group", "friend", "temp"]
    """上传的语音类型。"""
    voice: Union[str, Path]
    """上传的语音的本地路径。"""
    async def _call(
        self,
        api_provider: ApiProvider,
        method: Method = Method.GET,
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

    class Response(ApiResponse):
        data: Voice


class DeleteFriend(ApiPost):
    """删除好友。"""
    target: int
    """需要删除的好友 QQ 号。"""
    class Info(ApiPost.Info):
        name = "deleteFriend"
        alias = "delete_friend"


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


class Unmute(ApiPost):
    """解除群成员禁言。"""
    target: int
    """指定群的群号。"""
    member_id: int
    """指定群成员的 QQ 号。"""
    class Info(ApiPost.Info):
        name = "unmute"
        alias = "unmute"


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


class Quit(ApiPost):
    """退出群聊。"""
    target: int
    """指定群的群号。"""
    class Info(ApiPost.Info):
        name = "quit"
        alias = "quit"


class MuteAll(ApiPost):
    """全体禁言。"""
    target: int
    """指定群的群号。"""
    class Info(ApiPost.Info):
        name = "muteAll"
        alias = "mute_all"

    class Response(ApiResponse):
        pass


class UnmuteAll(ApiPost):
    """解除全体禁言。"""
    target: int
    """指定群的群号。"""
    class Info(ApiPost.Info):
        name = "unmuteAll"
        alias = "unmute_all"


class SetEssence(ApiPost):
    """设置群精华消息。"""
    target: int
    """精华消息的 message_id。"""
    class Info(ApiPost.Info):
        name = "setEssence"
        alias = "set_essence"


class GroupConfig(ApiRest):
    """获取或修改群设置。"""
    target: int
    """群号。"""
    config: Optional[GroupConfigModel] = None
    """仅修改时可用。群设置。"""
    class Info(ApiRest.Info):
        name = "groupConfig"
        alias = "group_config"

    class Response(ApiResponse):
        data: GroupConfigModel


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

    class Response(ApiResponse):
        data: MemberInfoModel


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
