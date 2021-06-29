import abc
import functools
from typing import Optional, Callable, Any, Union, Awaitable
from ..bus import EventBus


class Adapter(object):
    '''适配器基类，与 mirai-api-http 沟通的底层实现。
    '''
    def __init__(self, verify_key: str = '', bus: Optional[EventBus] = None):
        self.verify_key = verify_key
        self._bus = bus or EventBus.get_default_bus()

    @abc.abstractmethod
    async def login(self, qq: int):
        pass

    @abc.abstractmethod
    async def call_api(self, api: str, **params) -> Union[Awaitable[Any], Any]:
        pass

    def __getattr__(self,
                    api: str) -> Callable[..., Union[Awaitable[Any], Any]]:
        return functools.partial(self.call_api, api)

    @abc.abstractmethod
    async def run(self):
        pass


from .http import HTTPAdapter

__all__ = ['Adapter', 'HTTPAdapter']
