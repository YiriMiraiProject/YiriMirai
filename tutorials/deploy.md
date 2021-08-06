---
sidebar_position: 7
---

# 五：多适配器与部署

这一节，我们介绍如何在生产环境部署 YiriMirai。

## 前置知识

本节需要你对 ASGI 有所了解。你可以阅读 ASGI 标准的[文档](https://asgi.readthedocs.io/en/latest/)，如果觉得有点难懂，也可以先看看 uvicorn 的[文档](https://www.uvicorn.org)。

## 作为 ASGI 服务启动

前几节中，我们都是使用 `bot.run` 来启动机器人。这种启动方式并不适合在生产环境中使用。我们建议在生产环境中，将机器人作为 ASGI 服务启动。

`Mirai` 类提供了 `asgi` 属性，这个属性是一个 ASGI 服务。你可以使用 uvicorn 这样的工具启动它：

```python title='main.py'
from mirai import Mirai

bot = Mirai(...)

app = bot.asgi
```

在命令行中输入：

```shell
uvicorn main:app
```

这样，你就可以使用一些 uvicorn 提供的高级特性，比如自动重连：

```shell
uvicorn main:app --reload
```

## 适配器

mirai-api-http 2 提供了四种连接方式，称为“适配器”。YiriMirai 目前实现了其中三种的对接：HTTP 适配器、websocket 适配器，以及 WebHook 适配器。

### 使用适配器

| 名称             | 类名               | 描述                                                                        |
| ---------------- | ------------------ | --------------------------------------------------------------------------- |
| HTTP 适配器      | `HTTPAdapter`      | YiriMirai 作为客户端，向 mirai-api-http 发送 HTTP 请求                      |
| websocket 适配器 | `WebSocketAdapter` | YiriMirai 作为客户端，与 mirai-api-websocket 建立 websocket 连接            |
| WebHook 适配器   | `WebHookAdapter`   | YiriMirai 作为服务器，由 mirai-api-http 向 YiriMirai 通过 HTTP 请求上报事件 |

回忆一下第一节里创建 Mirai 实例的代码：

```python
from mirai import Mirai, WebSocketAdapter

bot = Mirai(
    qq=12345678, # 改成你的机器人的 QQ 号
    adapter=WebSocketAdapter(
        verify_key='yirimirai', host='localhost', port=8080
    )
)
```

可以把适配器创建单独拿出来：

```python
from mirai import Mirai, WebSocketAdapter

adapter = WebSocketAdapter(
    verify_key='yirimirai', host='localhost', port=8080
)
bot = Mirai(
    qq=12345678, # 改成你的机器人的 QQ 号
    adapter=adapter
)
```

#### HTTPAdapter

使用 `HTTPAdapter` 与之类似。不过，在使用之前，需要编辑 mirai-api-http 的配置。找到 `setting.yml`，编辑其中的 `adapters` 和 `adapterSettings` 部分：

```yaml title='setting.yml'
adapters:
  - http
  - ws
debug: true
enableVerify: true
verifyKey: yirimirai
singleMode: false
cacheSize: 4096
adapterSettings:
  http:
    host: localhost
    port: 8080
    cors: [*]
  ws:
    host: localhost
    port: 8080
    reservedSyncId: -1
```

然后就可以启用 HTTP 适配器了：

```python
from mirai import Mirai, HTTPAdapter

adapter = HTTPAdapter(
    verify_key='yirimirai', host='localhost', port=8080
)
bot = Mirai(
    qq=12345678, # 改成你的机器人的 QQ 号
    adapter=adapter
)
```

#### WebHookAdapter

使用 WebHook 适配器，需要安装 uvicorn 或 hypercorn 或其他 ASGI 服务器。

同样地，在 `setting.yml` 中，需要编辑 `adapters` 和 `adapterSettings` 部分，增加 WebHook 适配器：

```yaml title='setting.yml'
adapters:
  - http
  - webhook
debug: true
enableVerify: true
verifyKey: yirimirai
singleMode: false
cacheSize: 4096
adapterSettings:
  http:
    host: localhost
    port: 8080
    cors: [*]
  webhook:
    destinations:
      - http://localhost:8081/

    # extraHeaders:
    #   Authorization: 'bearer SV*(&*(SH@ID^G'
```

WebHook 适配器在创建时，不需要指定 `host` 和 `port`，其工作的位置和端口由 `bot.run` 的参数指定，或者在 uvicorn 等的启动参数里指定。

```python
from mirai import Mirai, WebHookAdapter

adapter = WebHookAdapter(
    verify_key='yirimirai'
)
bot = Mirai(
    qq=12345678, # 改成你的机器人的 QQ 号
    adapter=adapter
)

bot.run(port=8081)
```

:::note 额外请求头
在 mirai-api-http 的 `setting.yml` 的 webhook 配置中，可以设置一系列的 extraHeaders。这些额外请求头没有实际含义，仅用来作为权限认证。

在 YiriMirai 创建 WebHook 适配器时，可以指定一个 `extra_headers` 参数，只有当这两处的配置一致时，YiriMirai 才会处理 WebHook 请求。

```python
adapter = WebHookAdapter(
    verify_key='yirimirai',
    extra_headers={'Authorization': 'bearer SV*(&*(SH@ID^G'}
)
```

:::

### 在指定端口启动

在 WebHook 适配器下，YiriMirai 要作为服务器启动，因此需要指定一个端口。

`bot.run` 有两个可选参数 `host` 和 `port`，可以指定服务器的 IP 和端口。默认的端口是 8080。

```python
bot.run(host='127.0.0.1', port=8080)
```

使用 uvicorn 等方式启动时，可以在 uvicorn 的命令中使用 `--host` 和 `--port` 指定服务器的 IP 和端口。

```shell
uvicorn main:app --host=127.0.0.1 --port=8080
```

:::note 端口冲突
在安装 uvicorn 之后，`bot.run` 的行为会改为通过 uvicorn 启动。这时候，即使不使用 WebHook 适配器，也会占用相应的端口，比如默认情况下，YiriMirai 启动时会占用 8080 端口。

为了避免端口冲突，你可以用 `port` 参数指定一个不同的端口。
:::

### 临时切换适配器

前几节中，我们都是使用的 `WebSocketAdapter`，通过 websocket 与 mirai-api-http 连接，这是最方便的一种方式。

不过，websocket 适配器存在一些限制，比如某些 API 不支持 websocket。

这种情况下，我们可以使用 `bot.use_adapter` 方法，临时启用 HTTP 适配器：

```python
async with bot.use_adapter(HTTPAdapter.via(bot)):
    image = await bot.upload_image('friend', './images/1.png')
```

这里使用了适配器的 `via` 类方法，这个方法接受一个 `Mirai` 对象或另一个适配器作为参数，并返回一个新的适配器实例，这个新的适配器实例会尽可能地复制原适配器的信息。

### 适配器组合

更好的方法是不使用 websocket 适配器，而是改为使用其他适配器。

HTTP 适配器在调用 API 上功能最完善，但它默认使用短轮询的方式获取消息，会有一定的性能损失。而 WebHook 适配器可以方便地接收事件，但不能主动调用 API。YiriMirai 提供了一种优势互补的方式，称为“适配器组合”。

目前，HTTP 适配器与 WebHook 适配器的组合是功能最完善的选择。

```python
from mirai import Mirai, HTTPAdapter, WebHookAdapter, ComposeAdapter

adapter = ComposeAdapter(
    api_channel=HTTPAdapter(
        verify_key='yirimirai', host='127.0.0.1', port=6090
    ),
    event_channel=WebHookAdapter(
        verify_key='yirimirai',
        # extra_headers={'authorization': 'bearer SV*(&*(SH@ID^G'},
        enable_quick_response=False
    )
)
bot = Mirai(
    qq=12345678, # 改成你的机器人的 QQ 号
    adapter=adapter
)
```

## 总结

这一节主要讲述了如何在生产环境中部署 YiriMirai，以及多适配器的用法。

到这里，YiriMirai 的教程就结束了，虽然内容不多，但希望你能有所收获。毕竟这里是一个 SDK 的教程，所以我们把重点放在了 YiriMirai 的用法上，没有太多地关注具体功能的实现。

接下来，你可以去我们的[文档](/docs/intro)看看，你会对 YiriMirai 有更加深入的理解。
