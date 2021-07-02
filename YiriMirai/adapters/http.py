# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime
from json import dumps as json_dumps
import httpx
from YiriMirai import exceptions
from YiriMirai.adapters.base import Adapter, Method


def _parse_response(response: httpx.Response) -> dict:
    response.raise_for_status()
    result = response.json()
    if result.get('code', 0) != 0:
        raise exceptions.ApiError(result['code'])
    return result


def _json_default(obj):
    if isinstance(obj, datetime):
        return int(obj.timestamp())


class HTTPAdapter(Adapter):
    '''HTTP 轮询适配器。使用 HTTP 轮询的方式与 mirai-api-http 沟通。
    '''
    def __init__(
        self,
        verify_key: str = '',
        host: str = 'localhost',
        port: int = 8080,
        poll_interval: float = 1.
    ):
        '''HTTP 轮询适配器。
        `verify_key: str` 创建Mirai-Http-Server时生成的key
        `bus: Optional[EventBus]` 事件总线，留空使用默认总线
        `host: str = 'localhost'` Http Server 的地址
        `port: int = 8080` Http Server 的端口
        `poll_interval: float = 1.` 轮询时间间隔，单位秒
        '''
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

        self.session = ''
        self.headers = httpx.Headers() # 使用 headers 传递 session

    async def _post(
        self, client: httpx.AsyncClient, url: str, json: dict
    ) -> dict:
        '''调用 POST 方法。'''
        # 使用自定义的 json.dumps
        content = json_dumps(json, default=_json_default).encode('utf-8')
        response = await client.post(
            url, content=content, headers={'Content-Type': 'application/json'}
        )
        self.logger.debug(f'发送 POST 请求，地址{url}，状态 {response.status_code}。')
        return _parse_response(response)

    async def _get(
        self, client: httpx.AsyncClient, url: str, params: dict
    ) -> dict:
        '''调用 GET 方法。'''
        response = await client.get(url, params=params)
        self.logger.debug(f'发送 GET 请求，地址{url}，状态 {response.status_code}。')
        return _parse_response(response)

    async def login(self, qq: int):
        async with httpx.AsyncClient(
            base_url=self.host_name, headers=self.headers
        ) as client:
            try:
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
                        'qq': qq,
                    }
                )
                self.headers = httpx.Headers({'sessionKey': self.session})
                self.logger.info(f'成功登录到账号{qq}。')
            except (
                httpx.exceptions.NetworkError, httpx.exceptions.InvalidURL
            ) as e:
                raise exceptions.NetworkError(
                    '无法连接到 mirai。请检查地址与端口是否正确。'
                ) from e
            except exceptions.ApiError as e:
                raise exceptions.LoginError(e.code) from None

    async def poll_event(self):
        async with httpx.AsyncClient(
            base_url=self.host_name, headers=self.headers
        ) as client:
            msg_count = (await self._get(client, '/countMessage', {}))['data']
            if msg_count > 0:
                msg_list = (
                    await
                    self._get(client, '/fetchMessage', {'count': msg_count})
                )['data']
                for bus in self.buses:
                    for msg in msg_list:
                        await bus.emit(msg['type'], msg)

    async def call_api(self, api: str, method: Method = Method.GET, **params):
        async with httpx.AsyncClient(
            base_url=self.host_name, headers=self.headers
        ) as client:
            if method == Method.GET:
                return await self._get(client, f'/{api}', params)
            elif method == Method.POST or method == Method.REST:
                return await self._post(client, f'/{api}', params)

    async def run(self):
        await self._before_run()
        self.logger.info('机器人开始运行。按 Ctrl + C 停止。')
        while True:
            await self.poll_event()
            await asyncio.sleep(self.poll_interval)
