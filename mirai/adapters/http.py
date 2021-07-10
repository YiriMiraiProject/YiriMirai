# -*- coding: utf-8 -*-
"""
此模块提供 HTTP 轮询适配器，适用于 mirai-api-http 的 http adapter。
"""
import asyncio
import logging

import httpx
from mirai import exceptions
from mirai.adapters.base import Adapter, Method, json_dumps

logger = logging.getLogger(__name__)


def _parse_response(response: httpx.Response) -> dict:
    """根据 API 返回结果解析错误信息。"""
    response.raise_for_status()
    result = response.json()
    if result.get('code', 0) != 0:
        raise exceptions.ApiError(result['code'])
    return result


def _error_handler_async(func):
    """错误处理装饰器。"""
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except (httpx.NetworkError, httpx.InvalidURL) as e:
            err = exceptions.NetworkError('无法连接到 mirai。请检查地址与端口是否正确。')
            logger.error(e)
            raise err from e
        except Exception as e:
            logger.error(e)
            raise

    return wrapper


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
        verify_key: str,
        host: str,
        port: int,
        poll_interval: float = 1.
    ):
        """
        `verify_key: str` mirai-api-http 配置的认证 key。

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

    @_error_handler_async
    async def _post(
        self, client: httpx.AsyncClient, url: str, json: dict
    ) -> dict:
        """调用 POST 方法。"""
        # 使用自定义的 json.dumps
        content = json_dumps(json).encode('utf-8')
        response = await client.post(
            url, content=content, headers={'Content-Type': 'application/json'}
        )
        logger.debug(f'发送 POST 请求，地址{url}，状态 {response.status_code}。')
        return _parse_response(response)

    @_error_handler_async
    async def _get(
        self, client: httpx.AsyncClient, url: str, params: dict
    ) -> dict:
        """调用 GET 方法。"""
        response = await client.get(url, params=params)
        logger.debug(f'发送 GET 请求，地址{url}，状态 {response.status_code}。')
        return _parse_response(response)

    @_error_handler_async
    async def login(self, qq: int):
        async with httpx.AsyncClient(
            base_url=self.host_name, headers=self.headers
        ) as client:
            if not self.session:
                self.session = (
                    await self._post(
                        client, '/verify', {
                            "verifyKey": self.verify_key,
                        }
                    )
                )['session']

            await self._post(
                client, '/bind', {
                    "sessionKey": self.session,
                    "qq": qq,
                }
            )

            self.headers = httpx.Headers({'sessionKey': self.session})
            self.qq = qq
            logger.info(f'成功登录到账号{qq}。')

    @_error_handler_async
    async def logout(self):
        async with httpx.AsyncClient(
            base_url=self.host_name, headers=self.headers
        ) as client:
            await self._post(
                client, '/release', {
                    "sessionKey": self.session,
                    "qq": self.qq,
                }
            )
            logger.info(f"从账号{self.qq}退出。")

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
        """调用 API。

        `api`: API 名称，需与 mirai-api-http 中的定义一致。

        `method`: 调用方法。默认为 GET。

        `params`: 参数。
        """
        async with httpx.AsyncClient(
            base_url=self.host_name, headers=self.headers
        ) as client:
            if method == Method.GET or method == Method.RESTGET:
                return await self._get(client, f'/{api}', params)
            elif method == Method.POST or method == Method.RESTPOST:
                return await self._post(client, f'/{api}', params)

    async def run(self):
        """开始轮询。"""
        await self._before_run()
        logger.info('机器人开始运行。按 Ctrl + C 停止。')
        while True:
            asyncio.create_task(self.poll_event())
            await asyncio.sleep(self.poll_interval)
