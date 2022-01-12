"""
"""

import abc
from enum import Enum
from typing import Any, Generic, TypeVar


class ApiMethod(str, Enum):
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


class ApiInterface():
    """API 接口。由适配器提供，模型层通过接口调用底层API。"""
    @abc.abstractmethod
    async def call_api(
        self,
        api: str,
        method: ApiMethod = ApiMethod.GET,
        *args,
        **kwargs
    ) -> Any:
        """调用 API。此处为抽象方法，具体实现由子类决定。

        Args:
            api: API 名称。
            method: 调用方法。默认为 GET。
            *args: 参数。
            **kwargs: 参数。
        """


TEvent = TypeVar('TEvent', contravariant=True)


class EventInterface(Generic[TEvent]):
    """事件接口，由模型层提供，适配器通过接口向上发送事件通知。"""
    @abc.abstractmethod
    async def emit(self, event: TEvent) -> Any:
        """触发一个事件。"""


__all__ = [
    'ApiMethod',
    'ApiInterface',
    'EventInterface',
]
