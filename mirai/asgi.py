# -*- coding: utf-8 -*-
"""此模块提供公共 ASGI 前端。"""
import asyncio
import functools
import logging
from inspect import iscoroutinefunction
from typing import (
    Awaitable, Callable, Dict, List, Literal, Optional, Tuple, Union, cast
)

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

    async def _global_endpoint(self, key, request: Request):
        for endpoint in self._routes[key]:
            result = await endpoint(request)
            if result:
                return result
        return RedirectResponse(
            'https://yiri-mirai.vercel.app', status_code=301
        )

    def add_route(
        self,
        path: str,
        endpoint: Callable,
        methods: Optional[List[str]] = None
    ) -> 'ASGI':
        """添加路由。

        Args:
            path: 路由的路径。
            endpoint: 路由的处理函数。
            methods: 路由的请求方法。默认为 `['GET']`。

        Returns:
            ASGI: 返回自身。
        """
        methods = methods or ['GET']

        for method in methods:  # 拆分不同的 method
            key = (path, method)
            if key in self._routes:
                self._routes[key].append(endpoint)
            else:
                self._routes[key] = [endpoint]
                self.app.add_route(
                    path,
                    functools.partial(self._global_endpoint, key),
                    methods=[method]
                )

        return self

    def add_event_handler(
        self,
        event_type: Literal["startup", "shutdown"],
        handler: Optional[Callable] = None
    ):
        """注册生命周期事件处理函数。

        Args:
            event_type(`Literal["startup", "shutdown"]`): 事件类型，可选值为 `"startup"` 或 `"shutdown"`。
            handler(`Optional[Callable]`): 事件处理函数，省略此参数以作为装饰器调用。
        """
        if handler:
            self.app.add_event_handler(event_type, handler)
            return self

        # 装饰器用法
        def decorator(func):
            self.app.add_event_handler(event_type, func)
            return func

        return decorator

    def add_background_task(
        self, func: Union[Callable, Awaitable, None] = None
    ):
        """注册背景任务，将在 bot 启动后自动运行。

        Args:
            func(`Union[Callable, Awaitable, None]`): 背景任务，可以是函数或者协程，省略参数以作为装饰器调用。
        """
        if func is None:

            def decorator(func_):
                self.add_background_task(func_)
                return func_

            return decorator

        if iscoroutinefunction(func):  # 异步调用转化为传入协程
            func = cast(Callable[..., Awaitable], func)()

        if callable(func):
            self.app.add_event_handler('startup', func)
        else:
            _task: Optional[asyncio.Task] = None

            async def _startup():
                nonlocal _task
                _task = asyncio.create_task(func)
                # 不阻塞

            async def _shutdown():
                if _task and not _task.done():
                    _task.cancel()

            self.app.add_event_handler('startup', _startup)
            self.app.add_event_handler('shutdown', _shutdown)

        return func

    def mount(self, path: str, app: Callable) -> 'ASGI':
        """挂载另一个 ASGI 服务器。通过这个方法，可以同时运行 FastAPI 之类的服务。

        Args:
            path: 要挂载的路径。
            app: 要挂载的 ASGI 服务器。

        Returns:
            ASGI: 返回自身。
        """
        if not path.startswith('/'):
            path = '/' + path
        self.app.mount(path, app)
        logger.debug(f'向 {path} 挂载 {app}。')
        return self

    async def __call__(self, scope, recv, send):
        await self.app(scope, recv, send)


# noinspection PyUnresolvedReferences
def asgi_serve(
    app,
    host: str = '127.0.0.1',
    port: int = 8000,
    asgi_server: str = 'auto',
    **kwargs
):
    """运行一个 ASGI 服务器。

    Args:
        app: ASGI 应用程序。
        host: 服务器地址，默认为 127.0.0.1。
        port: 服务器端口，默认为 8000。
        asgi_server: ASGI 服务器，可选的有 `hypercorn` `uvicorn` 和 `auto`。
            如果设置为 `auto`，自动寻找是否已安装可用的 ASGI 服务（`unicorn` 或 `hypercorn`），并运行。
    """
    if asgi_server == 'auto':
        try:
            from uvicorn import run
            asgi = 'uvicorn'
        except ImportError:
            try:
                import hypercorn.config as config
                from hypercorn.asyncio import serve
                asgi = 'hypercorn'
            except ImportError:
                asgi = 'none'
    else:
        asgi = asgi_server
        if asgi_server == 'uvicorn':
            from uvicorn import run
        elif asgi_server == 'hypercorn':
            import hypercorn.config as config
            from hypercorn.asyncio import serve

    if asgi == 'uvicorn':
        run(app, host=host, port=port, debug=True, **kwargs)
        return True
    if asgi == 'hypercorn':
        import asyncio
        m_config = config.Config().from_mapping(bind=f'{host}:{port}', **kwargs)
        asyncio.run(serve(app, m_config), debug=True)
        return True
    return False
