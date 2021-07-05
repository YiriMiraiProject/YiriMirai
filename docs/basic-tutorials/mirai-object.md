---
sidebar_position: 3.1
---

# Mirai 对象

Mirai 对象表示一个机器人实例。我们要进行的一切操作几乎都是在这个对象上进行的。

`Mirai` 类定义在 `mirai.bot` 模块，同时也存在于顶层模块 `mirai` 的命名空间中，你可以通过 `from mirai import Mirai` 来导入。

## 创建 Mirai 对象

`Mirai` 类的构造函数包含两个参数：`qq` 和 `adapter`。`qq` 是机器人的 QQ 号，类型为整数。`adapter` 是网络适配器，当前版本支持 `HTTPAdapter`。

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

使用 `run` 方法启动机器人。

```python
bot.run()
```

一般情况下，`run` 方法不再返回。

## SimpleMirai

SimpleMirai 是工作在模型层之下的 Mirai。

:::note
模型层（model 层）提供了对 mirai-api-http 发回的原始数据的封装，让我们可以以更加 pythonic 的方式来处理这些数据。

关于模型层的更多信息，参看[YiriMirai 的架构](..\advanced-tutorials\structure-of-yiri-mirai.md)章节。
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
    print(f"收到来自{event['sender']['nickname']的消息。}")

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