import asyncio

import httpx

from . import Adapter
from ..exceptions import ApiError


def _parse_response(response: httpx.Response) -> dict:
    response.raise_for_status()
    result = response.json()
    if result['code'] != 0:
        raise ApiError(result['code'])
    return result


class HTTPAdapter(Adapter):
    '''HTTP 轮询适配器。使用 HTTP 轮询的方式与 mirai-api-http 沟通。
    '''
    def __init__(self,
                 verify_key: str = '',
                 host: str = 'localhost',
                 port: int = 8080,
                 poll_interval: float = 1.):
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
        elif host[:7] != 'http://' and host[:8] != 'https://':
            host = 'http://' + host

        if host[-1:] == '/':
            host = host[:-1]

        self.host_name = f'{host}:{port}'

        self.poll_interval = poll_interval

        self.session = ''
        self.headers = httpx.Headers()

    async def _post(self, client: httpx.AsyncClient, url: str,
                    json: dict) -> dict:
        response = await client.post(url, json=json, headers=self.headers)
        self.logger.debug(f'发送 POST 请求，地址{url}，状态 {response.status_code}。')
        return _parse_response(response)

    async def _get(self, client: httpx.AsyncClient, url: str,
                   params: dict) -> dict:
        response = await client.get(url, params=params, headers=self.headers)
        self.logger.debug(f'发送 GET 请求，地址{url}，状态 {response.status_code}。')
        return _parse_response(response)

    async def login(self, qq: int):
        async with httpx.AsyncClient(base_url=self.host_name) as client:
            self.session = (await self._post(client, '/verify', {
                "verifyKey": self.verify_key,
            }))['session']
            await self._post(client, '/bind', {
                "sessionKey": self.session,
                'qq': qq,
            })
            self.headers = httpx.Headers({'sessionKey': self.session})
            self.logger.info(f'成功登录到账号{qq}。')

    async def poll_event(self):
        async with httpx.AsyncClient(base_url=self.host_name) as client:
            msg_count = (await self._get(client, '/countMessage', {}))['data']
            if msg_count > 0:
                msg_list = (await self._get(client, '/fetchMessage',
                                            {'count': msg_count}))['data']
                for msg in msg_list:
                    await self.bus.emit(msg['type'], msg)

    async def call_api(self, api: str, **params):
        async with httpx.AsyncClient(base_url=self.host_name) as client:
            try:
                # 首先尝试使用 GET 请求
                return await self._get(client, f'/{api}', params)
            except httpx.HTTPError as e:
                # 如果没有就尝试 POST 请求
                if e.response.status_code == 404:
                    return await self._post(client, f'/{api}', params)

    async def run(self):
        await self._before_run()
        self.logger.info('机器人开始运行。按 Ctrl + C 停止。')
        while True:
            await self.poll_event()
            await asyncio.sleep(self.poll_interval)
