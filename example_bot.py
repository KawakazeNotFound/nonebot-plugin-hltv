#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nonebot2 CS2 HLTV 插件集成示例
展示如何在 Nonebot2 机器人中使用本插件

这是一个最小化的例子，展示如何：
1. 初始化Nonebot2驱动器
2. 注册OneBot适配器（支持QQ、微信等）
3. 加载CS2 HLTV插件
4. 启动机器人

实际部署时建议：
- 配置 .env 文件设置QQ号、令牌等
- 根据需要添加其他插件
- 修改驱动器配置（HTTP/WebSocket等）
"""

import nonebot
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Adapter as OneBot_V11_Adapter

# 初始化Nonebot驱动器
driver = get_driver()

# 注册OneBot v11适配器（支持QQ、微信等）
driver.register_adapter(OneBot_V11_Adapter)

# 加载CS2 HLTV插件
nonebot.load_plugin("nonebot_plugin_hltv")

# 其他插件也可以在这里加载
# nonebot.load_plugin("some_other_plugin")


def main():
    """启动机器人"""
    nonebot.run()


if __name__ == "__main__":
    main()
