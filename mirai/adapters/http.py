# -*- coding: utf-8 -*-
"""
此模块提供 HTTP 轮询适配器，适用于 mirai-api-http 的 http adapter。
"""
import asyncio
import logging
import random
from typing import Optional

import httpx
from mirai import exceptions
from mirai.tasks import Tasks
from mirai.adapters.base import Adapter, Method, json_dumps, error_handler_async

logger = logging.getLogger(__name__)


def _parse_response(response: httpx.Response) -> dict:
    """根据 API 返回结果解析错误信息。"""
    response.raise_for_status()
    result = response.json()
    if result.get('code', 0) != 0:
        raise exceptions.ApiError(result['code'])
    return result


_error_handler_async_local = error_handler_async(
    (httpx.NetworkError, httpx.InvalidURL)
)


class HTTPAdapter(Adapter):
    """HTTP 轮询适配器。使用 HTTP 轮询的方式与 mirai-api-http 沟通。
    """
    host_name: str
    """mirai-api-http 的 HTTPAdapter Server 主机名。"""
    poll_interval: float
    """轮询时间间隔，单位秒。"""
    qq: int
    """机器人的 QQ 号。"""
    headers: httpx.Headers
    """HTTP 请求头。"""
    def __init__(
        self,
        verify_key: Optional[str],
        host: str,
        port: int,
        poll_interval: float = 1.
    ):
        """
        `verify_key: str` mirai-api-http 配置的认证 key，关闭认证时为 None。

        `host: str` HTTP Server 的地址。

        `port: int` HTTP Server 的端口。

        `poll_interval: float = 1.` 轮询时间间隔，单位秒。
        """
        super().__init__(verify_key=verify_key)

        if host[:2] == '//':
            host = 'http:' + host
        elif host[:8] == 'https://':
            raise exceptions.NetworkError('不支持 HTTPS！')
        elif host[:7] != 'http://':
            host = 'http://' + host

        if host[-1:] == '/':
            host = host[:-1]

        self.host_name = f'{host}:{port}'

        self.poll_interval = poll_interval

        self.qq = 0
        self.headers = httpx.Headers() # 使用 headers 传递 session
        self._tasks = Tasks()

    @_error_handler_async_local
    async def _post(
        self, client: httpx.AsyncClient, url: str, json: dict
    ) -> dict:
        """调用 POST 方法。"""
        # 使用自定义的 json.dumps
        content = json_dumps(json).encode('utf-8')
        response = await client.post(
            url, content=content, headers={'Content-Type': 'application/json'}
        )
        logger.debug(f'[HTTP] 发送 POST 请求，地址{url}，状态 {response.status_code}。')
        return _parse_response(response)

    @_error_handler_async_local
    async def _get(
        self, client: httpx.AsyncClient, url: str, params: dict
    ) -> dict:
        """调用 GET 方法。"""
        response = await client.get(url, params=params)
        logger.debug(f'[HTTP] 发送 GET 请求，地址{url}，状态 {response.status_code}。')
        return _parse_response(response)

    @_error_handler_async_local
    async def login(self, qq: int):
        async with httpx.AsyncClient(
            base_url=self.host_name, headers=self.headers
        ) as client:
            if not self.session:
                if self.verify_key is not None:
                    self.session = (
                        await self._post(
                            client, '/verify', {
                                "verifyKey": self.verify_key,
                            }
                        )
                    )['session']
                else:
                    self.session = str(random.randint(1, 2**20))

            await self._post(
                client, '/bind', {
                    "sessionKey": self.session,
                    "qq": qq,
                }
            )

            self.headers = httpx.Headers({'sessionKey': self.session})
            self.qq = qq
            logger.info(f'[HTTP] 成功登录到账号{qq}。')

    @_error_handler_async_local
    async def logout(self):
        if self.session:
            async with httpx.AsyncClient(
                base_url=self.host_name, headers=self.headers
            ) as client:
                await self._post(
                    client, '/release', {
                        "sessionKey": self.session,
                        "qq": self.qq,
                    }
                )
                logger.info(f"[HTTP] 从账号{self.qq}退出。")

    async def poll_event(self):
        """进行一次轮询，获取并处理事件。"""
        async with httpx.AsyncClient(
            base_url=self.host_name, headers=self.headers
        ) as client:
            msg_count = (await self._get(client, '/countMessage', {}))['data']
            if msg_count > 0:
                msg_list = (
                    await
                    self._get(client, '/fetchMessage', {'count': msg_count})
                )['data']

                coros = []
                for bus in self.buses:
                    for msg in msg_list:
                        coros.append(bus.emit(msg['type'], msg))
                await asyncio.gather(*coros)

    async def call_api(self, api: str, method: Method = Method.GET, **params):
        async with httpx.AsyncClient(
            base_url=self.host_name, headers=self.headers
        ) as client:
            if method == Method.GET or method == Method.RESTGET:
                return await self._get(client, f'/{api}', params)
            elif method == Method.POST or method == Method.RESTPOST:
                return await self._post(client, f'/{api}', params)

    async def _background(self):
        """开始轮询。"""
        logger.info('[HTTP] 机器人开始运行。按 Ctrl + C 停止。')

        try:
            while True:
                self._tasks.create_task(self.poll_event())
                await asyncio.sleep(self.poll_interval)
        finally:
            self._tasks.cancel_all()
