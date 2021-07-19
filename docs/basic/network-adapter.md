---
sidebar_position: 3.5
---

# 接口适配器

在 mirai-api-http 2.X 版本中，将不同的连接方式拆分为 4 种接口适配器（adapter）。YiriMirai 针对 mirai-api-http 的接口适配器，设计了 `Adapter` 类。

当前版本支持 `HTTPAdapter` 和 `WebSocketAdapter`，对其他接口适配器的支持会在之后版本加入。

## 创建 Adapter

接口适配器定义在 `mirai.adapters` 模块，方便起见，也可从顶层模块 `mirai` 的命名空间中引入。

`Adapter` 是一个抽象类，应使用其子类实例化。

```python
from mirai import HTTPAdapter

adapter = HTTPAdapter(verify_key='your_verify_key', host='localhost', port=8080)
```

### 禁用身份验证

在 mirai-api-http 的配置中设置 `enableVerify: false` 之后，不会对请求进行身份验证。

此时，应在创建适配器时，将 `verify_key` 置为 `None`。

```python
adapter = HTTPAdapter(verify_key=None, host='localhost', port=8080)
```

### Single Mode

再 mirai-api-http 的配置中设置 `singleMode: true` 之后，将启用 Single Mode。

此时，应在创建适配器时，指定 `single_mode=True`。

```python
adapter = HTTPAdapter(verify_key='your_verify_key', host='localhost', port=8080, single_mode=True)
```

### 通过已有的适配器创建

使用 `via` 方法，可以通过一个已有的适配器创建新适配器。

新适配器会尽可能地复制原适配器的信息。

一个特殊的应用是在 `bot.use_adapter` 中，使用 `via` 以快速创建临时适配器。此时 `via` 可以接收 Mirai 对象作为参数，来读取到 Mirai 对象内部的适配器信息。

```python
new_adapter = HTTPAdapter.via(adapter)
# 在 use_adapter 中使用
async with bot.use_adapter(HTTPAdapter.via(bot)):
    ...
```

## Adapter 与事件总线

使用 `register_event_bus` 和 `unregister_event_bus` 方法注册和解注册事件总线。这两个方法都可以接收一个或多个参数，表示一个或多个事件总线。

```python
adapter.register_event_bus(bus1, bus2)
adapter.unregister_event_bus(bus2)
```

`Adapter.buses` 属性是一个 set，表示当前注册到适配器的所有事件总线。

关于事件总线的更多信息，请参考 [事件总线](../advanced/event-bus.mdx)。

在 bot 创建时，会**自动把 bot 的内部事件总线注册入 Adapter 中**。

## Adapter 的其他方法

### login

```python
async def login(self, qq: int):
    ...
```

`login` 方法表示登录到机器人实例。

一般情况下，此方法**无需手动调用**。`bot.run()` 将自动调用此方法。

### logout

```python
async def logout(self):
    ...
```

`logout` 方法表示登出机器人实例。

一般情况下，此方法**无需手动调用**。`bot.run()` 将自动在运行结束时调用此方法。

### call_api

```python
def call_api(self, api: str, method: Method = 'GET', **params) ‑> Union[Awaitable[Any], Any]:
    ...
```

`call_api` 表示调用一个 API，与 `bot.call_api()` 相同。

### register_event_bus

```python
def register_event_bus(self, *buses: List[EventBus]):
    ...
```

## HTTPAdapter

`HTTPAdapter` 是 `Adapter` 的子类，对应 mirai-api-http 中的 http 轮询。

### 创建

```python
adapter = HTTPAdapter(verify_key='your_verify_key', host='localhost', port=8080)
```

`verify_key` 与 mirai-api-http 的配置一致。`host` 和 `port` 与 mirai-api-http 中 http adapter 的配置一致。

## WebSocketAdapter

`WebSocketAdapter` 是 `Adapter` 的子类，对应 mirai-api-http 中的正向 websocket 连接，YiriMirai 作为 websocket 客户端，mirai-api-http 作为 websocket 服务端。

### 创建

```python
adapter = WebSocketAdapter(verify_key='your_verify_key', host='localhost', port=8080, sync_id='-1')
```

`verify_key` 与 mirai-api-http 的配置一致。`host` 和 `port` 与 mirai-api-http 中 wensocket adapter 的配置一致。

`sync_id` 与 mirai-api-http 中 websocket adapter 的配置一致。需注意，mirai-api-http 默认的 sync_id 为字符串 `'-1'`。

## WebHookAdapter

`WebHookAdapter` 是 `Adapter` 的子类，对应 mirai-api-http 中的 HTTP 事件上报。

### 创建

```python
adapter = WebHookAdapter(verify_key='your_verify_key', route='/post/', extra_headers={'Authorization': 'bearer AAAAAA'})
```

`verify_key` 与 mirai-api-http 的配置一致。

`route` 表示 WebHook 工作的路由。如设置为 `/post/`，表示在 `http://[BASEURI]/post/` 上接收 WebHook 事件，其中 `[BASEURI]` 为 WebHook 工作的地址。

`extra_headers` 表示 WebHook 事件上报时附带的额外头信息，与 mirai-api-http 的 webhook adapter 的配置一致。

### 启动服务

WebHook Adapter 工作的地址和端口在 `bot.run` 中指定。

```python
bot.run(host='localhost', port=8080)
```

当 WebHook Adapter 的 `route` 设置为 `/post/` 时，会在 `http://localhost:8080/post/` 上接收 WebHook 事件。

或者使用 ASGI 服务器，在启动 ASGI 服务器时指定地址和端口。

```shell
uvicorn main:app --host 127.0.0.1 --port 8080
```

## 适配器组合

`ComposeAdapter` 是 `Adapter` 的子类，使用这个适配器，可以将用一个适配器调用 API，另一个适配器接收事件。

一种常用的组合方式是 HTTP Adapter 与 WebHook 的组合：

```python
adapter = ComposeAdapter(
    api_channel=HTTPAdapter(
        verify_key='your_verify_key', host='127.0.0.1', port=6090
    ),
    event_channel=WebHookAdapter(
        verify_key='your_verify_key',
        extra_headers={'authorization': 'Bearer AAAAAAA'},
        enable_quick_response=False
    )
)
```

`api_channel` 与 `event_channel` 为 `Adapter` 实例，前者调用 API，后者接收事件。

组合的适配器必须设置相同的 `verify_key`。

:::tip
WebHook Adapter 用于组合时，只能做接收事件的适配器。

此时，将 `enable_quick_response` 参数设置为 `False`，禁用 WebHook 的事件快速响应，可以提高事件处理的效率。

这**并不影响**正常的快速响应的使用。快速响应仍然可用，它将通过 `api_channel` 调用 API。
:::
