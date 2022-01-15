# -*- coding: utf-8 -*-
"""
此模块提供 HTTP 轮询适配器，适用于 mirai-api-http 的 http adapter。
"""
import asyncio
import logging
import random
from typing import Optional

import httpx

from mirai.adapters.base import (
    Adapter, AdapterInterface, Session, error_handler_async, json_dumps
)
from mirai.exceptions import ApiError, NetworkError
from mirai.interface import ApiMethod
from mirai.tasks import Tasks

logger = logging.getLogger(__name__)


def _parse_response(response: httpx.Response) -> dict:
    """根据 API 返回结果解析错误信息。"""
    response.raise_for_status()
    result = response.json()
    if result.get('code', 0) != 0:
        raise ApiError(result)
    return result


_error_handler_async_local = error_handler_async(
    (httpx.NetworkError, httpx.InvalidURL)
)


@_error_handler_async_local
async def _post(client: httpx.AsyncClient, url: str,
                json: dict) -> Optional[dict]:
    """调用 POST 方法。"""
    # 使用自定义的 json.dumps
    content = json_dumps(json).encode('utf-8')
    try:
        response = await client.post(
            url,
            content=content,
            headers={'Content-Type': 'application/json'},
            timeout=60.
        )
        logger.debug(f'[HTTP] 发送 POST 请求，地址{url}，状态 {response.status_code}。')
    except httpx.TimeoutException:
        logger.error(f'[HTTP] POST 请求超时，地址{url}。')
        return None
    return _parse_response(response)


@_error_handler_async_local
async def _get(client: httpx.AsyncClient, url: str,
               params: dict) -> Optional[dict]:
    """调用 GET 方法。"""
    try:
        response = await client.get(url, params=params, timeout=60.)
        logger.debug(f'[HTTP] 发送 GET 请求，地址{url}，状态 {response.status_code}。')
    except httpx.TimeoutException:
        logger.error(f'[HTTP] GET 请求超时，地址{url}。')
        return None
    return _parse_response(response)


@_error_handler_async_local
async def _post_multipart(
    client: httpx.AsyncClient, url: str, data: dict, files: dict
) -> Optional[dict]:
    """调用 POST 方法，发送 multipart 数据。"""
    try:
        response = await client.post(url, data=data, files=files, timeout=30.)
        logger.debug(f'[HTTP] 发送 POST 请求，地址{url}，状态 {response.status_code}。')
    except httpx.TimeoutException:
        logger.error(f'[HTTP] POST 请求超时，地址{url}。')
        return None
    return _parse_response(response)


class HTTPSession(Session):
    """HTTP 轮询适配器的会话。"""
    adapter: 'HTTPAdapter'
    """创建 Session 的适配器。"""
    session: str
    """mirai-api-http 的 session。"""
    headers: httpx.Headers
    """HTTP 请求头。"""
    def __init__(self, qq: int, adapter: 'HTTPAdapter', session: str):
        super().__init__(qq)
        self.adapter = adapter
        self.session = session
        self.headers = httpx.Headers({'sessionKey': session})
        self._tasks = Tasks()

    @_error_handler_async_local
    async def poll_event(self):
        """进行一次轮询，获取并处理事件。"""
        async with httpx.AsyncClient(
            base_url=self.adapter.host_name, headers=self.headers
        ) as client:
            msg_count = (await _get(client, '/countMessage', {}) or {})['data']
            if msg_count > 0:
                msg_list = (
                    await _get(client, '/fetchMessage', {'count': msg_count})
                    or {}
                )['data']

                coros = [self.emit(msg) for msg in msg_list]
                await asyncio.gather(*coros)

    async def call_api(
        self,
        api: str,
        method: ApiMethod = ApiMethod.GET,
        *_,
        **params
    ) -> Optional[dict]:
        async with httpx.AsyncClient(
            base_url=self.adapter.host_name, headers=self.headers
        ) as client:
            if method == ApiMethod.GET or method == ApiMethod.RESTGET:
                return await _get(client, f'/{api}', params)
            if method == ApiMethod.POST or method == ApiMethod.RESTPOST:
                return await _post(client, f'/{api}', params)
            if method == ApiMethod.MULTIPART:
                return await _post_multipart(
                    client, f'/{api}', params['data'], params['files']
                )
            return None

    @_error_handler_async_local
    async def shutdown(self):
        if not self.adapter.single_mode:
            async with httpx.AsyncClient(
                base_url=self.adapter.host_name, headers=self.headers
            ) as client:
                await _post(
                    client, '/release', {
                        "sessionKey": self.session,
                        "qq": self.qq,
                    }
                )
        logger.info(f"[HTTP] 从账号{self.qq}退出。")
        await super().shutdown()

    async def _background(self):
        """开始轮询。"""
        logger.info('[HTTP] 机器人开始运行。按 Ctrl + C 停止。')

        try:
            while True:
                self._tasks.create_task(self.poll_event())
                await asyncio.sleep(self.adapter.poll_interval)
        finally:
            await self._tasks.cancel_all()


class HTTPAdapter(Adapter):
    """HTTP 轮询适配器。使用 HTTP 轮询的方式与 mirai-api-http 沟通。"""
    host_name: str
    """mirai-api-http 的 HTTPAdapter Server 主机名。"""
    poll_interval: float
    """轮询时间间隔，单位秒。"""
    def __init__(
        self,
        verify_key: Optional[str],
        host: str,
        port: int,
        poll_interval: float = 1.,
        single_mode: bool = False
    ):
        """
        Args:
            verify_key: mirai-api-http 配置的认证 key，关闭认证时为 None。
            host: HTTP Server 的地址。
            port: HTTP Server 的端口。
            poll_interval: 轮询时间间隔，单位秒。
            single_mode: 是否为单例模式。
        """
        super().__init__(verify_key=verify_key, single_mode=single_mode)

        self._host = host
        self._port = port

        if host[:2] == '//':
            host = 'http:' + host
        elif host[:8] == 'https://':
            raise NetworkError('不支持 HTTPS！')
        elif host[:7] != 'http://':
            host = 'http://' + host

        if host[-1:] == '/':
            host = host[:-1]

        self.host_name = f'{host}:{port}'

        self.poll_interval = poll_interval

        self.qq = 0

    @property
    def adapter_info(self):
        return {
            'verify_key': self.verify_key,
            'single_mode': self.single_mode,
            'host': self._host,
            'port': self._port,
            'poll_interval': self.poll_interval,
        }

    @classmethod
    def via(cls, adapter_interface: AdapterInterface) -> "HTTPAdapter":
        info = adapter_interface.adapter_info
        adapter = cls(
            verify_key=info['verify_key'],
            **{
                key: info[key]
                for key in ['host', 'port', 'poll_interval', 'single_mode']
                if key in info
            }
        )
        return adapter

    @_error_handler_async_local
    async def _login(self, qq: int) -> HTTPSession:
        async with httpx.AsyncClient(base_url=self.host_name) as client:
            if self.verify_key is not None:
                session = await _post(
                    client, '/verify', {
                        "verifyKey": self.verify_key,
                    }
                )
                session = (session or {})['session']

            else:
                session = str(random.randint(1, 2**20))

            if not self.single_mode:
                await _post(
                    client, '/bind', {
                        "sessionKey": session,
                        "qq": qq,
                    }
                )

            logger.info(f'[HTTP] 成功登录到账号{qq}。')
            return HTTPSession(qq, self, session)
