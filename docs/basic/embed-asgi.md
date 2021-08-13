---
sidebar_position: 3.6
---

# 嵌入 ASGI 服务

YiriMirai 内部维护了一个 ASGI 服务。在 [`mirai.asgi`](https://yiri-mirai-api.vercel.app/asgi.html) 模块可以找到它的定义。

`mirai.asgi` 中定义了一个单例类 `ASGI`，它是 YiriMirai 中所有 ASGI 服务的公共前端。

可以像这样获取到它的实例：

```python
from mirai.asgi import ASGI

asgi = ASGI()
```

使用它的 `mount` 方法，可以把另一个 ASGI 服务器挂载到子路由上，从而实现嵌入其他的 ASGI 服务。

比如和 FastAPI 协作：

```python
from fastapi import FastAPI
from mirai.asgi import ASGI
from mirai import Mirai

bot = Mirai(...)
app = FastAPI()

@app.get('/')
async def test():
    await bot.send_friend_message(...)
    return {'message': 'Hello, FastAPI!'}

asgi = ASGI()
asgi.mount('/fastapi', app)

bot.run(host='127.0.0.1', port=8080)
```

这样就可以在 `http://127.0.0.1:8080/fastapi/` 上访问 FastAPI 了。
