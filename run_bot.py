import sys
from pathlib import Path

# 将当前目录加入 Python 路径，确保能找到插件
sys.path.insert(0, str(Path(__file__).parent))

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

# 初始化 NoneBot
nonebot.init(
    driver="~fastapi+~httpx",
    host="127.0.0.1",
    port=8080,
    log_level="INFO",
    command_start=["/"],  # 配置命令前缀
)

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(OneBotV11Adapter)

# 加载插件
# 注意：这里直接加载本地的插件包
nonebot.load_plugin("nonebot_plugin_hltv")

# 启动 NoneBot
if __name__ == "__main__":
    nonebot.run()
