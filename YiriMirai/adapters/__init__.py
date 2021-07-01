import abc
import functools
import logging
from typing import Any, Awaitable, Callable, Union

from YiriMirai.bus import EventBus


class Api(object):
    '''支持从属性调用 API 的类。'''
    @abc.abstractmethod
    def call_api(self, api: str, **params) -> Union[Awaitable[Any], Any]:
        pass

    def __getattr__(self,
                    api: str) -> Callable[..., Union[Awaitable[Any], Any]]:
        return functools.partial(self.call_api, api)


class Adapter(Api):
    '''适配器基类，与 mirai-api-http 沟通的底层实现。
    '''
    def __init__(self, verify_key: str = ''):
        self.verify_key = verify_key
        self.bus: EventBus = None
        self.logger = logging.getLogger(__name__)

    @abc.abstractmethod
    async def login(self, qq: int):
        pass

    async def _before_run(self):
        if self.bus is None:
            raise RuntimeError('事件总线未指定！')

    async def run(self):
        await self._before_run()


from .http import HTTPAdapter

__all__ = ['Adapter', 'HTTPAdapter']
