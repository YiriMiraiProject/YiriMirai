import asyncio
import json
import logging
import random
from collections import defaultdict

import websockets
from mirai import exceptions
from mirai.adapters.base import Adapter, Method, json_dumps

logger = logging.getLogger(__name__)


class WebSocketAdapter(Adapter):
    """WebSocket 适配器。作为 WebSocket 客户端与 mirai-api-http 沟通。
    """
    host_name: str
    """WebSocket Server 的地址。"""
    sync_id: str
    """mirai-api-http 配置的同步 ID。"""
    qq: int
    """机器人的 QQ 号。"""
    connection: websockets.WebSocketClientProtocol
    """WebSocket 客户端连接。"""
    def __init__(
        self, verify_key: str, host: str, port: int, sync_id: str = '-1'
    ):
        """
        `verify_key: str` mirai-api-http 配置的认证 key。

        `host: str` WebSocket Server 的地址。

        `port: int` WebSocket Server 的端口。

        `sync_id: int` mirai-api-http 配置的同步 ID。
        """
        super().__init__(verify_key=verify_key)

        if host[:2] == '//':
            host = 'ws:' + host
        elif host[:7] == 'http://' or host[:8] == 'https://':
            raise exceptions.NetworkError(f'{host} 不是一个可用的 WebSocket 地址！')
        elif host[:5] != 'ws://':
            host = 'ws://' + host

        if host[-1:] == '/':
            host = host[:-1]

        self.host_name = f'{host}:{port}/all'

        self.sync_id = sync_id # 这个神奇的 sync_id，默认值 -1，居然是个字符串
        # 既然这样不如把 sync_id 全改成字符串好了

        # 接收 WebSocket 数据的 Task
        self._start_task = None
        # 用于临时保存接收到的数据，以便根据 sync_id 进行同步识别
        self._recv_dict = defaultdict(list)
        # 本地同步 ID，每次调用 API 递增。
        self._local_sync_id = random.randint(1, 1024) * 1024

    async def _start(self):
        """开始接收 websocket 数据。"""
        if not self.connect:
            raise exceptions.NetworkError(
                f'WebSocket 通道 {self.host_name} 未连接！'
            )
        while self._started:
            try:
                response = json.loads(await self.connection.recv())
                data = response['data']

                if data.get('code', 0) != 0:
                    raise exceptions.ApiError(data['code'])

                logger.debug(f"收到 WebSocket 数据，同步 ID：{response['syncId']}。")
                self._recv_dict[response['syncId']].append(data)
            except KeyError:
                logger.error(f'不正确的数据：{response}')
            except websockets.ConnectionClosedOK:
                return
            except websockets.ConnectionClosed as e:
                logger.error(
                    f'WebSocket 通道意外关闭。code: {e.code}, reason: {e.reason}'
                )
                return

    async def _recv(self, sync_id: str = '-1') -> dict:
        """接收并解析 websocket 数据。"""
        while not self._recv_dict[sync_id]:
            # 如果没有对应同步 ID 的数据，则等待 websocket 数据
            await asyncio.sleep(0)
        return self._recv_dict[sync_id].pop(0)

    async def login(self, qq: int):
        headers = {
            'verifyKey': self.verify_key,
            'qq': qq,
        }
        if self.session:
            headers['sessionKey'] = self.session

        self.connection = await websockets.connect(
            self.host_name, extra_headers=headers
        )
        self._start_task = asyncio.create_task(self._start())

        verify_response = await self._recv('') # 神奇现象：这里的 syncId 是个空字符串
        self.session = verify_response['session']

        self.qq = qq
        logger.info(f'成功登录到账号{qq}。')

    async def logout(self):
        await self.connection.close()

        await self._start_task

        logger.info(f"从账号{self.qq}退出。")

    async def poll_event(self):
        """获取并处理事件。"""
        event = await self._recv(self.sync_id)

        for bus in self.buses:
            asyncio.create_task(bus.emit(event['type'], event))

    async def call_api(self, api: str, method: Method = Method.GET, **params):
        """调用 API。

        `api`: API 名称，需与 mirai-api-http 中的定义一致。

        `method`: 调用方法。默认为 GET。

        `params`: 参数。
        """
        self._local_sync_id += 1 # 使用不同的 sync_id
        sync_id = str(self._local_sync_id)
        content = {
            'syncId': sync_id,
            'command': api.replace('/', '_'),
            'content': params
        }
        if method == Method.RESTGET:
            content['subCommand'] = 'get'
        elif method == Method.RESTPOST:
            content['subCommand'] = 'update'

        await self.connection.send(json_dumps(content))
        logger.debug(f"发送 WebSocket 数据，同步 ID：{sync_id}。")
        return await self._recv(sync_id)

    async def run(self):
        """开始接收事件。"""
        await self._before_run()
        logger.info('机器人开始运行。按 Ctrl + C 停止。')
        while True:
            await self.poll_event()
