# -*- coding: utf-8 -*-
"""
`mirai.bot` 模块的存根文件，用于补全代码提示。
"""
from pathlib import Path
from typing import (
    Any, Awaitable, Callable, Dict, Iterable, List, Optional, Union, overload,
    type_check_only
)

from typing_extensions import Literal

from mirai.adapters.base import Adapter, AdapterInterface, Session
from mirai.asgi import ASGI
from mirai.bus import EventBus, TEventHandler
from mirai.models.api import ApiModel
from mirai.models.api_impl import *
from mirai.models.entities import (
    Entity, Friend, Group, GroupConfigModel, GroupMember, MemberInfoModel,
    Profile, Subject
)
from mirai.models.events import Event, MessageEvent, RequestEvent
from mirai.models.message import Image, MessageChain, MessageComponent, Voice
from mirai.utils import Singleton


class LifeSpan(Event):
    type: str


class Startup(LifeSpan):
    type: str


class Shutdown(LifeSpan):
    type: str


def __getattr__(name) -> Any:
    ...


class MiraiRunner(Singleton):
    _asgi: ASGI
    bots: Iterable['Mirai']

    def __init__(self, *bots: 'Mirai') -> None:
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

    async def _run(self):
        ...


class Mirai(AdapterInterface):
    qq: int

    def __init__(self, qq: int, adapter: Adapter) -> None:
        ...

    @property
    def bus(self) -> EventBus:
        ...

    def subscribe(
        self,
        event_type: Union[type, str],
        func: TEventHandler,
        priority: int = ...
    ) -> None:
        ...

    def unsubscribe(
        self, event_type: Union[type, str], func: Callable
    ) -> None:
        ...

    def on(
        self, *event_types: Union[type, str], priority: int = ...
    ) -> Callable:
        ...

    async def call_api(self, api: str, *args, **kwargs):
        ...

    @property
    def adapter_info(self) -> Dict[str, Any]:
        ...

    async def use_adapter(self, adapter: Adapter):
        ...

    @property
    def session(self) -> Session:
        ...

    async def startup(self) -> None:
        ...

    async def background(self) -> None:
        ...

    async def shutdown(self) -> None:
        ...

    @property
    def asgi(self) -> MiraiRunner:
        ...

    @overload
    def add_background_task(self) -> Callable[[Callable], Callable]:
        ...

    @overload
    def add_background_task(self, func: Callable) -> Callable:
        ...

    @overload
    def add_background_task(self, func: Awaitable) -> Awaitable:
        ...

    def run(
        self,
        host: str = ...,
        port: int = ...,
        asgi_server: str = ...,
        **kwargs
    ) -> None:
        ...

    def api(self, api: str) -> ApiModel.Proxy:
        ...

    def __getattr__(self, api: str) -> ApiModel.Proxy:
        ...

    async def send(
        self,
        target: Union[Entity, MessageEvent],
        message: Union[MessageChain, Iterable[Union[MessageComponent, str]],
                       MessageComponent, str],
        quote: Union[bool, int] = False
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

    async def process_request(
        self,
        event: RequestEvent,
        operate: Union[int, RespOperate],
        message: str = ''
    ):
        ...

    async def allow(self, event: RequestEvent, message: str = ''):
        ...

    async def decline(
        self, event: RequestEvent, message: str = '', ban: bool = False
    ):
        ...

    async def ignore(
        self, event: RequestEvent, message: str = '', ban: bool = False
    ):
        ...

    ### 以下为自动生成 ###
    # About

    @type_check_only
    class __AboutProxy():
        async def get(self) -> dict:
            """获取插件信息。"""

        async def __call__(self) -> dict:
            """获取插件信息。"""

    @property
    def about(self) -> __AboutProxy:
        """获取插件信息。"""

    # BotProfile

    @type_check_only
    class __BotProfileProxy():
        async def get(self) -> Profile:
            """获取 Bot 资料。"""

        async def __call__(self) -> Profile:
            """获取 Bot 资料。"""

    @property
    def bot_profile(self) -> __BotProfileProxy:
        """获取 Bot 资料。"""

    # CmdExecute

    @type_check_only
    class __CmdExecuteProxy():
        async def set(
            self, command: Union[MessageChain, Iterable[Union[MessageComponent,
                                                              str]], str]
        ) -> None:
            """执行命令。

            Args:
                command (`Union[MessageChain,Iterable[Union[MessageComponent,str]],str]`): 命令。
            """

        async def __call__(
            self, command: Union[MessageChain, Iterable[Union[MessageComponent,
                                                              str]], str]
        ) -> None:
            """执行命令。

            Args:
                command (`Union[MessageChain,Iterable[Union[MessageComponent,str]],str]`): 命令。
            """

    @property
    def cmd_execute(self) -> __CmdExecuteProxy:
        """执行命令。

            Args:
            command (`Union[MessageChain,Iterable[Union[MessageComponent,str]],str]`): 命令。
            """

    # CmdRegister

    @type_check_only
    class __CmdRegisterProxy():
        async def set(
            self,
            name: str,
            usage: str,
            description: str,
            alias: Union[List[str], None] = None
        ) -> None:
            """注册命令。

            Args:
                name (`str`): 命令名称。
                usage (`str`): 使用说明。
                description (`str`): 命令描述。
                alias (`Union[List[str],None]`): 可选。命令别名，默认值 None。
            """

        async def __call__(
            self,
            name: str,
            usage: str,
            description: str,
            alias: Union[List[str], None] = None
        ) -> None:
            """注册命令。

            Args:
                name (`str`): 命令名称。
                usage (`str`): 使用说明。
                description (`str`): 命令描述。
                alias (`Union[List[str],None]`): 可选。命令别名，默认值 None。
            """

    @property
    def cmd_register(self) -> __CmdRegisterProxy:
        """注册命令。

            Args:
            name (`str`): 命令名称。
            usage (`str`): 使用说明。
            description (`str`): 命令描述。
            alias (`Union[List[str],None]`): 可选。命令别名，默认值 None。
            """

    # DeleteFriend

    @type_check_only
    class __DeleteFriendProxy():
        async def set(self, target: int) -> None:
            """删除好友。

            Args:
                target (`int`): 需要删除的好友 QQ 号。
            """

        async def __call__(self, target: int) -> None:
            """删除好友。

            Args:
                target (`int`): 需要删除的好友 QQ 号。
            """

    @property
    def delete_friend(self) -> __DeleteFriendProxy:
        """删除好友。

            Args:
            target (`int`): 需要删除的好友 QQ 号。
            """

    # FileDelete

    @type_check_only
    class __FileDeleteProxy():
        async def set(
            self, id: str, target: int, path: Union[str, None] = None
        ) -> None:
            """删除文件。

            Args:
                id (`str`): 欲删除的文件 id。
                target (`int`): 群号或好友 QQ 号。
                path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

        async def __call__(
            self, id: str, target: int, path: Union[str, None] = None
        ) -> None:
            """删除文件。

            Args:
                id (`str`): 欲删除的文件 id。
                target (`int`): 群号或好友 QQ 号。
                path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

    @property
    def file_delete(self) -> __FileDeleteProxy:
        """删除文件。

            Args:
            id (`str`): 欲删除的文件 id。
            target (`int`): 群号或好友 QQ 号。
            path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

    # FileInfo

    @type_check_only
    class __FileInfoProxy():
        async def get(
            self,
            id: str,
            target: int,
            with_download_info: Union[bool, None] = None,
            path: Union[str, None] = None
        ) -> FileProperties:
            """查看文件信息。

            Args:
                id (`str`): 文件 id。
                target (`int`): 群号或好友 QQ 号。
                with_download_info (`Union[bool,None]`): 是否携带下载信息，默认值 None。
                path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

        async def __call__(
            self,
            id: str,
            target: int,
            with_download_info: Union[bool, None] = None,
            path: Union[str, None] = None
        ) -> FileProperties:
            """查看文件信息。

            Args:
                id (`str`): 文件 id。
                target (`int`): 群号或好友 QQ 号。
                with_download_info (`Union[bool,None]`): 是否携带下载信息，默认值 None。
                path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

    @property
    def file_info(self) -> __FileInfoProxy:
        """查看文件信息。

            Args:
            id (`str`): 文件 id。
            target (`int`): 群号或好友 QQ 号。
            with_download_info (`Union[bool,None]`): 是否携带下载信息，默认值 None。
            path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

    # FileList

    @type_check_only
    class __FileListProxy():
        async def get(
            self,
            id: str,
            target: int,
            with_download_info: Union[bool, None] = None,
            path: Union[str, None] = None,
            offset: Union[int, None] = None,
            size: Union[int, None] = None
        ) -> FileProperties:
            """查看文件列表。

            Args:
                id (`str`): 文件夹 id，空串为根目录。
                target (`int`): 群号或好友 QQ 号。
                with_download_info (`Union[bool,None]`): 是否携带下载信息，默认值 None。
                path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
                offset (`Union[int,None]`): 可选。分页偏移，默认值 None。
                size (`Union[int,None]`): 可选。分页大小，默认值 None。
            """

        async def __call__(
            self,
            id: str,
            target: int,
            with_download_info: Union[bool, None] = None,
            path: Union[str, None] = None,
            offset: Union[int, None] = None,
            size: Union[int, None] = None
        ) -> FileProperties:
            """查看文件列表。

            Args:
                id (`str`): 文件夹 id，空串为根目录。
                target (`int`): 群号或好友 QQ 号。
                with_download_info (`Union[bool,None]`): 是否携带下载信息，默认值 None。
                path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
                offset (`Union[int,None]`): 可选。分页偏移，默认值 None。
                size (`Union[int,None]`): 可选。分页大小，默认值 None。
            """

    @property
    def file_list(self) -> __FileListProxy:
        """查看文件列表。

            Args:
            id (`str`): 文件夹 id，空串为根目录。
            target (`int`): 群号或好友 QQ 号。
            with_download_info (`Union[bool,None]`): 是否携带下载信息，默认值 None。
            path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            offset (`Union[int,None]`): 可选。分页偏移，默认值 None。
            size (`Union[int,None]`): 可选。分页大小，默认值 None。
            """

    # FileMkdir

    @type_check_only
    class __FileMkdirProxy():
        async def set(
            self,
            id: str,
            target: int,
            directory_name: str,
            path: Union[str, None] = None
        ) -> FileProperties:
            """创建文件夹。

            Args:
                id (`str`): 父目录 id。
                target (`int`): 群号或好友 QQ 号。
                directory_name (`str`): 新建文件夹名。
                path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

        async def __call__(
            self,
            id: str,
            target: int,
            directory_name: str,
            path: Union[str, None] = None
        ) -> FileProperties:
            """创建文件夹。

            Args:
                id (`str`): 父目录 id。
                target (`int`): 群号或好友 QQ 号。
                directory_name (`str`): 新建文件夹名。
                path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

    @property
    def file_mkdir(self) -> __FileMkdirProxy:
        """创建文件夹。

            Args:
            id (`str`): 父目录 id。
            target (`int`): 群号或好友 QQ 号。
            directory_name (`str`): 新建文件夹名。
            path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

    # FileMove

    @type_check_only
    class __FileMoveProxy():
        async def set(
            self,
            id: str,
            target: int,
            move_to: str,
            path: Union[str, None] = None,
            move_to_path: Union[str, None] = None
        ) -> None:
            """移动文件。

            Args:
                id (`str`): 欲移动的文件 id。
                target (`int`): 群号或好友 QQ 号。
                move_to (`str`): 移动目标文件夹 id。
                path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
                move_to_path (`Union[str,None]`): 可选。移动目标文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

        async def __call__(
            self,
            id: str,
            target: int,
            move_to: str,
            path: Union[str, None] = None,
            move_to_path: Union[str, None] = None
        ) -> None:
            """移动文件。

            Args:
                id (`str`): 欲移动的文件 id。
                target (`int`): 群号或好友 QQ 号。
                move_to (`str`): 移动目标文件夹 id。
                path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
                move_to_path (`Union[str,None]`): 可选。移动目标文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

    @property
    def file_move(self) -> __FileMoveProxy:
        """移动文件。

            Args:
            id (`str`): 欲移动的文件 id。
            target (`int`): 群号或好友 QQ 号。
            move_to (`str`): 移动目标文件夹 id。
            path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            move_to_path (`Union[str,None]`): 可选。移动目标文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

    # FileRename

    @type_check_only
    class __FileRenameProxy():
        async def set(
            self,
            id: str,
            target: int,
            rename_to: str,
            path: Union[str, None] = None
        ) -> None:
            """重命名文件。

            Args:
                id (`str`): 欲重命名的文件 id。
                target (`int`): 群号或好友 QQ 号。
                rename_to (`str`): 新文件名。
                path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

        async def __call__(
            self,
            id: str,
            target: int,
            rename_to: str,
            path: Union[str, None] = None
        ) -> None:
            """重命名文件。

            Args:
                id (`str`): 欲重命名的文件 id。
                target (`int`): 群号或好友 QQ 号。
                rename_to (`str`): 新文件名。
                path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

    @property
    def file_rename(self) -> __FileRenameProxy:
        """重命名文件。

            Args:
            id (`str`): 欲重命名的文件 id。
            target (`int`): 群号或好友 QQ 号。
            rename_to (`str`): 新文件名。
            path (`Union[str,None]`): 可选。文件夹路径。文件夹允许重名，不保证准确，准确定位使用 id，默认值 None。
            """

    # FileUpload

    @type_check_only
    class __FileUploadProxy():
        async def set(
            self,
            type: Literal['group'],
            target: int,
            file: Union[str, Path],
            path: str = ''
        ) -> FileProperties:
            """文件上传。

            Args:
                type (`Literal['group']`): 上传的文件类型。
                target (`int`): 群号。
                file (`Union[str,Path]`): 上传的文件的本地路径。
                path (`str`): 上传目录的 id，空串为上传到根目录，默认值 ''。
            """

        async def __call__(
            self,
            type: Literal['group'],
            target: int,
            file: Union[str, Path],
            path: str = ''
        ) -> FileProperties:
            """文件上传。

            Args:
                type (`Literal['group']`): 上传的文件类型。
                target (`int`): 群号。
                file (`Union[str,Path]`): 上传的文件的本地路径。
                path (`str`): 上传目录的 id，空串为上传到根目录，默认值 ''。
            """

    @property
    def file_upload(self) -> __FileUploadProxy:
        """文件上传。

            Args:
            type (`Literal['group']`): 上传的文件类型。
            target (`int`): 群号。
            file (`Union[str,Path]`): 上传的文件的本地路径。
            path (`str`): 上传目录的 id，空串为上传到根目录，默认值 ''。
            """

    # FriendList

    @type_check_only
    class __FriendListProxy():
        async def get(self) -> Friend:
            """获取好友列表。"""

        async def __call__(self) -> Friend:
            """获取好友列表。"""

    @property
    def friend_list(self) -> __FriendListProxy:
        """获取好友列表。"""

    # FriendProfile

    @type_check_only
    class __FriendProfileProxy():
        async def get(self, target: int) -> Profile:
            """获取好友资料。

            Args:
                target (`int`): 好友 QQ 号。
            """

        async def __call__(self, target: int) -> Profile:
            """获取好友资料。

            Args:
                target (`int`): 好友 QQ 号。
            """

    @property
    def friend_profile(self) -> __FriendProfileProxy:
        """获取好友资料。

            Args:
            target (`int`): 好友 QQ 号。
            """

    # GroupConfig

    @type_check_only
    class __GroupConfigProxy():
        async def get(
            self,
            target: int,
            config: Union[GroupConfigModel, None] = None
        ) -> GroupConfigModel:
            """获取或修改群设置。

            Args:
                target (`int`): 群号。
                config (`Union[GroupConfigModel,None]`): 仅修改时可用。群设置，默认值 None。
            """

        async def set(
            self,
            target: int,
            config: Union[GroupConfigModel, None] = None
        ) -> None:
            """获取或修改群设置。

            Args:
                target (`int`): 群号。
                config (`Union[GroupConfigModel,None]`): 仅修改时可用。群设置，默认值 None。
            """

        async def __call__(
            self,
            target: int,
            config: Union[GroupConfigModel, None] = None
        ) -> GroupConfigModel:
            """获取或修改群设置。

            Args:
                target (`int`): 群号。
                config (`Union[GroupConfigModel,None]`): 仅修改时可用。群设置，默认值 None。
            """

    @property
    def group_config(self) -> __GroupConfigProxy:
        """获取或修改群设置。

            Args:
            target (`int`): 群号。
            config (`Union[GroupConfigModel,None]`): 仅修改时可用。群设置，默认值 None。
            """

    # GroupList

    @type_check_only
    class __GroupListProxy():
        async def get(self) -> Group:
            """获取群列表。"""

        async def __call__(self) -> Group:
            """获取群列表。"""

    @property
    def group_list(self) -> __GroupListProxy:
        """获取群列表。"""

    # Kick

    @type_check_only
    class __KickProxy():
        async def set(
            self, target: int, member_id: int, msg: str = ''
        ) -> None:
            """移出群成员。

            Args:
                target (`int`): 指定群的群号。
                member_id (`int`): 指定群成员的 QQ 号。
                msg (`str`): 可选。信息，默认值 ''。
            """

        async def __call__(
            self, target: int, member_id: int, msg: str = ''
        ) -> None:
            """移出群成员。

            Args:
                target (`int`): 指定群的群号。
                member_id (`int`): 指定群成员的 QQ 号。
                msg (`str`): 可选。信息，默认值 ''。
            """

    @property
    def kick(self) -> __KickProxy:
        """移出群成员。

            Args:
            target (`int`): 指定群的群号。
            member_id (`int`): 指定群成员的 QQ 号。
            msg (`str`): 可选。信息，默认值 ''。
            """

    # MemberAdmin

    @type_check_only
    class __MemberAdminProxy():
        async def set(self, target: int, member_id: int, assign: bool) -> None:
            """设置或取消群成员管理员。

            Args:
                target (`int`): 群号。
                member_id (`int`): 指定群成员的 QQ 号。
                assign (`bool`): 是否设置管理员。
            """

        async def __call__(
            self, target: int, member_id: int, assign: bool
        ) -> None:
            """设置或取消群成员管理员。

            Args:
                target (`int`): 群号。
                member_id (`int`): 指定群成员的 QQ 号。
                assign (`bool`): 是否设置管理员。
            """

    @property
    def member_admin(self) -> __MemberAdminProxy:
        """设置或取消群成员管理员。

            Args:
            target (`int`): 群号。
            member_id (`int`): 指定群成员的 QQ 号。
            assign (`bool`): 是否设置管理员。
            """

    # MemberInfo

    @type_check_only
    class __MemberInfoProxy():
        async def get(
            self,
            target: int,
            member_id: int,
            info: Union[MemberInfoModel, None] = None
        ) -> MemberInfoModel:
            """获取或修改群成员资料。

            Args:
                target (`int`): 群号。
                member_id (`int`): 指定群成员的 QQ 号。
                info (`Union[MemberInfoModel,None]`): 仅修改时可用。群成员资料，默认值 None。
            """

        async def set(
            self,
            target: int,
            member_id: int,
            info: Union[MemberInfoModel, None] = None
        ) -> None:
            """获取或修改群成员资料。

            Args:
                target (`int`): 群号。
                member_id (`int`): 指定群成员的 QQ 号。
                info (`Union[MemberInfoModel,None]`): 仅修改时可用。群成员资料，默认值 None。
            """

        async def __call__(
            self,
            target: int,
            member_id: int,
            info: Union[MemberInfoModel, None] = None
        ) -> MemberInfoModel:
            """获取或修改群成员资料。

            Args:
                target (`int`): 群号。
                member_id (`int`): 指定群成员的 QQ 号。
                info (`Union[MemberInfoModel,None]`): 仅修改时可用。群成员资料，默认值 None。
            """

    @property
    def member_info(self) -> __MemberInfoProxy:
        """获取或修改群成员资料。

            Args:
            target (`int`): 群号。
            member_id (`int`): 指定群成员的 QQ 号。
            info (`Union[MemberInfoModel,None]`): 仅修改时可用。群成员资料，默认值 None。
            """

    # MemberList

    @type_check_only
    class __MemberListProxy():
        async def get(self, target: int) -> GroupMember:
            """获取群成员列表。

            Args:
                target (`int`): 指定群的群号。
            """

        async def __call__(self, target: int) -> GroupMember:
            """获取群成员列表。

            Args:
                target (`int`): 指定群的群号。
            """

    @property
    def member_list(self) -> __MemberListProxy:
        """获取群成员列表。

            Args:
            target (`int`): 指定群的群号。
            """

    # MemberProfile

    @type_check_only
    class __MemberProfileProxy():
        async def get(self, target: int, member_id: int) -> Profile:
            """获取群成员资料。

            Args:
                target (`int`): 指定群的群号。
                member_id (`int`): 指定群成员的 QQ 号。
            """

        async def __call__(self, target: int, member_id: int) -> Profile:
            """获取群成员资料。

            Args:
                target (`int`): 指定群的群号。
                member_id (`int`): 指定群成员的 QQ 号。
            """

    @property
    def member_profile(self) -> __MemberProfileProxy:
        """获取群成员资料。

            Args:
            target (`int`): 指定群的群号。
            member_id (`int`): 指定群成员的 QQ 号。
            """

    # MessageFromId

    @type_check_only
    class __MessageFromIdProxy():
        async def get(self, id: int) -> None:
            """通过 message_id 获取消息。

            Args:
                id (`int`): 获取消息的 message_id。
            """

        async def __call__(self, id: int) -> None:
            """通过 message_id 获取消息。

            Args:
                id (`int`): 获取消息的 message_id。
            """

    @property
    def message_from_id(self) -> __MessageFromIdProxy:
        """通过 message_id 获取消息。

            Args:
            id (`int`): 获取消息的 message_id。
            """

    # Mute

    @type_check_only
    class __MuteProxy():
        async def set(self, target: int, member_id: int, time: int) -> None:
            """禁言群成员。

            Args:
                target (`int`): 指定群的群号。
                member_id (`int`): 指定群成员的 QQ 号。
                time (`int`): 禁言时间，单位为秒，最多30天，默认为0。
            """

        async def __call__(
            self, target: int, member_id: int, time: int
        ) -> None:
            """禁言群成员。

            Args:
                target (`int`): 指定群的群号。
                member_id (`int`): 指定群成员的 QQ 号。
                time (`int`): 禁言时间，单位为秒，最多30天，默认为0。
            """

    @property
    def mute(self) -> __MuteProxy:
        """禁言群成员。

            Args:
            target (`int`): 指定群的群号。
            member_id (`int`): 指定群成员的 QQ 号。
            time (`int`): 禁言时间，单位为秒，最多30天，默认为0。
            """

    # MuteAll

    @type_check_only
    class __MuteAllProxy():
        async def set(self, target: int) -> None:
            """全体禁言。

            Args:
                target (`int`): 指定群的群号。
            """

        async def __call__(self, target: int) -> None:
            """全体禁言。

            Args:
                target (`int`): 指定群的群号。
            """

    @property
    def mute_all(self) -> __MuteAllProxy:
        """全体禁言。

            Args:
            target (`int`): 指定群的群号。
            """

    # Quit

    @type_check_only
    class __QuitProxy():
        async def set(self, target: int) -> None:
            """退出群聊。

            Args:
                target (`int`): 指定群的群号。
            """

        async def __call__(self, target: int) -> None:
            """退出群聊。

            Args:
                target (`int`): 指定群的群号。
            """

    @property
    def quit(self) -> __QuitProxy:
        """退出群聊。

            Args:
            target (`int`): 指定群的群号。
            """

    # Recall

    @type_check_only
    class __RecallProxy():
        async def set(self, target: int) -> None:
            """撤回消息。

            Args:
                target (`int`): 需要撤回的消息的 message_id。
            """

        async def __call__(self, target: int) -> None:
            """撤回消息。

            Args:
                target (`int`): 需要撤回的消息的 message_id。
            """

    @property
    def recall(self) -> __RecallProxy:
        """撤回消息。

            Args:
            target (`int`): 需要撤回的消息的 message_id。
            """

    # RespBotInvitedJoinGroupRequestEvent

    @type_check_only
    class __RespBotInvitedJoinGroupRequestEventProxy():
        async def set(
            self, event_id: int, from_id: int, group_id: int,
            operate: Union[int, RespOperate], message: str
        ) -> None:
            """响应被邀请入群申请。

            Args:
                event_id (`int`): 响应申请事件的标识。
                from_id (`int`): 事件对应申请人 QQ 号。
                group_id (`int`): 事件对应申请人的群号，可能为0。
                operate (`Union[int,RespOperate]`): 响应的操作类型。
                message (`str`): 回复的信息。
            """

        async def __call__(
            self, event_id: int, from_id: int, group_id: int,
            operate: Union[int, RespOperate], message: str
        ) -> None:
            """响应被邀请入群申请。

            Args:
                event_id (`int`): 响应申请事件的标识。
                from_id (`int`): 事件对应申请人 QQ 号。
                group_id (`int`): 事件对应申请人的群号，可能为0。
                operate (`Union[int,RespOperate]`): 响应的操作类型。
                message (`str`): 回复的信息。
            """

    @property
    def resp_bot_invited_join_group_request_event(
        self
    ) -> __RespBotInvitedJoinGroupRequestEventProxy:
        """响应被邀请入群申请。

            Args:
            event_id (`int`): 响应申请事件的标识。
            from_id (`int`): 事件对应申请人 QQ 号。
            group_id (`int`): 事件对应申请人的群号，可能为0。
            operate (`Union[int,RespOperate]`): 响应的操作类型。
            message (`str`): 回复的信息。
            """

    # RespMemberJoinRequestEvent

    @type_check_only
    class __RespMemberJoinRequestEventProxy():
        async def set(
            self, event_id: int, from_id: int, group_id: int,
            operate: Union[int, RespOperate], message: str
        ) -> None:
            """响应用户入群申请。

            Args:
                event_id (`int`): 响应申请事件的标识。
                from_id (`int`): 事件对应申请人 QQ 号。
                group_id (`int`): 事件对应申请人的群号。
                operate (`Union[int,RespOperate]`): 响应的操作类型。
                message (`str`): 回复的信息。
            """

        async def __call__(
            self, event_id: int, from_id: int, group_id: int,
            operate: Union[int, RespOperate], message: str
        ) -> None:
            """响应用户入群申请。

            Args:
                event_id (`int`): 响应申请事件的标识。
                from_id (`int`): 事件对应申请人 QQ 号。
                group_id (`int`): 事件对应申请人的群号。
                operate (`Union[int,RespOperate]`): 响应的操作类型。
                message (`str`): 回复的信息。
            """

    @property
    def resp_member_join_request_event(
        self
    ) -> __RespMemberJoinRequestEventProxy:
        """响应用户入群申请。

            Args:
            event_id (`int`): 响应申请事件的标识。
            from_id (`int`): 事件对应申请人 QQ 号。
            group_id (`int`): 事件对应申请人的群号。
            operate (`Union[int,RespOperate]`): 响应的操作类型。
            message (`str`): 回复的信息。
            """

    # RespNewFriendRequestEvent

    @type_check_only
    class __RespNewFriendRequestEventProxy():
        async def set(
            self, event_id: int, from_id: int, group_id: int,
            operate: Union[int, RespOperate], message: str
        ) -> None:
            """响应添加好友申请。

            Args:
                event_id (`int`): 响应申请事件的标识。
                from_id (`int`): 事件对应申请人 QQ 号。
                group_id (`int`): 事件对应申请人的群号，可能为0。
                operate (`Union[int,RespOperate]`): 响应的操作类型。
                message (`str`): 回复的信息。
            """

        async def __call__(
            self, event_id: int, from_id: int, group_id: int,
            operate: Union[int, RespOperate], message: str
        ) -> None:
            """响应添加好友申请。

            Args:
                event_id (`int`): 响应申请事件的标识。
                from_id (`int`): 事件对应申请人 QQ 号。
                group_id (`int`): 事件对应申请人的群号，可能为0。
                operate (`Union[int,RespOperate]`): 响应的操作类型。
                message (`str`): 回复的信息。
            """

    @property
    def resp_new_friend_request_event(
        self
    ) -> __RespNewFriendRequestEventProxy:
        """响应添加好友申请。

            Args:
            event_id (`int`): 响应申请事件的标识。
            from_id (`int`): 事件对应申请人 QQ 号。
            group_id (`int`): 事件对应申请人的群号，可能为0。
            operate (`Union[int,RespOperate]`): 响应的操作类型。
            message (`str`): 回复的信息。
            """

    # SendFriendMessage

    @type_check_only
    class __SendFriendMessageProxy():
        async def set(
            self,
            target: int,
            message_chain: Union[MessageChain, Iterable[Union[MessageComponent,
                                                              str]],
                                 MessageComponent, str],
            quote: Union[int, None] = None
        ) -> int:
            """发送好友消息。

            Args:
                target (`int`): 发送消息目标好友的 QQ 号。
                message_chain (`Union[MessageChain,Iterable[Union[MessageComponent,str]],MessageComponent,str]`): 消息链。
                quote (`Union[int,None]`): 可选。引用一条消息的 message_id 进行回复，默认值 None。
            """

        async def __call__(
            self,
            target: int,
            message_chain: Union[MessageChain, Iterable[Union[MessageComponent,
                                                              str]],
                                 MessageComponent, str],
            quote: Union[int, None] = None
        ) -> int:
            """发送好友消息。

            Args:
                target (`int`): 发送消息目标好友的 QQ 号。
                message_chain (`Union[MessageChain,Iterable[Union[MessageComponent,str]],MessageComponent,str]`): 消息链。
                quote (`Union[int,None]`): 可选。引用一条消息的 message_id 进行回复，默认值 None。
            """

    @property
    def send_friend_message(self) -> __SendFriendMessageProxy:
        """发送好友消息。

            Args:
            target (`int`): 发送消息目标好友的 QQ 号。
            message_chain (`Union[MessageChain,Iterable[Union[MessageComponent,str]],MessageComponent,str]`): 消息链。
            quote (`Union[int,None]`): 可选。引用一条消息的 message_id 进行回复，默认值 None。
            """

    # SendGroupMessage

    @type_check_only
    class __SendGroupMessageProxy():
        async def set(
            self,
            target: int,
            message_chain: Union[MessageChain, Iterable[Union[MessageComponent,
                                                              str]],
                                 MessageComponent, str],
            quote: Union[int, None] = None
        ) -> int:
            """发送群消息。

            Args:
                target (`int`): 发送消息目标群的群号。
                message_chain (`Union[MessageChain,Iterable[Union[MessageComponent,str]],MessageComponent,str]`): 消息链。
                quote (`Union[int,None]`): 可选。引用一条消息的 message_id 进行回复，默认值 None。
            """

        async def __call__(
            self,
            target: int,
            message_chain: Union[MessageChain, Iterable[Union[MessageComponent,
                                                              str]],
                                 MessageComponent, str],
            quote: Union[int, None] = None
        ) -> int:
            """发送群消息。

            Args:
                target (`int`): 发送消息目标群的群号。
                message_chain (`Union[MessageChain,Iterable[Union[MessageComponent,str]],MessageComponent,str]`): 消息链。
                quote (`Union[int,None]`): 可选。引用一条消息的 message_id 进行回复，默认值 None。
            """

    @property
    def send_group_message(self) -> __SendGroupMessageProxy:
        """发送群消息。

            Args:
            target (`int`): 发送消息目标群的群号。
            message_chain (`Union[MessageChain,Iterable[Union[MessageComponent,str]],MessageComponent,str]`): 消息链。
            quote (`Union[int,None]`): 可选。引用一条消息的 message_id 进行回复，默认值 None。
            """

    # SendNudge

    @type_check_only
    class __SendNudgeProxy():
        async def set(
            self, target: int, subject: int, kind: Literal['Friend', 'Group',
                                                           'Stranger']
        ) -> None:
            """发送头像戳一戳消息。

            Args:
                target (`int`): 戳一戳的目标 QQ 号，可以为 bot QQ 号。
                subject (`int`): 戳一戳接受主体（上下文），戳一戳信息会发送至该主体，为群号或好友 QQ 号。
                kind (`Literal['Friend','Group','Stranger']`): 上下文类型，可选值 `Friend`, `Group`, `Stranger`。
            """

        async def __call__(
            self, target: int, subject: int, kind: Literal['Friend', 'Group',
                                                           'Stranger']
        ) -> None:
            """发送头像戳一戳消息。

            Args:
                target (`int`): 戳一戳的目标 QQ 号，可以为 bot QQ 号。
                subject (`int`): 戳一戳接受主体（上下文），戳一戳信息会发送至该主体，为群号或好友 QQ 号。
                kind (`Literal['Friend','Group','Stranger']`): 上下文类型，可选值 `Friend`, `Group`, `Stranger`。
            """

    @property
    def send_nudge(self) -> __SendNudgeProxy:
        """发送头像戳一戳消息。

            Args:
            target (`int`): 戳一戳的目标 QQ 号，可以为 bot QQ 号。
            subject (`int`): 戳一戳接受主体（上下文），戳一戳信息会发送至该主体，为群号或好友 QQ 号。
            kind (`Literal['Friend','Group','Stranger']`): 上下文类型，可选值 `Friend`, `Group`, `Stranger`。
            """

    # SendTempMessage

    @type_check_only
    class __SendTempMessageProxy():
        async def set(
            self,
            qq: int,
            group: int,
            message_chain: Union[MessageChain, Iterable[Union[MessageComponent,
                                                              str]],
                                 MessageComponent, str],
            quote: Union[int, None] = None
        ) -> int:
            """发送临时消息。

            Args:
                qq (`int`): 临时会话对象 QQ 号。
                group (`int`): 临时会话对象群号。
                message_chain (`Union[MessageChain,Iterable[Union[MessageComponent,str]],MessageComponent,str]`): 消息链。
                quote (`Union[int,None]`): 可选。引用一条消息的 message_id 进行回复，默认值 None。
            """

        async def __call__(
            self,
            qq: int,
            group: int,
            message_chain: Union[MessageChain, Iterable[Union[MessageComponent,
                                                              str]],
                                 MessageComponent, str],
            quote: Union[int, None] = None
        ) -> int:
            """发送临时消息。

            Args:
                qq (`int`): 临时会话对象 QQ 号。
                group (`int`): 临时会话对象群号。
                message_chain (`Union[MessageChain,Iterable[Union[MessageComponent,str]],MessageComponent,str]`): 消息链。
                quote (`Union[int,None]`): 可选。引用一条消息的 message_id 进行回复，默认值 None。
            """

    @property
    def send_temp_message(self) -> __SendTempMessageProxy:
        """发送临时消息。

            Args:
            qq (`int`): 临时会话对象 QQ 号。
            group (`int`): 临时会话对象群号。
            message_chain (`Union[MessageChain,Iterable[Union[MessageComponent,str]],MessageComponent,str]`): 消息链。
            quote (`Union[int,None]`): 可选。引用一条消息的 message_id 进行回复，默认值 None。
            """

    # SessionInfo

    @type_check_only
    class __SessionInfoProxy():
        async def get(self) -> SessionInfo.Response.Data:
            """获取机器人信息。"""

        async def __call__(self) -> SessionInfo.Response.Data:
            """获取机器人信息。"""

    @property
    def session_info(self) -> __SessionInfoProxy:
        """获取机器人信息。"""

    # SetEssence

    @type_check_only
    class __SetEssenceProxy():
        async def set(self, target: int) -> None:
            """设置群精华消息。

            Args:
                target (`int`): 精华消息的 message_id。
            """

        async def __call__(self, target: int) -> None:
            """设置群精华消息。

            Args:
                target (`int`): 精华消息的 message_id。
            """

    @property
    def set_essence(self) -> __SetEssenceProxy:
        """设置群精华消息。

            Args:
            target (`int`): 精华消息的 message_id。
            """

    # Unmute

    @type_check_only
    class __UnmuteProxy():
        async def set(self, target: int, member_id: int) -> None:
            """解除群成员禁言。

            Args:
                target (`int`): 指定群的群号。
                member_id (`int`): 指定群成员的 QQ 号。
            """

        async def __call__(self, target: int, member_id: int) -> None:
            """解除群成员禁言。

            Args:
                target (`int`): 指定群的群号。
                member_id (`int`): 指定群成员的 QQ 号。
            """

    @property
    def unmute(self) -> __UnmuteProxy:
        """解除群成员禁言。

            Args:
            target (`int`): 指定群的群号。
            member_id (`int`): 指定群成员的 QQ 号。
            """

    # UnmuteAll

    @type_check_only
    class __UnmuteAllProxy():
        async def set(self, target: int) -> None:
            """解除全体禁言。

            Args:
                target (`int`): 指定群的群号。
            """

        async def __call__(self, target: int) -> None:
            """解除全体禁言。

            Args:
                target (`int`): 指定群的群号。
            """

    @property
    def unmute_all(self) -> __UnmuteAllProxy:
        """解除全体禁言。

            Args:
            target (`int`): 指定群的群号。
            """

    # UploadImage

    @type_check_only
    class __UploadImageProxy():
        async def set(
            self, type: Literal['friend', 'group', 'temp'], img: Union[str,
                                                                       Path]
        ) -> Image:
            """图片文件上传。

            Args:
                type (`Literal['friend','group','temp']`): 上传的图片类型。
                img (`Union[str,Path]`): 上传的图片的本地路径。
            """

        async def __call__(
            self, type: Literal['friend', 'group', 'temp'], img: Union[str,
                                                                       Path]
        ) -> Image:
            """图片文件上传。

            Args:
                type (`Literal['friend','group','temp']`): 上传的图片类型。
                img (`Union[str,Path]`): 上传的图片的本地路径。
            """

    @property
    def upload_image(self) -> __UploadImageProxy:
        """图片文件上传。

            Args:
            type (`Literal['friend','group','temp']`): 上传的图片类型。
            img (`Union[str,Path]`): 上传的图片的本地路径。
            """

    # UploadVoice

    @type_check_only
    class __UploadVoiceProxy():
        async def set(
            self, type: Literal['group', 'friend', 'temp'], voice: Union[str,
                                                                         Path]
        ) -> Voice:
            """语音文件上传。

            Args:
                type (`Literal['group','friend','temp']`): 上传的语音类型。
                voice (`Union[str,Path]`): 上传的语音的本地路径。
            """

        async def __call__(
            self, type: Literal['group', 'friend', 'temp'], voice: Union[str,
                                                                         Path]
        ) -> Voice:
            """语音文件上传。

            Args:
                type (`Literal['group','friend','temp']`): 上传的语音类型。
                voice (`Union[str,Path]`): 上传的语音的本地路径。
            """

    @property
    def upload_voice(self) -> __UploadVoiceProxy:
        """语音文件上传。

            Args:
            type (`Literal['group','friend','temp']`): 上传的语音类型。
            voice (`Union[str,Path]`): 上传的语音的本地路径。
            """
