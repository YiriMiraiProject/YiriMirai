# -*- coding: utf-8 -*-
"""
此模块提供网络适配器的一系列基础定义。
"""
import abc
import asyncio
import logging
from datetime import datetime
from json import dumps
from typing import Any, Dict, NoReturn, Optional, Set, Tuple, Type, Union

from mirai.api_provider import ApiProvider, Method
from mirai.bus import AbstractEventBus
from mirai.exceptions import NetworkError
from mirai.tasks import Tasks

logger = logging.getLogger(__name__)


def _json_default(obj: Any):  # 支持 datetime
    if isinstance(obj, datetime):
        return int(obj.timestamp())


def json_dumps(obj: Any) -> str:
    """保存为 json。"""
    return dumps(obj, default=_json_default)


def error_handler_async(errors: Tuple[Type[BaseException], ...]):
    """错误处理装饰器。"""
    def wrapper(func):
        async def wrapped(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except KeyError:
                raise NetworkError('从 mirai-api-http 返回的数据格式错误。请检查版本是否正确。')
            except errors as e:
                err = NetworkError(
                    '无法连接到 mirai。请检查 mirai-api-http 是否启动，地址与端口是否正确。'
                )
                logger.error(err)
                raise err from e
            except Exception as e:
                logger.error(e)
                raise

        return wrapped

    return wrapper


class AdapterInterface(abc.ABC):
    """适配器接口，包含适配器信息。"""
    @property
    @abc.abstractmethod
    def adapter_info(self) -> Dict[str, Any]:
        "适配器信息。"

    @classmethod
    def __subclasshook__(cls, C: type):
        if cls is AdapterInterface:
            if any("adapter_info" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented


class Session(ApiProvider):
    """会话。表示适配器到 mirai-api-http 的一个连接。"""
    qq: int
    """机器人的 QQ 号。"""
    buses: Set[AbstractEventBus]
    """注册的事件总线集合。"""
    background: Optional[asyncio.Task]
    """背景事件循环任务。"""
    def __init__(self, qq: int):
        self.qq = qq
        self.buses = set()
        self.background = None

    def register_event_bus(self, *buses: AbstractEventBus):
        """注册事件总线。

        Args:
            *buses: 一个或多个事件总线。
        """
        self.buses |= set(buses)

    def unregister_event_bus(self, *buses: AbstractEventBus):
        """解除注册事件总线。

        Args:
            *buses: 一个或多个事件总线。
        """
        self.buses -= set(buses)

    @abc.abstractmethod
    async def _background(self) -> Union[NoReturn, None]:
        """背景事件循环，用于接收事件。"""

    async def start(self):
        """运行背景事件循环。"""
        if not self.buses:
            raise RuntimeError('事件总线未指定！')

        self.background = asyncio.create_task(self._background())

    @abc.abstractmethod
    async def call_api(
        self, api: str, method: Method = Method.GET, **params
    ) -> Any:
        """调用 API。

        Args:
            api: API 名称，需与 mirai-api-http 中的定义一致。
            method: 调用方法。默认为 GET。
            **params: 参数。
        """

    async def shutdown(self):
        """退出登录，并停止背景事件循环。"""
        if self.background:
            await Tasks.cancel(self.background)

    async def emit(self, event: str, *args, **kwargs):
        """向事件总线发送一个事件。

        Args:
            event: 事件名称。
            *args: 事件参数。
            **kwargs: 事件参数。
        """
        coros = [bus.emit(event, *args, **kwargs) for bus in self.buses]
        return sum(await asyncio.gather(*coros), [])


class Adapter(AdapterInterface):
    """适配器基类，与 mirai-api-http 沟通的底层实现。

    属性 `buses` 为适配器注册的事件总线集合。适配器被绑定到 bot 时，bot 会自动将自身的事件总线注册到适配器。
    """
    verify_key: Optional[str]
    """mirai-api-http 配置的认证 key，关闭认证时为 None。"""
    single_mode: bool
    """是否开启 single_mode，开启后与 session 将无效。"""
    sessions: Dict[int, Session]
    """已登录的会话。"""
    def __init__(self, verify_key: Optional[str], single_mode: bool = False):
        """
        Args:
            verify_key: mirai-api-http 配置的认证 key，关闭认证时为 None。
            single_mode: 是否开启 single_mode，开启后与 session 将无效。
        """
        self.verify_key = verify_key
        self.single_mode = single_mode
        self.sessions = {}

    @property
    def adapter_info(self) -> Dict[str, Any]:
        return {
            'verify_key': self.verify_key,
            'single_mode': self.single_mode,
        }

    @classmethod
    def via(cls, adapter_interface: AdapterInterface) -> "Adapter":
        """从适配器接口创建适配器。

        Args:
            adapter_interface: 适配器接口。

        Returns:
            Adapter: 创建的适配器。
        """
        info = adapter_interface.adapter_info
        adapter = cls(
            verify_key=info['verify_key'],
            **{
                key: info[key]
                for key in ['single_mode'] if info.get(key) is not None
            }
        )
        return adapter

    @abc.abstractmethod
    async def _login(self, qq: int) -> Session:
        """登录到 mirai-api-http。"""

    async def login(self, qq: int) -> Session:
        """登录到 mirai-api-http。"""
        session = await self._login(qq)
        self.sessions[qq] = session
        return session

    async def logout(self, qq: int):
        """登出。"""
        session = self.sessions[qq]
        await session.shutdown()
        self.sessions.pop(qq)


__all__ = ['Adapter', 'AdapterInterface', 'Session', 'error_handler_async']
