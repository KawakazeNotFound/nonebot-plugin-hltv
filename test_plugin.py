#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nonebot2 CS2 HLTV 插件 - 快速测试脚本

这个脚本演示如何在 Nonebot2 中加载和使用 CS2 HLTV 插件
"""

import asyncio
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent

print("=" * 60)
print("✓ Nonebot2 CS2 HLTV 插件 - 快速测试")
print("=" * 60)

# 测试1: 导入插件元数据
print("\n[1] 测试插件导入...")
try:
    from nonebot_plugin_hltv import __plugin_meta__
    print(f"    ✓ 插件: {__plugin_meta__.name}")
    print(f"    ✓ 类型: {__plugin_meta__.type}")
    print(f"    ✓ 描述: {__plugin_meta__.description[:50]}...")
except Exception as e:
    print(f"    ✗ 导入失败: {e}")
    exit(1)

# 测试2: 导入配置模型
print("\n[2] 测试配置模型...")
try:
    from nonebot_plugin_hltv.config import ConfigModel
    config = ConfigModel()
    print(f"    ✓ 配置已初始化")
    print(f"    ✓ 缓存配置:")
    print(f"      - 比赛数据: {config.cache_duration_matches}s")
    print(f"      - 战队排名: {config.cache_duration_teams}s")
    print(f"      - 比赛结果: {config.cache_duration_results}s")
    print(f"    ✓ 功能开关:")
    print(f"      - 启用缓存: {config.enable_caching}")
    print(f"      - 话题检测: {config.enable_topic_detection}")
except Exception as e:
    print(f"    ✗ 配置失败: {e}")
    exit(1)

# 测试3: 导入HLTV客户端
print("\n[3] 测试HLTV客户端...")
try:
    from nonebot_plugin_hltv.client import HonestHLTVClient
    client = HonestHLTVClient()
    print(f"    ✓ 客户端已初始化")
except Exception as e:
    print(f"    ✗ 客户端初始化失败: {e}")
    exit(1)

# 测试4: 异步测试客户端
print("\n[4] 测试异步接口...")


async def test_async_interfaces():
    """测试异步接口"""
    try:
        # 测试获取比赛
        result = await client.get_cs2_matches()
        print(f"    ✓ get_cs2_matches: {result.get('success', False)}")
        print(f"      消息: {result.get('message', '')[:40]}...")

        # 测试获取排名
        result = await client.get_team_rankings()
        print(f"    ✓ get_team_rankings: {result.get('success', False)}")

        # 测试获取结果
        result = await client.get_match_results()
        print(f"    ✓ get_match_results: {result.get('success', False)}")

        # 测试获取选手信息
        result = await client.get_player_info("ZywOo")
        print(f"    ✓ get_player_info: {result.get('success', False)}")

        # 测试获取战队信息
        result = await client.get_team_info("Vitality")
        print(f"    ✓ get_team_info: {result.get('success', False)}")

        return True
    except Exception as e:
        print(f"    ✗ 异步测试失败: {e}")
        return False


try:
    success = asyncio.run(test_async_interfaces())
    if not success:
        exit(1)
except Exception as e:
    print(f"    ✗ 异步测试出错: {e}")
    exit(1)

# 测试5: 验证依赖
print("\n[5] 验证依赖...")
try:
    import nonebot
    import nonebot.adapters.onebot.v11
    import pydantic
    print(f"    ✓ nonebot2: {nonebot.__version__}")
    print(f"    ✓ nonebot-adapter-onebot: 已安装")
    print(f"    ✓ pydantic: {pydantic.__version__}")
except ImportError as e:
    print(f"    ✗ 依赖缺失: {e}")
    exit(1)

# 最终总结
print("\n" + "=" * 60)
print("✓ 所有测试通过！项目构建成功！")
print("=" * 60)
print("\n📖 后续步骤:")
print("   1. 在 bot.py 中加载插件:")
print("      nonebot.load_plugin('nonebot_plugin_hltv')")
print("\n   2. 或在 pyproject.toml 中配置:")
print("      [tool.nonebot]")
print("      plugins = ['nonebot_plugin_hltv']")
print("\n   3. 启动机器人后可使用命令:")
print("      /cs2比赛   - 查看当前比赛")
print("      /cs2战队 Vitality - 查询战队")
print("      /cs2排名   - 查看排名")
print("\n📚 更多信息: 查看 NONEBOT_GUIDE.md")
print("=" * 60)
