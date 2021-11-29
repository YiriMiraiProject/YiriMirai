# -*- coding: utf-8 -*-
"""
此模块定义机器人类，包含处于 model 层之下的 `SimpleMirai` 和建立在 model 层上的 `Mirai`。
"""
import asyncio
import contextlib
import logging
from typing import (
    Any, Awaitable, Callable, Dict, Iterable, List, Optional, Type, Union, cast
)

from mirai.adapters.base import Adapter, AdapterInterface
from mirai.api_provider import ApiProvider, Method
from mirai.asgi import ASGI, asgi_serve
from mirai.bus import AbstractEventBus
from mirai.models.api import ApiModel
from mirai.models.api_impl import RespEvent
from mirai.models.bus import ModelEventBus
from mirai.models.entities import (
    Entity, Friend, Group, GroupMember, Permission, RespOperate, Subject
)
from mirai.models.events import Event, MessageEvent, RequestEvent, TempMessage
from mirai.models.message import TMessage
from mirai.utils import Singleton

__all__ = ['Mirai', 'MiraiRunner', 'LifeSpan', 'Startup', 'Shutdown']


class Mirai(ApiProvider, AdapterInterface, AbstractEventBus):
    """
    机器人主类。

    使用了 `__getattr__` 魔术方法，可以直接在对象上调用 API。

    `Mirai` 类包含 model 层封装，API 名称经过转写以符合命名规范，所有的 API 全部使用小写字母及下划线命名。
    （API 名称也可使用原名。）
    API 参数可以使用具名参数，也可以使用位置参数，关于 API 参数的更多信息请参见模块 `mirai.models.api`。

    例如：
    ```py
    await bot.send_friend_message(12345678, [
        Plain("Hello World!")
    ])
    ```

    也可以使用 `call_api` 方法，此时 API 名称与参数名称需与 mirai-api-http 中的定义相同，
    参数需要全部以具名参数的形式给出，并且需要指明使用的方法（GET/POST）。

    例如：
    ```py
    await bot.call_api("sendFriendMessage", target=12345678, messageChain=[
        {"type": "Plain", "text": "Hello World!"}
    ], method="POST")

    file_list = await bot.call_api(
        "file/list", id="", target=12345678, method="GET"
    )
    ```
    """
    qq: int

    def __init__(self, qq: int, adapter: Adapter):
        """
        Args:
            qq: QQ 号。启用 Single Mode 时，可以随便传入，登陆后会自动获取正确的 QQ 号。
            adapter: 适配器，负责与 mirai-api-http 沟通，详见模块`mirai.adapters。
        """
        self.qq = qq
        self._adapter = adapter
        self._bus = ModelEventBus()
        adapter.register_event_bus(self._bus.base_bus)

    @property
    def bus(self) -> ModelEventBus:
        return self._bus

    def subscribe(self, event, func: Callable, priority: int = 0) -> None:
        self._bus.subscribe(event, func, priority)

    def unsubscribe(self, event, func: Callable) -> None:
        self._bus.unsubscribe(event, func)

    async def emit(self, event, *args, **kwargs) -> List[Awaitable[Any]]:
        return await self._bus.emit(event, *args, **kwargs)

    async def call_api(self, api: str, *args, **kwargs):
        """调用 API。

        Args:
            api: API 名称。
            *args: 参数。
            **kwargs: 参数。
        """
        return await self._adapter.call_api(api, *args, **kwargs)

    @property
    def adapter_info(self) -> Dict[str, Any]:
        return self._adapter.adapter_info

    @contextlib.asynccontextmanager
    async def use_adapter(self, adapter: Adapter):
        """临时使用另一个适配器。

        用法：
        ```py
        async with bot.use_adapter(HTTPAdapter.via(bot)):
            ...
        ```

        Args:
            adapter: 使用的适配器。
        """
        origin_adapter = self._adapter
        await adapter.login(self.qq)
        self._adapter = adapter
        yield
        self._adapter = origin_adapter
        await adapter.logout(False)

    async def startup(self):
        """开始运行机器人（立即返回）。"""
        await self._adapter.login(self.qq)

        if self._adapter.single_mode:
            # Single Mode 下，QQ 号可以随便传入。这里从 session info 中获取正确的 QQ 号。
            session_info = await self.session_info.get()
            if session_info:
                self.qq = session_info.qq.id

        asyncio.create_task(self._adapter.emit("Startup", {'type': 'Startup'}))
        await self._adapter.start()

    async def background(self):
        """等待背景任务完成。"""
        if self._adapter.background:
            await self._adapter.background

    async def shutdown(self):
        """结束运行机器人。"""
        await asyncio.create_task(
            self._adapter.emit("Shutdown", {'type': 'Shutdown'})
        )
        await self._adapter.logout()
        await self._adapter.shutdown()

    @property
    def session(self) -> str:
        """获取 session key，可用于调试。

        Returns:
            str: session key。
        """
        return self._adapter.session

    @property
    def asgi(self) -> 'MiraiRunner':
        """ASGI 对象，用于使用 uvicorn 等启动。"""
        return MiraiRunner(self)

    @staticmethod
    def add_background_task(func: Union[Callable, Awaitable, None] = None):
        """注册背景任务，将在 bot 启动后自动运行。

        Args:
            func(`Union[Callable, Awaitable, None]`): 背景任务，可以是函数或者协程，省略参数以作为装饰器调用。
        """
        asgi = ASGI()
        return asgi.add_background_task(func)

    def run(
        self,
        host: str = '127.0.0.1',
        port: int = 8000,
        asgi_server: str = 'auto',
        **kwargs
    ):
        """开始运行机器人。

        一般情况下，此函数会进入主循环，不再返回。

        Args:
            host: YiriMirai 作为服务器的地址，默认为 127.0.0.1。
            port: YiriMirai 作为服务器的端口，默认为 8000。
            asgi_server: ASGI 服务器类型，可选项有 `'uvicorn'` `'hypercorn'` 和 `'auto'`。
            **kwargs: 可选参数。多余的参数将传递给 `uvicorn.run` 和 `hypercorn.run`。
        """
        MiraiRunner(self).run(host, port, asgi_server, **kwargs)

    def on(
        self,
        event: Union[Type[Event], str],
        priority: int = 0,
    ) -> Callable:
        """注册事件处理器。

        用法举例：
        ```python
        @bot.on(FriendMessage)
        async def on_friend_message(event: FriendMessage):
            print(f"收到来自{event.sender.nickname}的消息。")
        ```

        Args:
            event: 事件类或事件名。
            priority: 优先级，较小者优先。
        """
        return self._bus.on(event, priority)

    def api(self, api: str) -> ApiModel.Proxy:
        """获取 API Proxy 对象。

        API Proxy 提供更加简便的调用 API 的写法，详见 `mirai.models.api`。

        `Mirai` 的 `__getattr__` 与此方法完全相同，可支持直接在对象上调用 API。

        Args:
            api: API 名称。

        Returns:
            ApiModel.Proxy: API Proxy 对象。
        """
        api_type = ApiModel.get_subtype(api)
        return api_type.Proxy(self, api_type)

    def __getattr__(self, api: str) -> ApiModel.Proxy:
        return self.api(api)

    async def send(
        self,
        target: Union[Entity, MessageEvent],
        message: TMessage,
        quote: Union[bool, int] = False
    ) -> int:
        """发送消息。可以从 `Friend` `Group` 等对象，或者从 `MessageEvent` 中自动识别消息发送对象。

        Args:
            target(`Union[Entity, MessageEvent]`): 目标对象。
            message(`TMessage`): 发送的消息。
            quote(`Union[bool, int]`): 需要回复的消息的 message_id，或者传入 True 以自动回复 target 对应的消息。

        Returns:
            int: 发送的消息的 message_id。
        """
        quoting = quote if quote is not True and quote is not False else None
        # 识别消息发送对象
        if isinstance(target, TempMessage):
            if quote is True and quoting is None:
                quoting = target.message_chain.message_id
            return (
                await self.send_temp_message(
                    qq=target.sender.id,
                    group=target.group.id,
                    message_chain=message,
                    quote=quoting
                ) or -1
            )

        if isinstance(target, MessageEvent):
            if quote is True and quoting is None:
                quoting = target.message_chain.message_id
            target = target.sender

        if isinstance(target, Friend):
            send_message = self.send_friend_message
            id_ = target.id
        elif isinstance(target, Group):
            send_message = self.send_group_message
            id_ = target.id
        elif isinstance(target, GroupMember):
            send_message = self.send_group_message
            id_ = target.group.id
        else:
            raise ValueError(f"{target} 不是有效的消息发送对象。")

        response = await send_message(
            target=id_, message_chain=message, quote=quoting
        )

        return response or -1

    async def get_friend(self, id_: int) -> Optional[Friend]:
        """获取好友对象。

        Args:
            id_: 好友 QQ 号。

        Returns:
            Friend: 好友对象。
            None: 好友不存在。
        """
        friend_list = await self.friend_list.get()
        if not friend_list:
            return None
        for friend in cast(List[Friend], friend_list):
            if friend.id == id_:
                return friend
        return None

    async def get_group(self, id_: int) -> Optional[Group]:
        """获取群组对象。

        Args:
            id_: 群号。

        Returns:
            Group: 群组对象。
            None: 群组不存在或 bot 未入群。
        """
        group_list = await self.group_list.get()
        if not group_list:
            return None
        for group in cast(List[Group], group_list):
            if group.id == id_:
                return group
        return None

    async def get_group_member(self, group: Union[Group, int],
                               id_: int) -> Optional[GroupMember]:
        """获取群成员对象。

        Args:
            group: 群组对象或群号。
            id_: 群成员 QQ 号。

        Returns:
            GroupMember: 群成员对象。
            None: 群成员不存在。
        """
        if isinstance(group, Group):
            group = group.id
        member_list = await self.member_list.get(group)
        if not member_list:
            return None
        for member in cast(List[GroupMember], member_list):
            if member.id == id_:
                return member
        return None

    async def get_entity(self, subject: Subject) -> Optional[Entity]:
        """获取实体对象。

        Args:
            subject: 以 `Subject` 表示的实体对象。

        Returns:
            Entity: 实体对象。
            None: 实体不存在。
        """
        if subject.kind == 'Friend':
            return await self.get_friend(subject.id)
        if subject.kind == 'Group':
            return await self.get_group(subject.id)
        return None

    @staticmethod
    async def is_admin(group: Group) -> bool:
        """判断机器人在群组中是否是管理员。

        Args:
            group: 群组对象。

        Returns:
            bool: 是否是管理员。
        """
        return group.permission in (Permission.Administrator, Permission.Owner)

    async def process_request(
        self,
        event: RequestEvent,
        operate: Union[int, RespOperate],
        message: str = ''
    ):
        """处理申请。

        Args:
            event: 申请事件。
            operate: 处理操作。
            message: 回复的信息。
        """
        api_type = cast(RespEvent, ApiModel.get_subtype('Resp' + event.type))
        api = api_type.from_event(event, operate, message)
        await api.call(self, Method.POST)

    async def allow(self, event: RequestEvent, message: str = ''):
        """允许申请。

        Args:
            event: 申请事件。
            message: 回复的信息。
        """
        await self.process_request(event, RespOperate.ALLOW, message)

    async def decline(
        self, event: RequestEvent, message: str = '', ban: bool = False
    ):
        """拒绝申请。

        Args:
            event: 申请事件。
            message: 回复的信息。
            ban: 是否拉黑，默认为 False。
        """
        await self.process_request(
            event, RespOperate.DECLINE
            & RespOperate.BAN if ban else RespOperate.DECLINE, message
        )

    async def ignore(
        self, event: RequestEvent, message: str = '', ban: bool = False
    ):
        """忽略申请。

        Args:
            event: 申请事件。
            message: 回复的信息。
            ban: 是否拉黑，默认为 False。
        """
        await self.process_request(
            event, RespOperate.IGNORE
            & RespOperate.BAN if ban else RespOperate.DECLINE, message
        )


class MiraiRunner(Singleton):
    """运行 SimpleMirai 对象的托管类。

    使用此类以实现机器人的多例运行。

    例如:
    ```py
    runner = MiraiRunner(mirai)
    runner.run(host='127.0.0.1', port=8000)
    ```
    """
    bots: Iterable[Mirai]
    """运行的 SimpleMirai 对象。"""
    def __init__(self, *bots: Mirai):
        """
        Args:
            *bots: 要运行的机器人。
        """
        self.bots = bots
        self._asgi = ASGI()
        self._asgi.add_event_handler('startup', self.startup)
        self._asgi.add_event_handler('shutdown', self.shutdown)

    async def startup(self):
        """开始运行。"""
        coros = [bot.startup() for bot in self.bots]
        await asyncio.gather(*coros)

    async def shutdown(self):
        """结束运行。"""
        coros = [bot.shutdown() for bot in self.bots]
        await asyncio.gather(*coros)

    async def __call__(self, scope, recv, send):
        await self._asgi(scope, recv, send)

    async def _run(self):
        try:
            await self.startup()
            backgrounds = [bot.background() for bot in self.bots]
            await asyncio.gather(*backgrounds)
        finally:
            await self.shutdown()

    def run(
        self,
        host: str = '127.0.0.1',
        port: int = 8000,
        asgi_server: str = 'auto',
        **kwargs
    ):
        """开始运行机器人。

        一般情况下，此函数会进入主循环，不再返回。
        """
        if not asgi_serve(
            self, host=host, port=port, asgi_server=asgi_server, **kwargs
        ):
            import textwrap
            logger = logging.getLogger(__name__)
            logger.warning(
                textwrap.dedent(
                    """
                    未找到可用的 ASGI 服务，反向 WebSocket 和 WebHook 上报将不可用。
                    仅 HTTP 轮询与正向 WebSocket 可用。
                    建议安装 ASGI 服务器，如 `uvicorn` 或 `hypercorn`。
                    在命令行键入：
                        pip install uvicorn
                    或者
                        pip install hypercorn
                    """
                ).strip()
            )
            try:
                asyncio.run(self._run())
            except (KeyboardInterrupt, SystemExit):
                pass


class LifeSpan(Event):
    """生命周期事件。"""
    type: str = 'LifeSpan'
    """事件名。"""


class Startup(LifeSpan):
    """启动事件。"""
    type: str = 'Startup'
    """事件名。"""


class Shutdown(LifeSpan):
    """关闭事件。"""
    type: str = 'Shutdown'
    """事件名。"""
