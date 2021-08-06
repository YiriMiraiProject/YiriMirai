---
sidebar_position: 6
---

# 四：使用机器人管理群

使用机器人管理群，可以说是机器人最常见的应用之一了。这一节，我们将实现一个简单的群管理机器人。

## 预期的功能

我们要实现最简单的群管理功能：垃圾信息撤回与警告。

## 垃圾信息判断

我们使用百度云的文本审核 API。和上一节一样，外部 API 的调用方式不是重点，这里只放代码，细节略过。

```python
from functools import lru_cache

import httpx


@lru_cache()
def get_access_token(api_key, secret_key):
    url = 'https://aip.baidubce.com/oauth/2.0/token'
    params = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': secret_key,
    }
    resp = httpx.get(url, params=params)
    resp.raise_for_status()
    return resp.json()['access_token']

BD_API_KEY = '你的 API KEY'
SECRET_KEY = '你的 SECRET KEY'

async def text_censor(s: str) -> bool:
    """文本审核。返回 True 表示文本无问题。"""
    access_token = get_access_token(BD_API_KEY, SECRET_KEY)
    url = "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                url, params={'access_token': access_token}, data={'text': s}
            )
            resp.raise_for_status()
            return resp.json()['conclusionType'] != 2
        except (httpx.NetworkError, httpx.HTTPStatusError, KeyError):
            return True
```

*其实只检查 `conclusionType` 有点过于严格了，这里仅作为示例，实际应用中还需要检查其他信息，进行辅助判断。*

## 调用 API

我们先模仿上一节的方式，搭好一个基本的框架：

```python
@bot.on(GroupMessage)
async def text_censor_event(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    if not await text_censor(msg):
        ...
```

### 撤回消息

判断出文本是垃圾信息之后，我们需要调用 API 来撤回这条消息。

但是，如果你去翻一下 YiriMirai 的源码或者 API 文档，会发现 Mirai 类没有像 `send` 一样提供一个撤回消息的方法。

……当然我们没有理由不支持撤回消息。实际上，用 `bot.recall` 就可以撤回消息。

但是为什么找不到这个方法的定义呢？因为 YiriMirai 的很多方法都是“动态”的，Mirai 类通过 `__getattr__` 方法，直接将方法调用与 mirai-api-http 的接口绑定。

因此，你可以在 mirai-api-http 的[文档](https://docs.mirai.mamoe.net/mirai-api-http/api/API.html)中寻找你需要的 API，然后直接用 `bot.API名称` 调用即可。

所以，要撤回消息，可以这样写：

```python
await bot.recall(event.message_chain.message_id)
```

:::tip 异步
YiriMirai 中所有的 API 调用都是异步的，必须要 `await` 才能真正调用。
:::

:::tip 错误处理
机器人在群里撤回其他人的消息，需要机器人有管理员权限。当机器人权限不足，或者尝试撤回其他管理员的消息时，会因为权限不足引发 `ApiError` 异常。

我们认为权限判断和异常处理应该是使用者的工作。你可以像这样捕获这个异常：

```python
from mirai.exceptions import ApiError

try:
    await bot.recall(event.message_chain.message_id)
except ApiError:
    pass
```
:::

### 发送私聊消息

撤回消息之后，我们先在群中发送一条警告：

```python
await bot.send(event, f'{event.sender.member_name}，不能说奇怪的话哟~')
```

然后机器人以私聊消息的形式，向你的账号发送一条报告。

这听起来不难，但是看一看 `bot.send` 方法的定义，你会发现它没有通过 QQ 号发送消息的功能。

这是因为 `bot.send` 不是 mirai-api-http 提供的 API，而是 YiriMirai 提供的一个简便方法。它实际上是对 `send_friend_message` `send_group_message` `send_temp_message` 等 API 的封装。如果只给定一个账号，不能确定这到底是 QQ 号还是群号，`send` 就无法调用合适的方法。

所以，想要向给定的账号发送私聊消息，要使用 `send_friend_message` 这个 API。幸运的是，YiriMirai 有良好的封装，`send_friend_message` 和 `send` 用起来几乎一样方便。

```python
await bot.send_friend_message(12345678, f'检测到异常发言: {repr(event)}') # 改成你的 QQ 号
```

:::tip 名称转写
在 mirai-api-http 的文档中，可以发现发送私聊消息的接口名称是 `sendFriendMessage`，但是这里我们用的是 `send_friend_message`。这是为什么呢？

**为了符合 PEP 8 规范，YiriMirai 对所有的 API 都进行了名称转写，全部使用小写字母和下划线分隔**。例如，`sendFriendMessage` 转写为 `send_friend_message`；`file/info` 转写为 `file_info`。API 的原始名称与转写后的名称都是可以通过点号调用的，除非原始名称带有斜杠。你可以仿照这个例子，得出其他 API 的命名。
:::

现在我们把调用 API 的部分综合起来，完成消息处理器：

```python
from mirai.exceptions import ApiError

@bot.on(GroupMessage)
async def text_censor_event(event: GroupMessage):
    msg = "".join(map(str, event.message_chain[Plain]))
    if not await text_censor(msg):
        try:
            await bot.recall(event.message_chain.message_id)
        except ApiError:
            pass
        await bot.send(event, f'{event.sender.member_name}，不能说奇怪的话哟~')
        await bot.send_friend_message(12345678, f'检测到异常发言: {repr(event.sender)}') # 改成你的 QQ 号
```

## 总结

这一节我们为机器人实现了简单的群反垃圾信息功能。

本节的示例代码在[这里](/examples/04.md)。

准备好了的话，就前往下一节吧。