# -*- coding: utf-8 -*-
"""
`mirai.bot` 模块的存根文件，用于补全代码提示。
"""
from pathlib import Path
from typing import (
    Any, Callable, Dict, Iterable, List, NoReturn, Optional, Type, Union
)

from mirai.models.base import MiraiBaseModel

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from mirai.adapters.base import Adapter, AdapterInterface, ApiProvider
from mirai.models.api import (
    AboutResponse, ApiModel, File, FileInfoResponse, FileListResponse,
    FileMkdirResponse, FriendListResponse, GroupListResponse,
    MemberListResponse, MessageFromIdResponse, MessageResponse,
    ProfileResponse, Response, RespOperate, SessionInfoResponse
)
from mirai.models.entities import (
    Entity, Friend, Group, GroupConfigModel, GroupMember, MemberInfoModel,
    Subject
)
from mirai.models.events import Event, MessageEvent
from mirai.models.message import Image, MessageChain, MessageComponent, Voice
from mirai.utils import Singleton


class SimpleMirai(ApiProvider, AdapterInterface):
    qq: int

    def __init__(self, qq: int, adapter: Adapter) -> NoReturn:
        ...

    async def call_api(self, api: str, *args, **kwargs):
        ...

    def on(self, event: str) -> Callable:
        ...

    @property
    def adapter_info(self) -> Dict[str, Any]:
        ...

    async def use_adapter(self, adapter: Adapter):
        ...

    async def startup(self) -> NoReturn:
        ...

    async def background(self) -> NoReturn:
        ...

    async def shutdown(self) -> NoReturn:
        ...

    @property
    def session(self) -> str:
        ...

    @property
    def asgi(self) -> MiraiRunner:
        ...

    def run(
        self,
        host: str = ...,
        port: int = ...,
        asgi_server: str = ...,
        **kwargs
    ) -> NoReturn:
        ...


class MiraiRunner(Singleton):
    bots: Iterable[SimpleMirai]

    def __init__(self, *bots: SimpleMirai) -> NoReturn:
        ...

    async def startup(self) -> NoReturn:
        ...

    async def shutdown(self) -> NoReturn:
        ...

    async def __call__(self, scope, recv, send) -> NoReturn:
        ...

    def run(
        self,
        host: str = ...,
        port: int = ...,
        asgi_server: str = ...,
        **kwargs
    ) -> NoReturn:
        ...


class Mirai(SimpleMirai):
    def __init__(self, qq: int, adapter: Adapter) -> NoReturn:
        ...

    def on(self, event_type: Union[Type[Event], str]) -> Callable:
        ...

    def api(self, api: str) -> ApiModel.Proxy:
        ...

    def __getattr__(self, api: str) -> ApiModel.Proxy:
        ...

    async def send(
        self,
        target: Union[Entity, MessageEvent],
        message: Union[MessageChain, List[Union[MessageComponent, str]], str],
        quote: bool = ...
    ) -> int:
        ...

    async def get_friend(self, id: int) -> Optional[Friend]:
        ...

    async def get_group(self, id: int) -> Optional[Group]:
        ...

    async def get_group_member(self, group: Union[Group, int],
                               id: int) -> Optional[GroupMember]:
        ...

    async def get_entity(self, subject: Subject) -> Optional[Entity]:
        ...

    async def is_admin(self, group: Group) -> bool:
        ...

    def about(self, ) -> ApiModel.Proxy[AboutResponse]:
        ... # About

    def bot_profile(self, ) -> ApiModel.Proxy[ProfileResponse]:
        ... # BotProfile

    def cmd_execute(
        self, command: Union[MessageChain, List[Union[MessageComponent, str]],
                             str]
    ) -> ApiModel.Proxy[Response]:
        ... # CmdExecute

    def cmd_register(
        self,
        name: str,
        alias: Optional[List[str]] = None,
        usage: str = '',
        description: str = ''
    ) -> ApiModel.Proxy[Response]:
        ... # CmdRegister

    def delete_friend(self, target: int) -> ApiModel.Proxy[Response]:
        ... # DeleteFriend

    def file_delete(self, id: str, target: int) -> ApiModel.Proxy[Response]:
        ... # FileDelete

    def file_info(self, id: str,
                  target: int) -> ApiModel.Proxy[FileInfoResponse]:
        ... # FileInfo

    def file_list(self, id: str,
                  target: int) -> ApiModel.Proxy[FileListResponse]:
        ... # FileList

    def file_mkdir(self, id: str, target: int,
                   directory_name: str) -> ApiModel.Proxy[FileMkdirResponse]:
        ... # FileMkdir

    def file_move(self, id: str, target: int,
                  move_to: str) -> ApiModel.Proxy[Response]:
        ... # FileMove

    def file_rename(self, id: str, target: int,
                    rename_to: str) -> ApiModel.Proxy[Response]:
        ... # FileRename

    def file_upload(
        self, type: Literal['group'], target: int, file: Union[str, Path],
        path: str
    ) -> ApiModel.Proxy[File]:
        ... # FileUpload

    def friend_list(self, ) -> ApiModel.Proxy[FriendListResponse]:
        ... # FriendList

    def friend_profile(self, target: int) -> ApiModel.Proxy[ProfileResponse]:
        ... # FriendProfile

    def group_config(
        self,
        target: int,
        config: Optional[GroupConfigModel] = None
    ) -> ApiModel.Proxy[GroupConfigModel]:
        ... # GroupConfig

    def group_list(self, ) -> ApiModel.Proxy[GroupListResponse]:
        ... # GroupList

    def kick(self, target: int, memder_id: int,
             msg: str) -> ApiModel.Proxy[Response]:
        ... # Kick

    def member_info(
        self,
        target: int,
        member_id: int,
        info: Optional[MemberInfoModel] = None
    ) -> ApiModel.Proxy[MemberInfoModel]:
        ... # MemberInfo

    def member_list(self, target: int) -> ApiModel.Proxy[MemberListResponse]:
        ... # MemberList

    def member_profile(self, target: int,
                       member_id: int) -> ApiModel.Proxy[ProfileResponse]:
        ... # MemberProfile

    def message_from_id(self,
                        id: int) -> ApiModel.Proxy[MessageFromIdResponse]:
        ... # MessageFromId

    def mute(self, target: int, memder_id: int,
             time: int) -> ApiModel.Proxy[Response]:
        ... # Mute

    def mute_all(self, target: int) -> ApiModel.Proxy[Response]:
        ... # MuteAll

    def quit(self, target: int) -> ApiModel.Proxy[Response]:
        ... # Quit

    def recall(self, target: int) -> ApiModel.Proxy[Response]:
        ... # Recall

    def resp_bot_invited_join_group_request_event(
        self, event_id: int, from_id: int, group_id: int,
        operate: Union[int, RespOperate], message: str
    ) -> ApiModel.Proxy[MiraiBaseModel]:
        ... # RespBotInvitedJoinGroupRequestEvent

    def resp_member_join_request_event(
        self, event_id: int, from_id: int, group_id: int,
        operate: Union[int, RespOperate], message: str
    ) -> ApiModel.Proxy[MiraiBaseModel]:
        ... # RespMemberJoinRequestEvent

    def resp_new_friend_request_event(
        self, event_id: int, from_id: int, group_id: int,
        operate: Union[int, RespOperate], message: str
    ) -> ApiModel.Proxy[MiraiBaseModel]:
        ... # RespNewFriendRequestEvent

    def send_friend_message(
        self,
        target: int,
        message_chain: Union[MessageChain, List[Union[MessageComponent, str]],
                             str],
        quote: Optional[int] = None
    ) -> ApiModel.Proxy[MessageResponse]:
        ... # SendFriendMessage

    def send_group_message(
        self,
        target: int,
        message_chain: Union[MessageChain, List[Union[MessageComponent, str]],
                             str],
        quote: Optional[int] = None
    ) -> ApiModel.Proxy[MessageResponse]:
        ... # SendGroupMessage

    def send_nudge(
        self, target: int, subject: int, kind: Literal['Friend', 'Group',
                                                       'Stranger']
    ) -> ApiModel.Proxy[Response]:
        ... # SendNudge

    def send_temp_message(
        self,
        qq: int,
        group: int,
        message_chain: Union[MessageChain, List[Union[MessageComponent, str]],
                             str],
        quote: Optional[int] = None
    ) -> ApiModel.Proxy[MessageResponse]:
        ... # SendTempMessage

    def session_info(self, ) -> ApiModel.Proxy[SessionInfoResponse]:
        ... # SessionInfo

    def set_essence(self, target: int) -> ApiModel.Proxy[Response]:
        ... # SetEssence

    def unmute(self, target: int, memder_id: int) -> ApiModel.Proxy[Response]:
        ... # Unmute

    def unmute_all(self, target: int) -> ApiModel.Proxy[Response]:
        ... # UnmuteAll

    def upload_image(
        self, type: Literal['friend', 'group', 'temp'], img: Union[str, Path]
    ) -> ApiModel.Proxy[Image]:
        ... # UploadImage

    def upload_voice(self, type: Literal['group'],
                     voice: Union[str, Path]) -> ApiModel.Proxy[Voice]:
        ... # UploadVoice


class LifeSpan(Event):
    type: str


class Startup(LifeSpan):
    type: str


class Shutdown(LifeSpan):
    type: str
