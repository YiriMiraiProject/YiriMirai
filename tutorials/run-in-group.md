---
sidebar_position: 4
---

# 二：在群里运行

上一节，我们完成了一个最简单的机器人。不过，这个机器人只处理了好友消息，并没有处理群消息。一个有趣的机器人，只能自娱自乐当然没有什么意思，肯定要拿出来到群里，才能让大家玩得开心。

现在，让我们来修改一下机器人的代码，让它能够处理群消息。

## 处理群消息

上一节中，我们使用 `bot.on(FriendMessage)` 来处理好友消息。同样地，我们可以用 `bot.on(GroupMessage)` 来处理群消息。

首先我们需要引入 `GroupMessage` 类：

```python
from mirai import GroupMessage
```

然后仿照上一节那样，编写 `GroupMessage` 的事件处理器。

```python
@bot.on(GroupMessage)
def on_group_message(event: GroupMessage):
    if str(event.message_chain) == '你好':
        return bot.send(event, 'Hello, World!')
```

:::note 我应该把事件处理器放在哪里？
答案很简单：创建 Mirai 实例之后，调用 `bot.run` 之前的任何地方。当然，你需要保证你的事件处理器的定义不在无法运行得到的地方。

比如这里的 `on_group_message` 事件处理器，就可以简单地放在 `on_friend_message` 后面。
:::

现在，开始运行……慢着！你想好为机器人设置怎样的逻辑了吗？

:::caution
当群里的人比较多时，没有人会喜欢一个喋喋不休的机器人。所以，为机器人设置合理的触发逻辑是非常必要的。

另外，测试群组相关的功能时，最好单独为机器人创建一个测试用群，避免打扰其他人。
:::

## 触发条件：At 时回复

一个比较有用的逻辑是：只有 At 机器人，机器人才会回复。

下面我们就来实现一下这个逻辑。

```python
from mirai import At

@bot.on(GroupMessage)
def on_group_message(event: GroupMessage):
    if At(bot.qq) in event.message_chain:
        return bot.send(event, [At(event.sender.id), '你在叫我吗？'])
```

稍微有点难以理解了。我们一点点来吧。

## 消息链

可以看到，我们是从 `event.message_chain` 中取得消息内容的。`message_chain` 直译过来就是“消息链”。

### 为什么是消息链？

QQ 消息并不只是纯文本，也不只是单一类型的消息。文本中可以夹杂着图片、At 某人等多种类型的消息。mirai 为了处理富文本消息，采用了消息链（Message Chain）这一方式。

消息链可以看作是一系列消息组件（Message Component）构成的列表。消息组件表示消息中的一部分，比如纯文本 `Plain`，At 某人 `At` 等等。

### 消息组件

常见的消息组件有以下几个：

| 名称  | 含义    | 示例                      |
| ----- | ------- | ------------------------- |
| Plain | 纯文本  | `Plain('Hello!')`         |
| At    | @某人   | `At(123456)`              |
| AtAll | @所有人 | `AtAll()`                 |
| Face  | 表情    | `Face(name='斜眼笑')`     |
| Image | 图片    | `Image(path='image.png')` |

### 使用消息链

用 `in` 运算符可以判断消息链中有没有某个消息组件。比如这里的 `At(bot.qq) in event.message_chain`，就是判断是否有人 At 机器人。

`bot.send` 方法的第二个参数可以是字符串，也可以是消息链。实际上，字符串会被转换成只有一个 Plain 元素的消息链。

传入消息链时，我们可以显式地使用 `MessageChain` 类的构造函数，也可以简单地使用消息组件构成的列表。构造消息链时，`Plain` 可以省略。

比如上面的代码，也可以写成：

```python
if At(bot.qq) in event.message_chain:
    return bot.send(event, MessageChain([At(event.sender.id), Plain('你在叫我吗？')]))
```

## 事件类型

在上一节，我们用到了 `FriendMessage`，这里我们用到了 `GroupMessage`，这两个都是类。

如果你使用 VSCode 或者 PyCharm 这样的编辑器，可以按住 Ctrl 点击这两个名字，查看它们的定义。比如下面就是 `GroupMessage` 的定义：

```python
class GroupMessage(MessageEvent):
    """群消息。

    `type: str` 事件名。

    `sender: GroupMember` 发送消息的群成员。

    `message_chain: MessageChain` 消息内容。
    """
    type: str = 'GroupMessage'
    """事件名。"""
    sender: GroupMember
    """发送消息的群成员。"""
    message_chain: MessageChain
    """消息内容。"""
    @property
    def group(self) -> Group:
        return self.sender.group
```

从这里我们可以知道，`GroupMessage` 类型有三个字段：`type` `sender` 和 `message_chain`。从 `sender` 字段中，我们可以知道发送消息的群成员是哪个。

:::note
这样的定义方式看起来和 pydantic 有点像。

……实际上，这就是 pydantic。YiriMirai 通过 pydantic 解析 mirai-api-http 发来的数据，从而转换成更加便于 Python 操作的类型。
:::

现在再来看一看我们处理群消息的这段代码。

```python {2,4}
@bot.on(GroupMessage)
def on_group_message(event: GroupMessage):
    if At(bot.qq) in event.message_chain:
        return bot.send(event, [At(event.sender.id), '你在叫我吗？'])
```

注意标出的这两行。还记得事件处理器的参数 `event` 吗？这个参数就是对应事件类型的一个实例。从相应的定义可以知道，`event.sender` 是发送消息的群成员，`event.sender.id` 是这个群成员的 QQ 号。所以，`At(event.sender.id)` 就是 At 一下对应的群成员。

:::tip 善用代码提示和查看定义
由于精力有限，我们不可能把所有事件类型的使用方法事无巨细地在这里列出来，这也会加大你学习的难度。所以，我们选择把细节内容放在 docstring 中，如果你想了解更多关于事件类型的信息，可以查看它们的定义。

一个优秀的代码编辑器会显示充分的代码提示，比如 docstring，从中你能获知很多信息。所以，善用这个功能，能让你更加高效地完成你的代码。

当然，如果你的代码编辑器没有这样的功能，也不要着急，不妨来看看我们的 [API 文档](https://yiri-mirai-api.vercel.app/)，你会找到你需要的东西的。
:::

## 自由发挥时间

回过头来，重新看一看这一节的代码：

```python
from mirai import At

@bot.on(GroupMessage)
def on_group_message(event: GroupMessage):
    if At(bot.qq) in event.message_chain:
        return bot.send(event, [At(event.sender.id), '你在叫我吗？'])
```

你可以试着仿照这段代码，自己编写一个处理群消息的事件处理器。

```python
from mirai import At

@bot.on(GroupMessage)
def on_group_message(event: GroupMessage):
    if At(bot.qq) in event.message_chain:
        return bot.send(event, [At(event.sender.id), '你在叫我吗？'])

@bot.on(GroupMessage)
def on_group_message_new(event: GroupMessage):
    """发挥你的创意……"""
```

:::note 多个事件处理器
是的，同一个事件可以有多个事件处理器。

需要注意的一点是，**由于异步的特性，事件处理器的执行顺序并不是固定的，后定义的事件处理器可能在先定义的事件处理器之前运行**。
:::

:::note 注意命名冲突
因为事件处理器的名字并不重要，你应该为不同的事件处理器命名不同的名字，以避免命名冲突。
:::

## 总结

这一节我们成功地把机器人设置到了群里，处理和发送群消息。

本节的示例代码在[这里](/examples/02.md)。

准备好了的话，就前往下一节吧。