# YiriMirai

一个轻量级、低耦合度的基于 mirai-api-http 的 Python SDK。

目前仍处于开发阶段，各种内容可能会有较大的变化。

## 安装

克隆这个仓库到本地，然后使用`poetry`安装：
```shell
git clone git@github.com:Wybxc/YiriMirai.git
cd YiriMirai
poetry install
```

## 使用

```python
from YiriMirai import Mirai, HTTPAdapter, FriendMessage, Plain

if __name__ == '__main__':
    bot = Mirai(qq=12345678, adapter=HTTPAdapter(verify_key='your_verify_key', host='localhost', port=8080))

    @bot.on(FriendMessage)
    async def on_friend_message(event: FriendMessage):
        if str(event.message_chain) == '你好':
            await bot.send_friend_message(event.sender.id, [Plain('Hello World!')]
```

更多信息参看[文档](https://yiri-mirai.vercel.app/)。

## 开源协议

本项目使用 AGPLv3 开源协议。