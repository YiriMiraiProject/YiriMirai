---
sidebar_position: 3.4
---

# 消息链

## 为什么是消息链？

QQ 消息并不只是纯文本，也不只是单一类型的消息。文本中可以夹杂着图片、At 某人等多种类型的消息。

mirai 为了处理富文本消息，采用了消息链（Message Chain）这一方式。

消息链可以看作是一系列消息组件（Message Component）构成的列表。消息组件表示消息中的一部分，比如纯文本 `Plain`，At 某人 `At` 等等。

关于可用的消息组件，参看 [API 文档](https://yiri-mirai-api.vercel.app/models/message.html)。

## 构造消息链

一个构造消息链的例子：

```py
message_chain = MessageChain([
    AtAll(),
    Plain("Hello World!"),
])
```

`Plain` 可以省略。

```py
message_chain = MessageChain([
    AtAll(),
    "Hello World!",
])
```

## 使用消息链

在调用 API 时，参数中需要 MessageChain 的，也可以使用 `List[MessageComponent]` 代替。
例如，以下两种写法是等价的：

```py
await bot.send_friend_message(12345678, [
    Plain("Hello World!")
])
```

```py
await bot.send_friend_message(12345678, MessageChain([
    Plain("Hello World!")
]))
```

## 消息链的字符串表示

使用`str(message_chain)`获取消息链的字符串表示，字符串采用 mirai 码格式，并自动按照 mirai 码的规定转义。参看 mirai 的[文档](https://github.com/mamoe/mirai/blob/dev/docs/Messages.md#mirai-%E7%A0%81)。

获取未转义的消息链字符串，可以使用`deserialize(str(message_chain))`。

## 在消息链上的操作

可以使用 for 循环遍历消息链中的消息组件。

```py
for component in message_chain:
    print(repr(component))
```

可以使用 `==` 运算符比较两个消息链是否相同。

```py
another_msg_chain = MessageChain([
    {
        "type": "AtAll"
    }, {
        "type": "Plain",
        "text": "Hello World!"
    },
])
print(message_chain == another_msg_chain)
'True'
```

可以使用 `in` 运算检查消息链中：

1. 是否有某个消息组件。
2. 是否有某个类型的消息组件。
3. 是否有某个子消息链。
4. 对应的 mirai 码中是否有某子字符串。

```py
if AtAll in message_chain:
    print('AtAll')

if At(bot.qq) in message_chain:
    print('At Me')

if MessageChain([At(bot.qq), Plain('Hello!')]) in message_chain:
    print('Hello!')

if 'Hello' in message_chain:
    print('Hi!')
```

也可以使用 `>=` 和 `<=` 运算符：

```py
if MessageChain([At(bot.qq), Plain('Hello!')]) <= message_chain:
    print('Hello!')
```

:::tip
此处的子消息链匹配会把 Plain 看成一个整体，而不是匹配其文本的一部分。

如需对文本进行部分匹配，请采用 mirai 码字符串匹配的方式。
:::

消息链对索引操作进行了增强。以消息组件类型为索引，获取消息链中的全部该类型的消息组件。

```py
plain_list = message_chain[Plain]
'[Plain("Hello World!")]'
```

以 `类型: 数量` 为索引，获取前至多多少个该类型的消息组件。

```py
plain_list_first = message_chain[Plain: 1]
'[Plain("Hello World!")]'
```
