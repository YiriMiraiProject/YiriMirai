# -*- coding: utf-8 -*-
"""
此模块提供网络适配器的一系列基础定义。
"""
import abc
import functools
import logging
from enum import Enum
from typing import Any, Awaitable, Callable, List, Set, Union

from YiriMirai.bus import EventBus


class Method(str, Enum):
    """API 接口的调用方法。"""
    GET = "GET"
    """使用 GET 方法调用。"""
    POST = "POST"
    """使用 POST 方法调用。"""
    REST = "REST"
    """表明这是一个 RESTful 的 POST。"""


class Api(object):
    """支持从属性调用 API 的类。

    使用了`__getattr__`，可以直接通过属性调用 API。
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


class Adapter(Api):
    """适配器基类，与 mirai-api-http 沟通的底层实现。

    属性`buses`为适配器注册的事件总线集合。适配器被绑定到 bot 时，bot 会自动将自身的事件总线注册到适配器。
    """
    def __init__(self, verify_key: str = ''):
        """
        `verify_key: str = ''` mirai-api-http 配置的认证 key。
        """
        self.verify_key = verify_key
        self.buses: Set[EventBus] = set()
        self.logger = logging.getLogger(__name__)

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
        """登录到 mirai-api-http。此处为抽象方法，具体实现由子类决定。"""

    async def _before_run(self):
        if not self.buses:
            raise RuntimeError('事件总线未指定！')

    async def run(self):
        """运行。

        具体实现由子类决定。一般的行为是进入事件循环。
        """
        await self._before_run()
