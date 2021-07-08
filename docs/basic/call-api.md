---
sidebar_position: 3.3
---

# 调用 API

## 直接调用

可以直接通过在 `Mirai` 对象上使用点号调用 mirai-api-http 的 API。

```python
await bot.send_group_message(12345678, [Plain('Hello, World!')]) # 发送群消息
profile = await bot.bot_profile.get() # 获取机器人账号的资料
```

API 名称与 mirai-api-http 中的定义一致，但经过了转写以符合 PEP 8 的风格，采用**小写字母和下划线分隔**。例如，`sendFriendMessage` 转写为 `send_friend_message`；`file/info` 转写为 `file_info`。API 的原始名称与转写后的名称都是可以通过点号调用的，除非原始名称带有斜杠。

对 API 的调用**全部都是异步的**。所以，不要忘记 `await`。

### API 类型

API 分为三类：GET 类型，POST 类型，以及 RESTful 类型。像上面的 `send_group_message` 和 `send_friend_message` 是 POST 类型的，`bot_profile` 是 GET 类型的。

对于 GET 和 POST 类型的 API，可以直接像函数一样调用。GET 类型的 API 也可以通过 `get` 方法调用。

```python
profile = await bot.bot_profile.get()
# 这两句是等价的。
profile = await bot.bot_profile()
```

POST 类型的 API 也可以通过 `set` 方法调用。

```python
await bot.send_group_message(12345678, [Plain('Hello, World!')])
# 这两句是等价的。
await bot.send_group_message.set(12345678, [Plain('Hello, World!')])
```

:::tip
出于语义准确性的考虑，我们更推荐用 `get` 方法调用 GET 类型 API，而直接像函数一样调用 POST 类型 API。

```python {1,5}
profile = await bot.bot_profile.get() # 这是推荐的写法。
# 这两句是等价的。
profile = await bot.bot_profile()

await bot.send_group_message(12345678, [Plain('Hello, World!')]) # 这是推荐的写法。
# 这两句是等价的。
await bot.send_group_message.set(12345678, [Plain('Hello, World!')])
```
:::

对于 RESTful 类型的 API，通过 `get` 方法获取值，通过 `set` 方法修改值。

```python
config = await bot.group_config(12345678).get() # 获取群设置
await bot.group_config(12345678).set(config.modify(announcement='测试')) # 修改群设置，将入群公告改为“测试”
```

:::tip
可用的 API 列表，可以在 mirai-api-http 的[文档](https://project-mirai.github.io/mirai-api-http/adapter/HttpAdapter.html)中查看。

其中，标记为 `[GET]` 的是 GET 类型 API，标记为 `[POST]` 的是 POST 类型 API，既有 `[GET]` 又有 `[POST]` 的是 RESTful 类型 API。
:::

## 调用 API 的其他方式

### `api` 方法

使用 `api` 方法是调用 API 的另一种方式。事实上，上述通过点号调用 API 的方式就是通过在 `__getattr__` 中调用 `api` 方法实现的。

```python
profile = await bot.bot_profile.get()
# 这两句是等价的。
profile = await bot.api('bot_profile').get()

await bot.send_group_message(12345678, [Plain('Hello, World!')])
# 这两句是等价的。
await bot.api('send_group_message')(12345678, [Plain('Hello, World!')])
```

### `call_api` 方法

与 `api` 不同，`call_api` 定义在 `SimpleMirai` 中。这意味着它没有 model 层封装，也就是说，必须使用 mirai-api-http 中定义的原始名称，并指定使用的方法（GET/POST），而且参数只能通过具名参数传入，具有复杂数据格式的参数只能使用字典表示。

```python
await bot.call_api('sendGroupMessage', target=12345678, messageChain=[
    {'type': 'Plain', 'text': 'Hello, World!'}
], method='POST')
```
