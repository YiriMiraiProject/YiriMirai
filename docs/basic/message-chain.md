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

## 图片与语音

### 接收图片

获取消息链的 `Image` 元素后，可以通过其 `download` 方法下载图片。

```python
images = message_chain[Image]
for image in images:
    await image.download(directory='./images')
```

下载时，可以指定文件名或目录名。

```python
await image.download(directory='./images')
await image.download(filename='./images/1.png')
```

默认情况下，文件名的拓展名会被忽略，由接收到的图片的类型决定拓展名。可以通过 `determine_type=False` 禁用这一行为。

```python
await image.download(filename='./images/1.png', determine_type=False)
```

### 接收语音

语音的下载与图片基本相同，都是通过 `download` 方法实现。

```python
voice = message_chain[Voice][0] # 一条消息只会包含一个语音
await voice.download(directory='./voices')
# 或者指定文件名
await image.download(filename='./voices/1.silk')
```

语音采用 silk v3 格式编码，silk 格式的编解码请使用 [graiax-silkcoder](https://pypi.org/project/graiax-silkcoder/)。

### 发送图片

发送图片的最简单的方式是直接实例化 `Image` 类型的消息组件。此方式支持本地图片、网络图片和 base64 编码的图片。

```python
from pathlib import Path
message_chain = MessageChain([
    # 传入 path 时，应使用绝对路径
    Image(path=str(Path.cwd() / 'images/1.png')),
    Image(url='https://raw.githubusercontent.com/mamoe/mirai/dev/docs/mirai.png'),
    Image(base64='/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkS' \
        + 'Ew8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJ' \
        + 'CQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy' \
        + 'MjIyMjIyMjIyMjIyMjL/wgARCAAbABsDASIAAhEBAxEB/8QAGQAAAgMBAAAAAAAA' \
        + 'AAAAAAAAAAQBBQYD/8QAGAEAAgMAAAAAAAAAAAAAAAAAAAECAwT/2gAMAwEAAhAD' \
        + 'EAAAAd+l2zry6kQfV8VloCTcAl//xAAdEAACAgEFAAAAAAAAAAAAAAABAwACBBAR' \
        + 'EiAj/9oACAEBAAEFApbKXW+jiapxVBrVu9oRuDi8YlIV2//EABkRAQADAQEAAAAA' \
        + 'AAAAAAAAAAIAAQMxEf/aAAgBAwEBPwHfVFUB24XS5FmV2E0a8qf/xAAVEQEBAAAA' \
        + 'AAAAAAAAAAAAAAABIP/aAAgBAgEBPwEj/8QAIRAAAQIEBwAAAAAAAAAAAAAAAQAR' \
        + 'ECExQQIDEiAjQmH/2gAIAQEABj8CWip8jiIqymWaaOTVrwIN1xonsd3/xAAcEAAB' \
        + 'BAMBAAAAAAAAAAAAAAABABEhMRBBYSD/2gAIAQEAAT8hQmDnLcZpWQTDOxS1JsUU' \
        + '6AMVto7afEDaR6//2gAMAwEAAgADAAAAEKf3/P/EABkRAAMAAwAAAAAAAAAAAAAA' \
        + 'AAABIRFBgf/aAAgBAwEBPxBNgKW9J0srUY1w/8QAFhEBAQEAAAAAAAAAAAAAAAAA' \
        + 'AQAR/9oACAECAQE/EAJrJkKS7f/EAB4QAQACAgMAAwAAAAAAAAAAAAERIQBREDFB' \
        + 'IGFx/9oACAEBAAE/EMY4i4EJYt5c2Eq07xBRBOyJ1iLC5tzqCn784HiUDY54k9Di' \
        + 'X6ZeQrEwaPl//9k=')
])
```

此外，还有几种发送图片的方法。

使用 `Image.from_local`，将从本地读取图片，并以 base64 编码的形式发送。此方式可能会消耗较多内存。

```python
message_chain = MessageChain([
    # 此处可以使用相对路径或绝对路径
    await Image.from_local('./images/1.png')
])
```

使用 `upload_image` API 将图片提前上传到服务器。

```python
message_chain = MessageChain([
    # 第一个参数为会话类型，可以为 'friend' 'group' 或 'temp'
    await bot.upload_image('friend', './images/1.png')
])
```

:::caution
`upload_image` API **只能在 HTTP 适配器下工作**（包括下文提到的 `upload_voice`）。这是由于 WebSocket 在文件传输时会阻塞管道，造成信号延迟。

如果要在 WebSocket 适配器下上传图片或语音，可以使用 `bot.use_adapter`，临时启用 HTTP 适配器。

```python
async with bot.use_adapter(HTTPAdapter.via(bot)):
    image = await bot.upload_image('friend', './images/1.png')
```
:::

### 发送语音

语音的发送与图片类似。此方式支持本地语音、网络语音文件和 base64 编码的语音。

```python
from pathlib import Path
message_chain1 = MessageChain([
    # 传入 path 时，应使用绝对路径
    Voice(path=str(Path.cwd() / 'voices/1.silk'))
])
message_chain2 = MessageChain([Voice(url='...')])
message_chain3 = MessageChain([Voice(base64='...')])
```

语音消息除包含一个 `Voice` 组件外，不能再包含其他组件。

:::caution 私聊语音
由于目前 mirai-api-http **只支持群聊语音，不支持私聊语音**，在私聊中发送语音会导致未知的错误。
:::

此外，和图片一样，可以通过 `Voice.from_local` 将本地语音以 base64 的形式发送，也可以通过 `upload_voice` API 提前上传语音到服务器（需要 HTTP 适配器）。

```python
message_chain4 = MessageChain([
    # 此处可以使用相对路径或绝对路径
    await Voice.from_local('./voices/1.silk')
])
message_chain5 = MessageChain([
    # 第一个参数为会话类型，只能为 'group'
    await bot.upload_voice('group', './voices/1.silk')
])
```
