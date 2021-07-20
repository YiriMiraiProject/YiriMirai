# -*- coding: utf-8 -*-
"""
此模块定义机器人类，包含处于 model 层之下的 `SimpleMirai` 和建立在 model 层上的 `Mirai`。
"""
import asyncio
import contextlib
import logging
import sys
from typing import Callable, List, Optional, Type, Union

from mirai.adapters.base import Adapter, AdapterInterface, ApiProvider
from mirai.asgi import ASGI, asgi_serve
from mirai.bus import EventBus
from mirai.models.api import ApiModel, MessageResponse
from mirai.models.bus import ModelEventBus
from mirai.models.entities import (
    Entity, Friend, Group, GroupMember, Permission, Subject
)
from mirai.models.events import Event, MessageEvent, TempMessage
from mirai.models.message import MessageChain, MessageComponent
from mirai.utils import Singleton, async_

__all__ = [
    'Mirai', 'SimpleMirai', 'MiraiRunner', 'LifeSpan', 'Startup', 'Shutdown'
]


class SimpleMirai(ApiProvider, AdapterInterface):
    """
    基于 adapter 和 bus，处于 model 层之下的机器人类。

    使用了 `__getattr__` 魔术方法，可以直接在对象上调用 API。

    通过 `SimpleMirai` 调用 API 时，需注意此类不含 model 层封装，因此 API 名称与参数名称需与 mirai-api-http 中的定义相同，
    参数需要全部以具名参数的形式给出，并且需要指明使用的方法（GET/POST）。

    例如：
    ```py
    await bot.sendFriendMessage(target=12345678, messageChain=[
        {"type": "Plain", "text": "Hello World!"}
    ], method="POST")
    ```

    也可以使用 `call_api` 方法。

    对于名称的路由含有二级目录的 API，由于名称中含有斜杠，必须使用 `call_api` 调用，例如：
    ```py
    file_list = await bot.call_api("file/list", id="", target=12345678, method="GET")
    ```
    """
    def __init__(self, qq: int, adapter: Adapter):
        """
        `qq: int` QQ 号。启用 Single Mode 时，可以随便传入，登陆后会自动获取正确的 QQ 号。

        `adapter: Adapter` 适配器，负责与 mirai-api-http 沟通，详见模块`mirai.adapters`。

        `name: str = ''` 机器人名称，此名称将用作。
        """
        self.qq = qq

        self._adapter = adapter
        self._bus = EventBus()
        self._adapter.register_event_bus(self._bus)

        self.logger = logging.getLogger(__name__)

    async def call_api(self, api: str, **params):
        """调用 API。

        `api: str` API 名称。

        `**params` 参数。
        """
        return await async_(self._adapter.call_api(api, **params))

    def on(self, event: str, priority: int = 0) -> Callable:
        """注册事件处理器。

        `event: str` 事件名。

        `priority: int = 0` 优先级，较小者优先。

        用法举例：
        ```py
        @bot.on('FriendMessage')
        async def on_friend_message(event: dict):
            print(f"收到来自{event['sender']['nickname']}的消息。")
        ```
        """
        return self._bus.on(event, priority=priority)

    @property
    def adapter_info(self):
        return self._adapter.adapter_info

    @contextlib.asynccontextmanager
    async def use_adapter(self, adapter: Adapter):
        """临时使用另一个适配器。

        `adapter: Adapter` 使用的适配器。

        用法：
        ```py
        async with bot.use_adapter(HTTPAdapter.via(bot)):
            ...
        ```
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
            self.qq = (await self.session_info.get()).qq

        await self._adapter.emit("Startup", {'type': 'Startup'})
        self._adapter.start()

    async def background(self):
        """等待背景任务完成。"""
        await self._adapter.background

    async def shutdown(self):
        """结束运行机器人。"""
        await self._adapter.logout()
        await self._adapter.emit("Shutdown", {'type': 'Shutdown'})
        self._adapter.shutdown()

    @property
    def asgi(self):
        return MiraiRunner(self)

    def run(
        self,
        host: str = '127.0.0.1',
        port: int = 8000,
        asgi_server: str = 'auto',
        **kwargs
    ):
        """开始运行机器人。

        一般情况下，此函数会进入主循环，不再返回。

        `host: str = '127.0.0.1'` YiriMirai 作为服务器的地址。

        `port: int = 8000` YiriMirai 作为服务器的端口。

        `asgi_server: str = 'auto'` ASGI 服务器类型，可选项有 `'uvicorn'` `'hypercorn'` 和 `'auto'`。

        `**kwargs` 可选参数。多余的参数将传递给 `uvicorn.run` 和 `hypercorn.run`。
        """
        MiraiRunner(self).run(host, port, asgi_server, **kwargs)


class MiraiRunner(Singleton):
    """运行 SimpleMirai 对象的托管类。

    使用此类以实现机器人的多例运行。

    例如:
    ```py
    runner = MiraiRunner(mirai)
    runner.run(host='127.0.0.1', port=8000)
    ```
    """
    _created = None
    bots: List[SimpleMirai]
    """运行的 SimpleMirai 对象。"""
    def __init__(self, *bots: SimpleMirai):
        """
        `*bots: SimpleMirai` 要运行的机器人。
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
            except KeyboardInterrupt:
                sys.exit(0)


class Mirai(SimpleMirai):
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

    也可以使用 `call_api` 方法，须注意此方法直接继承自 `SimpleMirai`，因此未经 model 层封装，
    需要遵循 `SimpleMirai` 的规定。
    """
    def __init__(self, qq: int, adapter: Adapter):
        super().__init__(qq=qq, adapter=adapter)
        # 将 bus 更换为 ModelEventBus
        adapter.unregister_event_bus(self._bus)
        self._bus = ModelEventBus()
        adapter.register_event_bus(self._bus.base_bus)

    def on(
        self,
        event_type: Union[Type[Event], str],
    ) -> Callable:
        """注册事件处理器。

        `event_type: Union[Type[Event], str]` 事件类或事件名。

        `priority: int = 0` 优先级，较小者优先。

        用法举例：
        ```python
        @bot.on(FriendMessage)
        async def on_friend_message(event: FriendMessage):
            print(f"收到来自{event.sender.nickname}的消息。")
        ```
        """
        return self._bus.on(event_type=event_type)

    def api(self, api: str) -> ApiModel.Proxy:
        """获取 API Proxy 对象。

        API Proxy 提供更加简便的调用 API 的写法，详见`mirai.models.api`。

        `Mirai` 的 `__getattr__` 与此方法完全相同，可支持直接在对象上调用 API。

        `api: str` API 名称。
        """
        api_type = ApiModel.get_subtype(api)
        return api_type.Proxy(self, api_type)

    def __getattr__(self, api: str) -> ApiModel.Proxy:
        return self.api(api)

    async def send(
        self,
        target: Union[Entity, MessageEvent],
        message: Union[MessageChain, List[Union[MessageComponent, str]], str],
        quote: bool = False
    ) -> MessageResponse:
        """发送消息。可以从 `Friend` `Group` 等对象，或者从 `MessageEvent` 中自动识别消息发送对象。

        `target: Union[Entity, MessageEvent]` 目标对象。

        `message: Union[MessageChain, List[Union[MessageComponent, str]], str]` 发送的消息。

        `quote: bool = False` 是否以回复消息的形式发送。
        """
        # 构造消息链
        if isinstance(message, str):
            message = [message]
        # 识别消息发送对象
        if isinstance(target, TempMessage):
            quote = target.message_chain.message_id if quote else None
            return await self.send_temp_message(
                qq=target.sender.id,
                group=target.group.id,
                message_chain=message,
                quote=quote
            )
        else:
            if isinstance(target, MessageEvent):
                quote = target.message_chain.message_id if quote else None
                target = target.sender
            else:
                quote = None

            if isinstance(target, Friend):
                send_message = self.send_friend_message
                id = target.id
            elif isinstance(target, Group):
                send_message = self.send_group_message
                id = target.id
            elif isinstance(target, GroupMember):
                send_message = self.send_group_message
                id = target.group.id

            return await send_message(
                target=id, message_chain=message, quote=quote
            )

    async def get_friend(self, id: int) -> Optional[Friend]:
        """获取好友对象。

        `id: int` 好友 ID。
        """
        for friend in await self.friend_list.get():
            if friend.id == id:
                return friend

    async def get_group(self, id: int) -> Optional[Group]:
        """获取群组对象。

        `id: int` 群组 ID。
        """
        for group in await self.group_list.get():
            if group.id == id:
                return group

    async def get_group_member(self, group: Union[Group, int],
                               id: int) -> Optional[GroupMember]:
        """获取群成员对象。

        `group: Union[Group, int]` 群组对象或群组 ID。

        `id: int` 群成员 ID。
        """
        if isinstance(group, Group):
            group = group.id
        for member in await self.member_list(group):
            if member.id == id:
                return member

    async def get_entity(self, subject: Subject) -> Optional[Entity]:
        """获取实体对象。

        `subject: Subject` 实体对象。
        """
        if subject.kind == 'Friend':
            return await self.get_friend(subject.id)
        elif subject.kind == 'Group':
            return await self.get_group(subject.id)

    async def is_admin(self, group: Group) -> bool:
        """判断机器人在群组中是否是管理员。

        `group: Group` 群组对象。
        """
        return group.permission in (Permission.Administrator, Permission.Owner)


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
