# -*- coding: utf-8 -*-
"""
此模块提供 ApiProvider 的基础定义。
"""
import abc
import functools
from enum import Enum
from typing import Any, Awaitable, Callable, Union


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
    MULTIPART = "MULTIPART"
    """表明这是一个使用了 multipart/form-data 的 POST。"""


class ApiProvider(abc.ABC):
    """支持从属性调用 API 的类。

    使用了 `__getattr__`，可以直接通过属性调用 API。
    """
    @abc.abstractmethod
    async def call_api(
        self, api: str, method: Method = Method.GET, **params
    ) -> Any:
        """调用 API。此处为抽象方法，具体实现由子类决定。

        Args:
            api: API 名称。
            method: 调用方法。默认为 GET。
            **params: 参数。
        """

    def __getattr__(self,
                    api: str) -> Callable[..., Union[Awaitable[Any], Any]]:
        return functools.partial(self.call_api, api)
