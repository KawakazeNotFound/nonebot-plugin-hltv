#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


async def main():
    print("\n" + "=" * 70)
    print("🌐 HLTV数据测试")
    print("=" * 70)
    
    try:
        from nonebot_plugin_hltv.real_client import HLTVClient
        
        client = HLTVClient()
        print("✓ 客户端初始化成功\n")
        
        # 测试1: 获取比赛
        print("📋 [1] 获取CS2比赛...")
        result = await client.get_cs2_matches()
        print(f"    成功: {result['success']}")
        print(f"    消息: {result['message']}")
        if result['data']:
            print(f"    返回 {len(result['data'])} 场比赛:")
            for i, match in enumerate(result['data'][:5], 1):
                print(f"      {i}. {match['team1']} vs {match['team2']} @ {match['time']} ({match['event']})")
        print()
        
        # 测试2: 获取排名
        print("🏆 [2] 获取战队排名...")
        result = await client.get_team_rankings(limit=5)
        print(f"    成功: {result['success']}")
        print(f"    消息: {result['message']}")
        if result['data']:
            print(f"    返回 {len(result['data'])} 支战队:")
            for team in result['data'][:5]:
                members = ", ".join(team.get('members', [])[:3])
                print(f"      #{team['rank']} {team['title']} ({team.get('points', 0)}分) - {members}...")
        print()
        
        # 测试3: 获取结果
        print("📊 [3] 获取比赛结果...")
        result = await client.get_match_results(days=7)
        print(f"    成功: {result['success']}")
        print(f"    消息: {result['message']}")
        if result['data']:
            print(f"    返回 {len(result['data'])} 场结果:")
            for i, match in enumerate(result['data'][:3], 1):
                print(f"      {i}. {match['team1']} {match['score1']}-{match['score2']} {match['team2']}")
        print()
        
        # 测试4: 获取选手信息
        print("👤 [4] 获取选手信息 (ZywOo)...")
        result = await client.get_player_info("ZywOo")
        print(f"    成功: {result['success']}")
        print(f"    消息: {result['message']}")
        if result['data']:
            print(f"    数据: {result['data']}")
        print()
        
        # 测试5: 获取战队信息
        print("⚽ [5] 获取战队信息 (Vitality)...")
        result = await client.get_team_info("Vitality")
        print(f"    成功: {result['success']}")
        print(f"    消息: {result['message']}")
        if result['data']:
            print(f"    数据: {result['data']}")
        print()
        
        print("=" * 70)
        print("✓ 所有测试完成！")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"❌ 错误: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
