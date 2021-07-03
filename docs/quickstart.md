---
sidebar_position: 2
---

# 快速上手

## 准备工作

YiriMirai 需要 **Python 3.7 及以上版本**。同时，YiriMirai 使用 poetry 进行依赖管理，你需要先安装 [poetry](https://python-poetry.org/)。

YiriMirai 基于 mirai 运行。如果你还没有安装 mirai，我们建议你使用 [mcl-installer](https://github.com/iTXTech/mcl-installer)，支持一键安装，并自带 mirai-api-http。安装完成后，**运行 mirai-console，登录你的机器人账号**。

### 安装

目前，你可以从 Github 上安装 YiriMirai。

```shell
git clone https://github.com/Wybxc/YiriMirai.git
poetry install
```

### 配置

按照 mirai-api-http 的[配置文档](https://project-mirai.github.io/mirai-api-http/)配置 mirai-api-http，启用 http adapter，配置完成后记录你设置的 `verifyKey` ，以及 http adapter 的 `host` 和 `port` 。


## 编写第一个机器人

在你的项目中新建一个`quickstart.py`文件，内容如下：

```python title='quickstart.py'
from YiriMirai import Mirai, HTTPAdapter, FriendMessage, Plain

if __name__ == '__main__':
    bot = Mirai(qq=12345678, adapter=HTTPAdapter(verify_key='your_verify_key', host='localhost', port=8080))

    @bot.on(FriendMessage)
    async def on_friend_message(event: FriendMessage):
        if str(event.message_chain) == '你好':
            await bot.send_friend_message(event.sender.id, [Plain('Hello World!')]

    bot.run()
```

记得把 QQ 号改成你自己的。

运行这个文件：

```shell
python quickstart.py
```

看到如上输出，说明机器人已经开始运行。

试着给你的机器人发送一条“你好”，你的机器人就会发送一条消息“Hello World!”。

## 发生了什么？

:::info
要理解接下来的内容，你需要掌握 Python 异步编程（asyncio）的相关知识。你可以在[这里](https://docs.python.org/3/library/asyncio.html)查看 Python 的 asyncio 官方文档。
:::

我们来看看这段代码的具体运行过程。

首先，我们创建了一个 Mirai 实例，并设置了 QQ 号和 adapter。

adapter 是网络适配器，负责与 mirai-api-http 通信。当前版本只支持 `HTTPAdapter` ，与 mirai-api-http 的 http adapter 对接。

```python
bot = Mirai(qq=12345678, adapter=HTTPAdapter(verify_key='your_verify_key', host='localhost', port=8080))
```

然后，我们定义了一个 `FriendMessage` 类型的事件处理器，并且把它注册到了 Mirai 中。

```python
@bot.on(FriendMessage)
async def on_friend_message(event: FriendMessage):
    if str(event.message_chain) == '你好':
        await bot.send_friend_message(event.sender.id, [Plain('Hello World!')])
```

事件处理器是一个异步函数，接收一个唯一参数 `event`，它是 `FriendMessage` 类型，包含了发送者的 QQ 号和消息。

:::note NOTE: 事件类型
`FriendMessage` 是一个事件类型，它的实例包含事件的信息。

`FriendMessage` 包含 `sender` 属性和 `message_chain` 属性。`sender` 属性是一个 `Friend` 类型，包含了发送者的信息。`message_chain` 属性是一个 `MessageChain` 类型，它包含了发送者发送的消息链。

你可以在 [API 文档](https://yiri-mirai-api.vercel.app/models/events.html#YiriMirai.models.events.FriendMessage)中找到 `FriendMessage` 的定义，并查看它有哪些属性。
:::

:::note
如果你熟悉 pydantic，你会发现 `FriendMessage`、`Event`、`Friend`、`MessageChain` 都是 pydantic 的模型（model）。

YiriMirai 依靠 pydantic 解析 mirai-api-http 发回的数据，并将其转换成 Python 的对象。你可以方便地通过点号访问模型的属性。
:::

这里，我们使用了 `str(event.message_chain)` ，来获取消息链的文本形式。

:::note NOTE: 消息链
因为 QQ 的消息不只是文本形式，所以 mirai 采用了消息链来表示消息。为了与 mirai 保持一致，也为了更好的灵活性，YiriMirai 同样使用消息链来表示消息。

消息链可以看作是一系列消息组件构成的列表。上面我们使用的 `Plain` 就是一个消息组件，它表示一段纯文本。

像上面一样，你可以方便地使用 `str` 将消息链转换为字符串。
:::

接下来，我们创建了一个包含 `Plain` 类型的消息链，并且把它发送给了好友。

```python
await bot.send_friend_message(event.sender.id, [Plain('Hello World!')])
```

这里，我们使用了 `send_friend_message` 方法来发送消息。这个方法有两个参数，即好友的 QQ 号和欲发送的消息链。

:::note NOTE: 调用 API
在上面的代码中，我们调用了 `send_friend_message` 方法，这个方法会调用 mirai-api-http 的 API `sendFriendMessage`。

如果你查看 `Mirai` 类的源代码，你会发现你找不到这个方法。这是因为 `Mirai` 使用了 `__getattr__` 来实现动态调用 API。你只需要知道 mirai-api-http 中 API 的名称和参数，就可以像这样直接通过 `bot.API名称` 调用。

为什么是 `bot.send_friend_message` 而不是 `bot.sendFriendMessage`？这是为了符合 PEP 8 规范，因为 `send_friend_message` 是一个合理的函数命名。事实上，`bot.sendFriendMessage` 也是可用的。**我们对所有的 API 都进行了名称转写，全部使用小写字母和下划线**。你可以仿照这个例子，得出其他 API 的命名。

API 的参数和 mirai-api-http 中的定义一致，可以使用位置参数或具名参数的方式调用。
:::

:::note NOTE: 异步
在上面的代码中，我们使用了 `async` 关键字定义异步的事件处理器。这是因为 `send_friend_message` 是一个异步方法，所以我们需要使用 `await` 来调用它。

事实上，你也可以不使用 `async` 关键字，定义同步的事件处理器。但是因为所有的 API 都是异步的，这会导致你无法在事件处理器内调用 API。
:::

最后，我们调用了 `run` 方法，来启动机器人。这一方法会进入事件循环，一直运行。

```python
bot.run()
```

## 总结

到这里，你已经大体知道了如何使用 YiriMirai 开发 QQ 机器人的基本方式。

接下来，你可以查看我们的教程。