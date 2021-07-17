# -*- coding: utf-8 -*-
"""
此模块提供网络适配器的一系列基础定义。
"""
import abc
import asyncio
import functools
import logging
from datetime import datetime
from enum import Enum
from json import dumps
from typing import Any, Awaitable, Callable, List, Optional, Set, Union

from mirai import exceptions
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


async def default_asgi(scope, recv, send):
    """默认的 ASGI 行为：把所有 HTTP 请求重定向到项目主页。"""
    if scope["type"] == "http":
        await recv()
        await send(
            {
                "type": "http.response.start",
                "status": 301,
                "headers": [[b"Location", b"https://yiri-mirai.vercel.app"], ]
            }
        )
        await send({
            'type': 'http.response.body',
            'body': b'',
        })


class Method(str, Enum):
    """API 接口的调用方法。"""
    GET = "GET"
    """使用 GET 方法调用。"""
    POST = "POST"
    """使用 POST 方法调用。"""
    # 区分下面两个，是为了兼容 websocket
    RESTGET = "RESTGET"
    """表明这是一个对 RESTful 接口的 GET。"""
    RESTPOST = "RESTPOST"
    """表明这是一个对 RESTful 接口的 POST。"""


class ApiProvider(object):
    """支持从属性调用 API 的类。

    使用了 `__getattr__`，可以直接通过属性调用 API。
    """
    @abc.abstractmethod
    def call_api(self,
                 api: str,
                 method: Method = Method.GET,
                 **params) -> Union[Awaitable[Any], Any]:
        """调用 API。此处为抽象方法，具体实现由子类决定。

        `api`: API 名称。

        `method`: 调用方法。默认为 GET。

        `params`: 参数。
        """

    def __getattr__(self,
                    api: str) -> Callable[..., Union[Awaitable[Any], Any]]:
        return functools.partial(self.call_api, api)


class Adapter(ApiProvider):
    """适配器基类，与 mirai-api-http 沟通的底层实现。

    属性 `buses` 为适配器注册的事件总线集合。适配器被绑定到 bot 时，bot 会自动将自身的事件总线注册到适配器。
    """
    verify_key: Optional[str]
    """mirai-api-http 配置的认证 key。"""
    session: str
    """从 mirai-api-http 处获得的 session。"""
    buses: Set[EventBus]
    """注册的事件总线集合。"""
    background: asyncio.Task
    """背景事件循环任务。"""
    def __init__(self, verify_key: Optional[str]):
        """
        `verify_key: str` mirai-api-http 配置的认证 key，关闭认证时为 None。
        """
        self.verify_key = verify_key
        self.session = ''
        self.buses = set()

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
    async def logout(self):
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

    @property
    def asgi(self) -> Callable:
        """返回 ASGI 实例，可用于启动服务。"""
        return default_asgi
