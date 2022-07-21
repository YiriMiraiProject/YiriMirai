# -*- coding: utf-8 -*-
"""
此模块提供正向 WebSocket 适配器，适用于 mirai-api-http 的 websocket adapter。
"""

import asyncio
import json
import logging
import random
import time
from typing import Dict, Optional

from websockets.client import WebSocketClientProtocol, connect
from websockets.exceptions import (
    ConnectionClosed, ConnectionClosedOK, InvalidURI
)

from mirai.adapters.base import (
    Adapter, AdapterInterface, Session, error_handler_async, json_dumps
)
from mirai.exceptions import ApiError, NetworkError
from mirai.interface import ApiMethod
from mirai.utils import Tasks

logger = logging.getLogger(__name__)

_error_handler_async_local = error_handler_async(
    (ConnectionRefusedError, InvalidURI)
)


class WebSocketSession(Session):
    """WebSocket 适配器的会话。"""
    adapter: 'WebSocketAdapter'
    """创建 Session 的适配器。"""
    session: str
    """mirai-api-http 的 session。"""
    connection: Optional[WebSocketClientProtocol]
    """WebSocket 客户端连接。"""

    def __init__(self, qq: int, adapter: 'WebSocketAdapter'):
        super().__init__(qq)
        self.adapter = adapter

        # 接收 WebSocket 数据的 Task
        self._receiver_task: Optional[asyncio.Task] = None
        # # 用于临时保存接收到的数据，以便根据 sync_id 进行同步识别
        # self._recv_dict: Dict[str, deque] = defaultdict(deque)
        self._recv_futures: Dict[str, asyncio.Future[dict]] = {}
        # 本地同步 ID，每次调用 API 递增。
        self._local_sync_id = random.randint(1, 1024) * 1024
        # 事件处理任务管理器
        self._tasks = Tasks()
        # 心跳机制（Keep-Alive）：上次发送数据包的时间
        self._last_send_time: float = 0.

    async def login(self, verify_key: str, host_name: str):
        headers = {
            'verifyKey': verify_key,  # 关闭认证时，WebSocket 可传入任意 verify_key
            'qq': str(self.qq),
        }

        self.connection = await connect(host_name, extra_headers=headers)
        self._receiver_task = asyncio.create_task(self._receiver())

        verify_response = await self._recv('')  # 神奇现象：这里的 syncId 是个空字符串
        self.session = verify_response['session']

    async def shutdown(self):
        if self.connection:
            await self.connection.close()

            if self._receiver_task:
                await self._receiver_task

            logger.info(f"[WebSocket] 从账号{self.qq}退出。")
        await super().shutdown()

    @_error_handler_async_local
    async def _receiver(self):
        """开始接收 websocket 数据。"""
        if not self.connection:
            raise NetworkError('WebSocket 通道未连接！')

        response = None
        while True:
            try:
                # 数据格式：
                # {
                #   'syncId': '-1',
                #   'data': {
                #       // Event Content
                #   }
                # }
                response = json.loads(await self.connection.recv())
                data = response['data']
                sync_id = response['syncId']

                logger.debug(f"[WebSocket] 收到 WebSocket 数据，同步 ID：{sync_id}。")

                if sync_id == self.adapter.sync_id:
                    self._tasks.create_task(self.emit(data))
                else:
                    self._recv_futures[sync_id].set_result(data)
                    del self._recv_futures[sync_id]

            except KeyError:
                logger.error(f'[WebSocket] 不正确的数据：{response}')
            except ConnectionClosedOK as e:
                raise SystemExit() from e
            except ConnectionClosed as e:
                exit_message = f'[WebSocket] WebSocket 通道意外关闭。code: {e.code}, reason: {e.reason}'

                logger.error(exit_message)
                raise SystemExit(exit_message) from e

    async def _recv(self, sync_id: str = '-1', timeout: int = 600) -> dict:
        """接收并解析 websocket 数据。"""
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._recv_futures[sync_id] = future  # future 在 _receiver 中被从 dict 删除。
        data = await future
        if data.get('code', 0) != 0:
            raise ApiError(data)
        return data

    async def call_api(
        self, api: str, method: ApiMethod = ApiMethod.GET, *_, **params
    ):
        if not self.connection:
            raise NetworkError('WebSocket 通道未连接！')
        self._local_sync_id += 1  # 使用不同的 sync_id
        sync_id = str(self._local_sync_id)
        content = {
            'syncId': sync_id,
            'command': api.replace('/', '_'),
            'content': params
        }
        if method == ApiMethod.RESTGET:
            content['subCommand'] = 'get'
        elif method == ApiMethod.RESTPOST:
            content['subCommand'] = 'update'
        elif method == ApiMethod.MULTIPART:
            raise NotImplementedError(
                "WebSocket 适配器不支持上传操作。请使用 bot.use_adapter 临时调用 HTTP 适配器。"
            )

        await self.connection.send(json_dumps(content))
        self._last_send_time = time.time()
        logger.debug(f"[WebSocket] 发送 WebSocket 数据，同步 ID：{sync_id}。")
        try:
            return await self._recv(sync_id)
        except TimeoutError as e:
            logger.debug(e)

    async def _heartbeat(self):
        while self.connection:
            await asyncio.sleep(self.adapter.heartbeat_interval)
            if time.time(
            ) - self._last_send_time > self.adapter.heartbeat_interval:
                await self.connection.send('{}')
                self._last_send_time = time.time()
                logger.debug("[WebSocket] 发送心跳包。")

    async def _background(self):
        """开始接收事件。"""
        logger.info('[WebSocket] 机器人开始运行。按 Ctrl + C 停止。')

        try:
            await self._heartbeat()
        finally:
            await self._tasks.cancel_all()


class WebSocketAdapter(Adapter):
    """WebSocket 适配器。作为 WebSocket 客户端与 mirai-api-http 沟通。"""
    host_name: str
    """WebSocket Server 的地址。"""
    sync_id: str
    """mirai-api-http 配置的同步 ID。"""
    heartbeat_interval: float
    """每隔多久发送心跳包，单位：秒。"""

    def __init__(
        self,
        verify_key: Optional[str],
        host: str,
        port: int,
        sync_id: str = '-1',
        single_mode: bool = False,
        heartbeat_interval: float = 60.,
    ):
        """
        Args:
            verify_key: mirai-api-http 配置的认证 key，关闭认证时为 None。
            host: WebSocket Server 的地址。
            port: WebSocket Server 的端口。
            sync_id: mirai-api-http 配置的同步 ID。
            single_mode: 是否启用单例模式。
            heartbeat_interval: 每隔多久发送心跳包，单位秒。
        """
        super().__init__(verify_key=verify_key, single_mode=single_mode)

        self._host = host
        self._port = port

        if host.startswith('//'):
            host = f'ws:{host}'
        elif host.startswith('http://') or host.startswith('https://'):
            raise NetworkError(f'{host} 不是一个可用的 WebSocket 地址！')
        elif host[:5] != 'ws://':
            host = f'ws://{host}'

        host = host.removesuffix('/')
        self.host_name = f'{host}:{port}/all'

        self.sync_id = sync_id  # 这个神奇的 sync_id，默认值 -1，居然是个字符串
        # 既然这样不如把 sync_id 全改成字符串好了

        self.heartbeat_interval = heartbeat_interval

    @property
    def adapter_info(self):
        return {
            'verify_key': self.verify_key,
            'single_mode': self.single_mode,
            'host': self._host,
            'port': self._port,
            'sync_id': self.sync_id,
        }

    @classmethod
    def via(cls, adapter_interface: AdapterInterface) -> "WebSocketAdapter":
        info = adapter_interface.adapter_info
        adapter = cls(
            verify_key=info['verify_key'],
            **{
                key: info[key]
                for key in ['host', 'port', 'sync_id', 'single_mode']
                if key in info
            }
        )
        return adapter

    @_error_handler_async_local
    async def _login(self, qq: int) -> WebSocketSession:
        session = WebSocketSession(qq, self)
        await session.login(self.verify_key or '', self.host_name)
        logger.info(f'[WebSocket] 成功登录到账号{qq}。')
        return session
