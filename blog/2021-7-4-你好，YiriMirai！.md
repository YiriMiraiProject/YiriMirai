---
title: 你好，YiriMirai！
author: 忘忧北萱草
author_url: https://github.com/Wybxc
author_image_url: https://avatars.githubusercontent.com/u/25005856
tags: [开发笔记]
hide_table_of_contents: false
---

2021年6月28日，我启动了 YiriMirai 的开发。7月4日，发布第一个预览版本 v0.1.1。

YiriMirai 是一个 mirai-api-http 的 Python SDK。<!--truncate-->在这个项目之前，基于 mirai-api-http，在 Python 上编写的机器人框架已经有多个，其中不乏优秀的项目，比如 Graia Framework，已经有了相对完备的设计和初步成型的社区。那么，为什么我要重新开发一个新的 SDK？

最主要的原因，是我们缺少一个“纯粹”的 SDK。像 Graia Framework 这样的项目，其实是“框架”而非 SDK。以盖房子为喻，“框架”是为你搭好了骨架，甚至建好了墙壁，你需要的是把你想要的东西“填充”进框架，最终盖好的房子总是符合框架的形状；而 SDK 更像地基，它并不关心你的房子是什么样的，它只关心你能否建造一座漂亮的、牢固地立在地上的房子。

框架式的设计有时候会让开发变得简单，有时候也会带来很多麻烦，尤其是当你需要的东西和框架不完全一致的时候。虽然你可以对你的项目进行一些小小的改造，来适应这个框架，即使不至于方枘圆凿，也会让框架的功能得不到发挥。

一个典型的例子是 Graia Framework 的 Broadcast Contorl。是的，它极其强大，极富表现力，但它并非万能的。当你需要的逻辑超出了它的能力范围，你不得不在它上面重新搭建一层消息分发器。如此一来，Broadcast Contorl 原本的强大性就失效了，这显然不是框架的本意。

我一直相信一个道理：**如果不需要一项功能，你最好没有它**。

再比如，“模块化”这一设计。这很好，适合很多人，但也不是适合所有人。我就遇到了这样的问题。我之前的聊天机器人设计，功能与功能之间存在很强的业务耦合，如果想要放到模块化的框架里，就必须把整个机器人做成一个模块。这就完全没有模块化的必要了。

在这一方面，我认为 Nonebot 做得很好。它包含两个项目：aiocqhttp 是底层 SDK，Nonebot 是在 aiocqhttp 及其他 SDK 基础上的框架。我之前的项目中，就是使用的 aiocqhttp。我基于它搭建了自己的框架，效果很好。

那么，在 mirai-api-http 生态中，**为什么不能有一个像 aiocqhttp 一样的纯粹的 SDK 呢**？

于是我开发了 YiriMirai。YiriMirai 从一开始就是作为 SDK 设计的，它只是在对 mirai-api-http 进行封装，提供 json 数据与 Python 对象的转换，仅此而已。没有模块化或者其他复杂的设计，这不是 YiriMirai 要关心的事情。

总之，YiriMirai 诞生了。它很新，仍在成长中，但我相信它能够成长到独当一面的那一天，也总会有人需要一个 YiriMirai。
