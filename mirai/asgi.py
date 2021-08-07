# -*- coding: utf-8 -*-
"""此模块提供公共 ASGI 前端。"""

import logging
from typing import Callable, Dict, List, Optional, Tuple, Union

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse

from mirai.utils import Singleton

logger = logging.getLogger(__name__)


async def default_endpoint(_: Request):
    return


class ASGI(Singleton):
    """单例类。公共 ASGI 前端。

    对 Starlette 功能的一个扩充，支持当某一个 endpoint 无返回时，调用其他同一路由的 endpoint。
    """

    app: Starlette
    """内部的 Starlette 实例。"""
    def __init__(self):
        self.app = Starlette()
        self._routes: Dict[Tuple[str, str], List[Callable]] = {}

        self.add_route('/', default_endpoint)

    def add_route(
        self,
        path: str,
        endpoint: Callable,
        methods: Optional[List[str]] = None
    ):
        """添加路由。

        `path: str` 路由的路径。

        `endpoint: Callable` 路由的处理函数。

        `methods: Optional[List[str]] = None` 路由的请求方法。默认为 `['GET']`。
        """
        methods = methods or ['GET']

        for method in methods: # 拆分不同的 method
            key = (path, method)
            if self._routes.get(key):
                self._routes[key].append(endpoint)
            else:
                self._routes[key] = [endpoint]

                async def global_endpoint(request: Request):
                    for endpoint in self._routes[key]:
                        result = await endpoint(request)
                        if result:
                            return result
                    else:
                        return RedirectResponse(
                            'https://yiri-mirai.vercel.app', status_code=301
                        )

                self.app.add_route(path, global_endpoint, methods=[method])

        return self

    def add_event_handler(self, event_type: str, handler: Callable):
        """注册生命周期事件处理函数。"""
        self.app.add_event_handler(event_type, handler)
        return self

    def mount(self, path: str, app: Callable):
        """挂载另一个 ASGI 服务器。通过这个方法，可以同时运行 FastAPI 之类的服务。

        `path: str` 要挂载的路径。

        `app: Callable` 要挂载的 ASGI 服务器。
        """
        self.app.mount(path, app)
        logger.debug(f'向 {path} 挂载 {app}。')
        return self

    async def __call__(self, scope, recv, send):
        await self.app(scope, recv, send)


def asgi_serve(
    app,
    host: str = '127.0.0.1',
    port: int = 8000,
    asgi_server: str = 'auto',
    **kwargs
):
    """运行一个 ASGI 服务器。

    `app` ASGI 应用程序。

    `host: str = '127.0.0.1'` 服务器地址。

    `port: int = 8000` 服务器端口。

    `asgi_server='auto'` ASGI 服务器，可选的有 `hypercorn` `uvicorn` 和 `auto`。
        如果设置为 `auto`，自动寻找是否已安装可用的 ASGI 服务（`unicorn` 或 `hypercorn`），并运行。
    """
    if asgi_server == 'auto':
        try:
            from uvicorn import run
            asgi = 'uvicorn'
        except ImportError:
            try:
                from hypercorn.asyncio import serve
                from hypercorn.config import Config
                asgi = 'hypercorn'
            except ImportError:
                asgi = 'none'
    else:
        asgi = asgi_server

    if asgi == 'uvicorn':
        run(app, host=host, port=port, debug=True, **kwargs)
        return True
    elif asgi == 'hypercorn':
        import asyncio
        config = Config().from_mapping(bind=f'{host}:{port}', **kwargs)
        asyncio.run(serve(app, config), debug=True)
        return True
    else:
        return False
