# -*- coding: utf-8 -*-
"""
此模块提供 HTTP 回调适配器，适用于 mirai-api-http 的 webhook adapter。
"""
import logging
from typing import Optional

from starlette.requests import Request
from starlette.responses import JSONResponse

from mirai.adapters.base import Adapter, json_dumps
from mirai.api_provider import Method
from mirai.asgi import ASGI

logger = logging.getLogger(__name__)


class YiriMiraiJSONResponse(JSONResponse):
    """调用自定义的 json_dumps 的 JSONResponse。"""
    def render(self, content) -> bytes:
        return json_dumps(content).encode('utf-8')


class WebHookAdapter(Adapter):
    """WebHook 适配器。作为 HTTP 服务器与 mirai-api-http 沟通。
    """
    session: str
    """WebHook 不需要 session，此处为机器人的 QQ 号。"""
    route: str
    """适配器的路由。"""
    extra_headers: dict
    """额外请求头。"""
    enable_quick_response: bool
    """是否启用快速响应。"""
    def __init__(
        self,
        verify_key: Optional[str],
        route: str = '/',
        extra_headers: Optional[dict] = None,
        enable_quick_response: bool = True,
        single_mode: bool = False
    ):
        """
        `verify_key: str` mirai-api-http 配置的认证 key，关闭认证时为 None。

        `route: str = '/'` 适配器的路由，默认在根目录上提供服务。

        `extra_headers: Optional[dict] = None` 额外请求头，与 mirai-api-http 的配置一致。

        `enable_quick_response: bool = True` 是否启用快速响应，当与其他适配器混合使用时，
            禁用可以提高响应速度。

        `single_mode: bool = False` 是否启用单例模式。
        """
        super().__init__(verify_key=verify_key, single_mode=single_mode)
        self.route = route
        self.extra_headers = extra_headers or {}
        self.enable_quick_response = enable_quick_response

        async def endpoint(request: Request):
            # 鉴权（QQ 号和额外请求头）
            if request.headers.get('bot') != self.session: # 验证 QQ 号
                logger.debug(f"收到来自其他账号（{request.headers.get('bot')}）的事件。")
                return
            for key in self.extra_headers: # 验证请求头
                key = key.lower() # HTTP headers 不区分大小写
                if request.headers.get(key).lower(
                ) != self.extra_headers[key].lower():
                    logger.debug(
                        f"请求头验证失败：expect {self.extra_headers[key].lower()}, " +
                        f"got {request.headers.get(key).lower()}。"
                    )
                    return JSONResponse(
                        status_code=401, content={'error': 'Unauthorized'}
                    )
            # 处理事件
            event = await request.json()
            result = await self.handle_event(event)
            return YiriMiraiJSONResponse(result)

        ASGI().add_route(self.route, endpoint, methods=['POST'])

    class QuickResponse(BaseException):
        """WebHook 快速响应，以异常的方式跳出。"""
        def __init__(self, data: dict):
            self.data = data

    async def login(self, qq: int):
        """WebHook 不需要登录。直接返回。"""
        self.session = str(qq)
        logger.info(f'[WebHook] 成功登录到账号{qq}。')

    async def logout(self):
        """WebHook 不需要登出。直接返回。"""
        logger.info(f"[WebHook] 从账号{self.session}退出。")

    async def call_api(self, api: str, method: Method = Method.GET, **params):
        """调用 API。WebHook 的 API 调用只能在快速响应中发生。"""
        if self.enable_quick_response:
            content = {'command': api.replace('/', '_'), 'content': params}
            if method == Method.RESTGET:
                content['subCommand'] = 'get'
            elif method == Method.RESTPOST:
                content['subCommand'] = 'update'

            logger.debug(f'[WebHook] WebHook 快速响应 {api}。')
            raise WebHookAdapter.QuickResponse(content)
        return None

    async def _background(self):
        """WebHook 不需要事件循环。直接返回。"""

    async def handle_event(self, event):
        try:
            for bus in self.buses:
                await bus.emit(event['type'], event)
        except WebHookAdapter.QuickResponse as response:
            # 快速响应，直接返回。
            return response.data

        return {}
