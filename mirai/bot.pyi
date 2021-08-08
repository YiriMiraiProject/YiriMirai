# -*- coding: utf-8 -*-
"""
`mirai.bot` 模块的存根文件，用于补全代码提示。
"""
from pathlib import Path
from typing import (
    Any, Awaitable, Callable, Dict, Iterable, List, Optional, Type, Union
)

from mirai.asgi import ASGI
from mirai.models.base import MiraiBaseModel

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from mirai.adapters.base import Adapter, AdapterInterface, ApiProvider
from mirai.bus import AbstractEventBus
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


class SimpleMirai(ApiProvider, AdapterInterface, AbstractEventBus):
    qq: int

    def __init__(self, qq: int, adapter: Adapter) -> None:
        ...

    def subscribe(self, event, func: Callable, priority: int = 0) -> None:
        ...

    def unsubscribe(self, event, func: Callable) -> None:
        ...

    async def emit(self, event, *args, **kwargs) -> List[Awaitable[Any]]:
        ...

    async def call_api(self, api: str, *args, **kwargs):
        ...

    def on(self, event: str, priority: int = 0) -> Callable:
        ...

    @property
    def adapter_info(self) -> Dict[str, Any]:
        ...

    async def use_adapter(self, adapter: Adapter):
        ...

    async def startup(self) -> None:
        ...

    async def background(self) -> None:
        ...

    async def shutdown(self) -> None:
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
    ) -> None:
        ...


class MiraiRunner(Singleton):
    _asgi: ASGI
    bots: Iterable[SimpleMirai]

    def __init__(self, *bots: SimpleMirai) -> None:
        ...

    async def startup(self) -> None:
        ...

    async def shutdown(self) -> None:
        ...

    async def __call__(self, scope, recv, send) -> None:
        ...

    def run(
        self,
        host: str = ...,
        port: int = ...,
        asgi_server: str = ...,
        **kwargs
    ) -> None:
        ...


class Mirai(SimpleMirai):
    def __init__(self, qq: int, adapter: Adapter) -> None:
        ...

    def on(
        self,
        event_type: Union[Type[Event], str],
        priority: int = 0
    ) -> Callable:
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

    @property
    def about(self, ) -> ApiModel.Proxy[AboutResponse]:
        ...  # About

    @property
    def bot_profile(self, ) -> ApiModel.Proxy[ProfileResponse]:
        ...  # BotProfile

    @property
    def cmd_execute(
        self, command: Union[MessageChain, List[Union[MessageComponent, str]],
                             str]
    ) -> ApiModel.Proxy[Response]:
        ...  # CmdExecute

    @property
    def cmd_register(
        self,
        name: str,
        alias: Optional[List[str]] = None,
        usage: str = '',
        description: str = ''
    ) -> ApiModel.Proxy[Response]:
        ...  # CmdRegister

    @property
    def delete_friend(self, target: int) -> ApiModel.Proxy[Response]:
        ...  # DeleteFriend

    @property
    def file_delete(self, id: str, target: int) -> ApiModel.Proxy[Response]:
        ...  # FileDelete

    @property
    def file_info(self, id: str,
                  target: int) -> ApiModel.Proxy[FileInfoResponse]:
        ...  # FileInfo

    @property
    def file_list(self, id: str,
                  target: int) -> ApiModel.Proxy[FileListResponse]:
        ...  # FileList

    @property
    def file_mkdir(self, id: str, target: int,
                   directory_name: str) -> ApiModel.Proxy[FileMkdirResponse]:
        ...  # FileMkdir

    @property
    def file_move(self, id: str, target: int,
                  move_to: str) -> ApiModel.Proxy[Response]:
        ...  # FileMove

    @property
    def file_rename(self, id: str, target: int,
                    rename_to: str) -> ApiModel.Proxy[Response]:
        ...  # FileRename

    @property
    def file_upload(
        self, type: Literal['group'], target: int, file: Union[str, Path],
        path: str
    ) -> ApiModel.Proxy[File]:
        ...  # FileUpload

    @property
    def friend_list(self, ) -> ApiModel.Proxy[FriendListResponse]:
        ...  # FriendList

    @property
    def friend_profile(self, target: int) -> ApiModel.Proxy[ProfileResponse]:
        ...  # FriendProfile

    @property
    def group_config(
        self,
        target: int,
        config: Optional[GroupConfigModel] = None
    ) -> ApiModel.Proxy[GroupConfigModel]:
        ...  # GroupConfig

    @property
    def group_list(self, ) -> ApiModel.Proxy[GroupListResponse]:
        ...  # GroupList

    @property
    def kick(self, target: int, memder_id: int,
             msg: str) -> ApiModel.Proxy[Response]:
        ...  # Kick

    @property
    def member_info(
        self,
        target: int,
        member_id: int,
        info: Optional[MemberInfoModel] = None
    ) -> ApiModel.Proxy[MemberInfoModel]:
        ...  # MemberInfo

    @property
    def member_list(self, target: int) -> ApiModel.Proxy[MemberListResponse]:
        ...  # MemberList

    @property
    def member_profile(self, target: int,
                       member_id: int) -> ApiModel.Proxy[ProfileResponse]:
        ...  # MemberProfile

    @property
    def message_from_id(self,
                        id: int) -> ApiModel.Proxy[MessageFromIdResponse]:
        ...  # MessageFromId

    @property
    def mute(self, target: int, memder_id: int,
             time: int) -> ApiModel.Proxy[Response]:
        ...  # Mute

    @property
    def mute_all(self, target: int) -> ApiModel.Proxy[Response]:
        ...  # MuteAll

    @property
    def quit(self, target: int) -> ApiModel.Proxy[Response]:
        ...  # Quit

    @property
    def recall(self, target: int) -> ApiModel.Proxy[Response]:
        ...  # Recall

    @property
    def resp_bot_invited_join_group_request_event(
        self, event_id: int, from_id: int, group_id: int,
        operate: Union[int, RespOperate], message: str
    ) -> ApiModel.Proxy[MiraiBaseModel]:
        ...  # RespBotInvitedJoinGroupRequestEvent

    @property
    def resp_member_join_request_event(
        self, event_id: int, from_id: int, group_id: int,
        operate: Union[int, RespOperate], message: str
    ) -> ApiModel.Proxy[MiraiBaseModel]:
        ...  # RespMemberJoinRequestEvent

    @property
    def resp_new_friend_request_event(
        self, event_id: int, from_id: int, group_id: int,
        operate: Union[int, RespOperate], message: str
    ) -> ApiModel.Proxy[MiraiBaseModel]:
        ...  # RespNewFriendRequestEvent

    @property
    def send_friend_message(
        self,
        target: int,
        message_chain: Union[MessageChain, List[Union[MessageComponent, str]],
                             str],
        quote: Optional[int] = None
    ) -> ApiModel.Proxy[MessageResponse]:
        ...  # SendFriendMessage

    @property
    def send_group_message(
        self,
        target: int,
        message_chain: Union[MessageChain, List[Union[MessageComponent, str]],
                             str],
        quote: Optional[int] = None
    ) -> ApiModel.Proxy[MessageResponse]:
        ...  # SendGroupMessage

    @property
    def send_nudge(
        self, target: int, subject: int, kind: Literal['Friend', 'Group',
                                                       'Stranger']
    ) -> ApiModel.Proxy[Response]:
        ...  # SendNudge

    @property
    def send_temp_message(
        self,
        qq: int,
        group: int,
        message_chain: Union[MessageChain, List[Union[MessageComponent, str]],
                             str],
        quote: Optional[int] = None
    ) -> ApiModel.Proxy[MessageResponse]:
        ...  # SendTempMessage

    @property
    def session_info(self, ) -> ApiModel.Proxy[SessionInfoResponse]:
        ...  # SessionInfo

    @property
    def set_essence(self, target: int) -> ApiModel.Proxy[Response]:
        ...  # SetEssence

    @property
    def unmute(self, target: int, memder_id: int) -> ApiModel.Proxy[Response]:
        ...  # Unmute

    @property
    def unmute_all(self, target: int) -> ApiModel.Proxy[Response]:
        ...  # UnmuteAll

    @property
    def upload_image(
        self, type: Literal['friend', 'group', 'temp'], img: Union[str, Path]
    ) -> ApiModel.Proxy[Image]:
        ...  # UploadImage

    @property
    def upload_voice(self, type: Literal['group'],
                     voice: Union[str, Path]) -> ApiModel.Proxy[Voice]:
        ...  # UploadVoice


class LifeSpan(Event):
    type: str


class Startup(LifeSpan):
    type: str


class Shutdown(LifeSpan):
    type: str
