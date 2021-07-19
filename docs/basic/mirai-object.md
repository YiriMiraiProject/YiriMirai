---
sidebar_position: 3.1
---

# Mirai 对象

Mirai 对象表示一个机器人实例。我们要进行的一切操作几乎都是在这个对象上进行的。

`Mirai` 类定义在 `mirai.bot` 模块，同时也存在于顶层模块 `mirai` 的命名空间中，你可以通过 `from mirai import Mirai` 来导入。

## 创建 Mirai 对象

`Mirai` 类的构造函数包含两个参数：`qq` 和 `adapter`。`qq` 是机器人的 QQ 号，类型为整数。`adapter` 是网络适配器。

```python
from mirai import Mirai, HTTPAdapter

adapter = HTTPAdapter(verify_key='your_verify_key', host='localhost', port=8080)
bot = Mirai(qq=12345678, adapter=adapter)
```

## 调用 API

可以直接通过在 Mirai 对象上使用点号调用 mirai-api-http 的 API。

```python
await bot.send_group_message(12345678, [Plain('Hello, World!')]) # 发送群消息
profile = await bot.bot_profile.get() # 获取机器人账号的资料
```

更多信息，查看[调用 API](call-api.md)章节。

### 临时适配器切换

某些特殊的 API，比如 `upload_image` 和 `upload_voice` 只能在 HTTP 适配器下工作。如果想要在其他适配下使用这些 API，可以用 `use_adpter` 方法临时切换适配器。

`use_adapter` 返回一个异步上下文对象，用于 `async with` 中。

```python
async with bot.use_adapter(HTTPAdapter.via(bot)):
    ...
```

## 处理事件

Mirai 对象的 `on` 方法用于注册事件处理器。

```python
from mirai import GroupMessage

# 接受群消息
@bot.on(GroupMessage)
async def handle_group_message(event: GroupMessage):
    print(str(event.message_chain)) # 打印消息内容
```

更多信息，查看[事件处理](event-handling.mdx)章节。

## 运行

### 使用 run 方法

使用 `run` 方法启动机器人。

```python
bot.run()
```

当使用 WebHook 时，在此处指定 WebHook 的地址和端口。

```python
bot.run(host='127.0.0.1', port=8081)
```

:::tip 端口冲突
即使不使用 WebHook，在不指定 `run` 的参数时，Mirai 默认占用 `localhost:8080` 的端口。

如果遇到端口冲突无法启动，试着指定一个别的端口。
:::

### 使用 ASGI 服务器

另一种方式是使用 `bot.asgi`，这一属性可访问到 bot 的 ASGI 实例。

可以使用 `uvivorn` 或 `hypercorn` 等 ASGI 服务器运行机器人。

```python main.py
from mirai import Mirai
bot = Mirai(...)

...

app = bot.asgi
```

在命令行运行：

```shell
uvicorn main:app --host 127.0.0.1 --port 8081
# 或者
hypercorn main:app --bind 127.0.0.1:8081
```

:::note 在 run 方法中使用 ASGI
当你安装了 uvicorn 或 hypercorn 时，`bot.run` 会自动使用 ASGI 的方式启动。

默认优先使用 uvicorn。可以通过参数 `asgi_server` 来控制使用的服务器。此参数的默认值为 `auto`，表示自动选择（uvicorn 优先）；设置为 `uvicorn` 或 `hypercorn` 则使用指定的服务器。

`asgi_server` 设置为其他值，或未找到可用的 ASGI 服务器，将禁用 ASGI。此时，WebHook 将不可用。

```python
bot.run(host='127.0.0.1', port=8081, asgi_server='uvicorn')
```
:::

### 多例运行

使用 `MiraiRunner` 类可以同时运行多个 Mirai 对象。

```python
from mirai import MiraiRunner
bot1 = Mirai(...)
bot2 = Mirai(...)

runner = MiraiRunner(bot1, bot2)
runner.run()
```

`MiraiRunner` 的 `run` 方法的参数与 `bot.run` 的参数相同。

:::tip
`MiraiRunner` 本身是一个 ASGI 实例，可以用于 uvicorn 等 ASGI 服务器。

```shell
uvicorn main:runner --host 127.0.0.1 --port 8081
```
:::

:::caution
`MiraiRunner` 是单例类，请不要使用不同的参数多次创建 `MiraiRunner` 实例。
:::

## SimpleMirai

SimpleMirai 是工作在模型层之下的 Mirai。

:::note
模型层（model 层）提供了对 mirai-api-http 发回的原始数据的封装，让我们可以以更加 pythonic 的方式来处理这些数据。

关于模型层的更多信息，参看[YiriMirai 的架构](../advanced/structure-of-yiri-mirai.mdx)章节。
:::

SimpleMirai 不含模型层封装，这意味着一切都必须和 mirai-api-http 的原始定义一致，并且只能使用基本类型，比如 dict 来描述数据。

创建 SimpleMirai 对象和创建 Mirai 对象的方式相同：

```python
from mirai import SimpleMirai, HTTPAdapter

adapter = HTTPAdapter(verify_key='your_verify_key', host='localhost', port=8080)
bot = SimpleMirai(qq=12345678, adapter=adapter)
```

SimpleMirai 对象也可以通过 `on` 注册事件处理器，但由于没有模型层封装，所以**只能使用字符串型的事件名称**，并且不会发生[事件传播](event-handling.mdx#事件传播)。

SimpleMirai 的事件处理器接收到的 `event` 参数是字典类型，存放 mirai-api-http 发回的原始数据。

```python
@bot.on('FriendMessage')
async def handle_group_message(event: dict):
    print(f"收到来自{event['sender']['nickname']}的消息。")

# # FriendMessage 不会被传播到 Event
# @bot.on('Event')
# async def handle_event(event: dict):
#     print("这里不会被执行。")
```

SimpleMirai 对象也能通过点号调用 API。此时，API 的名称必须与 mirai-api-http 的原始定义一致，比如，只能使用 `bot.sendFriendMessage` 而不能使用 `bot.send_friend_message`。同时，必须指出 API 的[类型](call-api.md#api-类型)（GET/POST）。

```python
await bot.sendGroupMessage(target=12345678, messageChain=[
    {'type': 'Plain', 'text': 'Hello, World!'}
], method='POST')
```

对于名称中含有 `/` 的 API，需要使用 `call_api` 方法。

```python
file_list = await bot.call_api('file/list', id="", target=12345678, method='GET')
```
