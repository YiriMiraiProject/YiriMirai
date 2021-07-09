---
sidebar_position: 3.4
---

# 接口适配器

在 mirai-api-http 2.X 版本中，将不同的连接方式拆分为 4 种接口适配器（adapter）。YiriMirai 针对 mirai-api-http 的接口适配器，设计了 `Adapter` 类。

当前版本仅支持 `HTTPAdapter`，对其他接口适配器的支持会在之后版本加入。

## 创建 Adapter

接口适配器定义在 `mirai.adapters` 模块，方便起见，也可从顶层模块 `mirai` 的命名空间中引入。

`Adapter` 是一个抽象类，应使用其子类实例化。

```python
from mirai import HTTPAdapter

adapter = HTTPAdapter(verify_key='your_verify_key', host='localhost', port=8080)
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

### run

```python
async def run(self):
    ...
```

`run` 方法表示运行。同样，此方法**无需手动调用**，将在`bot.run()` 中自动调用。

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

`verify_key` 与与 mirai-api-http 的配置一致。`host` 和 `port` 与 mirai-api-http 中 http adapter 的配置一致。
