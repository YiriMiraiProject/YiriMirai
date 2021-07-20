# -*- coding: utf-8 -*-
"""
此模块提供网络适配器的一系列基础定义。
"""
import abc
import asyncio
import logging
from datetime import datetime
from json import dumps
from typing import Any, Dict, List, Optional, Set

from mirai import exceptions
from mirai.api_provider import ApiProvider, Method
from mirai.bus import EventBus

logger = logging.getLogger(__name__)


def _json_default(obj): # 支持 datetime
    if isinstance(obj, datetime):
        return int(obj.timestamp())


def json_dumps(obj) -> str:
    """保存为 json。"""
    return dumps(obj, default=_json_default)


def error_handler_async(errors):
    """错误处理装饰器。"""
    def wrapper(func):
        async def wrapped(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except errors as e:
                err = exceptions.NetworkError(
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
    def __subclasshook__(cls, C):
        if cls is AdapterInterface:
            if any("adapter_info" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented


class Adapter(ApiProvider, AdapterInterface):
    """适配器基类，与 mirai-api-http 沟通的底层实现。

    属性 `buses` 为适配器注册的事件总线集合。适配器被绑定到 bot 时，bot 会自动将自身的事件总线注册到适配器。
    """
    verify_key: Optional[str]
    """mirai-api-http 配置的认证 key，关闭认证时为 None。"""
    single_mode: bool
    """是否开启 single_mode，开启后与 session 将无效。"""
    session: str
    """从 mirai-api-http 处获得的 session。"""
    buses: Set[EventBus]
    """注册的事件总线集合。"""
    background: Optional[asyncio.Task]
    """背景事件循环任务。"""
    def __init__(self, verify_key: Optional[str], single_mode: bool = False):
        """
        `verify_key: str` mirai-api-http 配置的认证 key，关闭认证时为 None。
        """
        self.verify_key = verify_key
        self.single_mode = single_mode
        self.session = ''
        self.buses = set()
        self.background = None

    @property
    def adapter_info(self):
        return {
            'verify_key': self.verify_key,
            'session': self.session,
            'single_mode': self.single_mode,
        }

    @classmethod
    def via(cls, adapter_interface: AdapterInterface) -> "Adapter":
        """从适配器接口创建适配器。"""
        info = adapter_interface.adapter_info
        adapter = cls(
            verify_key=info['verify_key'],
            **{
                key: info[key]
                for key in ['single_mode'] if info.get(key) is not None
            }
        )
        adapter.session = info.get('session')
        return adapter

    def register_event_bus(self, *buses: List[EventBus]):
        """注册事件总线。

        `*buses: List[EventBus]` 一个或多个事件总线。
        """
        self.buses |= set(buses)

    def unregister_event_bus(self, *buses: List[EventBus]):
        """解除注册事件总线。

        `*buses: List[EventBus]` 一个或多个事件总线。
        """
        self.buses -= set(buses)

    @abc.abstractmethod
    async def login(self, qq: int):
        """登录到 mirai-api-http。"""

    @abc.abstractmethod
    async def logout(self, terminate: bool = True):
        """登出。"""

    @abc.abstractmethod
    async def call_api(self, api: str, method: Method = Method.GET, **params):
        """调用 API。

        `api`: API 名称，需与 mirai-api-http 中的定义一致。

        `method`: 调用方法。默认为 GET。

        `params`: 参数。
        """

    @abc.abstractmethod
    async def _background(self):
        """背景事件循环，用于接收事件。"""

    def start(self):
        """运行背景事件循环。"""
        if not self.buses:
            raise RuntimeError('事件总线未指定！')
        if not self.session:
            raise RuntimeError('未登录！')

        self.background = asyncio.create_task(self._background())

    def shutdown(self):
        """停止背景事件循环。"""
        if self.background:
            self.background.cancel()
