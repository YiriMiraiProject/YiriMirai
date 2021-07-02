# -*- coding: utf-8 -*-
import abc
import functools
import logging
from enum import Enum
from typing import Any, Awaitable, Callable, List, Set, Union

from YiriMirai.bus import EventBus


class Method(str, Enum):
    '''API 接口的调用方法。

    `GET` 使用 GET 方法调用。

    `POST` 使用 POST 方法调用。

    `REST` 表明这是一个 RESTful 的 POST。
    '''
    GET = "GET"
    POST = "POST"
    REST = "REST"


class Api(object):
    '''支持从属性调用 API 的类。'''
    @abc.abstractmethod
    def call_api(self,
                 api: str,
                 method: Method = Method.GET,
                 **params) -> Union[Awaitable[Any], Any]:
        pass

    def __getattr__(self,
                    api: str) -> Callable[..., Union[Awaitable[Any], Any]]:
        return functools.partial(self.call_api, api)


class Adapter(Api):
    '''适配器基类，与 mirai-api-http 沟通的底层实现。
    '''
    def __init__(self, verify_key: str = ''):
        self.verify_key = verify_key
        self.buses: Set[EventBus] = set()
        self.logger = logging.getLogger(__name__)

    def register_event_bus(self, *buses: List[EventBus]):
        '''注册事件总线。

        `*buses: List[EventBus]` 一个或多个事件总线
        '''
        self.buses |= set(buses)

    def unregister_event_bus(self, *buses: List[EventBus]):
        '''解注册事件总线。

        `*buses: List[EventBus]` 一个或多个事件总线
        '''
        self.buses -= set(buses)

    @abc.abstractmethod
    async def login(self, qq: int):
        pass

    async def _before_run(self):
        if self.bus is None:
            raise RuntimeError('事件总线未指定！')

    async def run(self):
        await self._before_run()
