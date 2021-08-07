---
sidebar_position: 5
---

# 常见问题

## ModuleNotFoundError: No module named 'mirai'

1. 检查你有没有在正确的 python 环境下运行，尤其是在使用 conda 或 venv 这样的 python 环境管理器时。
2. 重新安装 YiriMirai。使用 `pip install yiri-mirai --upgrade`。
3. 试一下 `import YiriMirai`。如果你成功导入了，说明你安装了错误的版本。**从 0.1.1 开始，YiriMirai 的 PyPI 仓库名称变成了 `yiri-mirai`，而不是 `yirimirai`（注意短杠）**。使用 `pip install yiri-mirai` 安装正确的版本。

## 端口冲突

可能的报错：
```
[Errno 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
[Errno 10048] 通常每个套接字地址(协议/网络地址/端口)只允许使用一次
[WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
[WinError 10048] 通常每个套接字地址(协议/网络地址/端口)只允许使用一次
[Errno 10013] An attempt was made to access a socket in a way forbidden by its access permissions
[Errno 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。
[WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions
[WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。
```

这种情况往往是由于端口冲突引起的。

`bot.run` 在不传入参数时，会占用 8080 端口，可以通过传入 `port` 参数指定其他端口。

```python
bot.run(port=8099)
```

## 启动后立即退出

如果你看到了这样的输出：

```
2021-08-07 09:06:46 - WARNING  未找到可用的 ASGI 服务，反向 WebSocket 和 WebHook 上报将不可用。
仅 HTTP 轮询与正向 WebSocket 可用。
建议安装 ASGI 服务器，如 `uvicorn` 或 `hypercorn`。
在命令行键入：
    pip install uvicorn
或者
    pip install hypercorn
2021-08-07 09:06:46 - INFO     [HTTP] 成功登录到账号12345678。
2021-08-07 09:06:46 - INFO     [WebHook] 成功登录到账号12345678。
2021-08-07 09:06:47 - INFO     [WebHook] 从账号12345678退出。
2021-08-07 09:06:47 - INFO     [HTTP] 从账号12345678退出。
```

这说明你启用了 WebHook 适配器，但没有安装 uvicorn 或 hypercorn。

在命令行键入：
```
pip install uvicorn
```
或者
```
pip install hypercorn
```

## 提问的艺术

:::warning
在提出问题之前，请先学习提问的艺术。
:::

当提出一个技术问题时，你能得到怎样的回答？这不仅取决于问题的复杂程度，还取决于你提问的方法。

首先你必须明白，我们喜欢能激发思维的好问题。好问题是一份厚礼，可以提高我们的理解力，而且通常会暴露我们以前从没意识到或者思考过的问题。

有时看起来似乎我们对新手，对知识贫乏者怀有敌意，但其实不是那样的。

我们不想掩饰对这样一些人的蔑视——他们不愿思考，或者在发问前不去完成他们应该做的事。这种人只是在浪费别人的精力--他们只愿索取，从不付出，无端消耗我们的时间，而我们本可以把时间用在更有趣的问题或者更值得回答的人身上。

如果你决定向我们求助，当然不希望被视为无价值的人。立刻得到有效答案的最好方法，就是提出一个优秀的问题——聪明、自信、有解决问题的思路，只是偶尔在特定的问题上需要获得一点帮助。

我们在很大程度上属于志愿者，从繁忙的生活中抽出时间来解惑答疑，而且时常被提问淹没。所以我们无情的滤掉一些话题，特别是抛弃那些看起来无用的家伙，以便更高效的利用时间来回答那些聪明的问题。如果你以此无理取闹, 我们有权利停止对本项目的更新.

在提出技术问题前，检查你有没有做到：

- 通读手册，试着自己找答案。
- 在 FAQ （也就是下面的内容）里找答案。
- 在网上搜索。
- 向你身边精于此道的朋友打听。

当你提出问题的时候，首先要说明在此之前你干了些什么；这将有助于树立你的形象：你不是一个妄图不劳而获的乞讨者，不愿浪费别人的时间。如果提问者能从答案中学到东西，我们更乐于回答他的问题。

提问前，做好周全的思考，准备好你的问题。草率的发问只能得到草率的回答，或者根本得不到任何答案。越表现出在寻求帮助前为解决问题付出的努力，你越能得到 实质性的帮助。

绝不要自以为够资格得到答案，你没这种资格。毕竟你没有为这种服务支付任何报酬。你要自己去“挣”回一个答案，靠提出一个有内涵的，有趣的，有思维激励作用的问题--一个对社区的经验有潜在贡献的问题，而不仅仅是被动的从他人处索要知识。

## 其他问题

如果你的问题在此页上没有找到，你可以在我们的社区（见网页页脚）询问。

如果你确信你的问题是由 YiriMirai 导致的，并能明确问题发生的原因，请在 [GitHub Issues](https://github.com/YiriMiraiProject/YiriMirai/issues) 上提出，我们会尽可能地解决这个问题。
