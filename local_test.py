#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


class LocalTestBot:
    """本地测试机器人"""

    def __init__(self):
        print("\n" + "=" * 70)
        print("🤖 Nonebot2 CS2 HLTV 插件 - 本地测试工具")
        print("=" * 70)

        try:
            from nonebot_plugin_hltv.real_client import HLTVClient
            from nonebot_plugin_hltv.config import ConfigModel

            self.client = HLTVClient()
            self.config = ConfigModel()
            print("✓ 插件加载成功\n")
        except ImportError as e:
            print(f"✗ 插件加载失败: {e}")
            sys.exit(1)

        # 命令映射
        self.commands = {
            "cs2比赛": self.handle_matches,
            "cs2战队": self.handle_team,
            "cs2排名": self.handle_ranking,
            "cs2结果": self.handle_results,
            "cs2选手": self.handle_player,
            "帮助": self.show_help,
            "help": self.show_help,
            "exit": self.exit_app,
            "quit": self.exit_app,
        }

    def show_help(self, args: str = ""):
        help_text = """
📚 可用命令:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/cs2比赛              查看当前CS2实时比赛
/cs2战队 <战队名>      查询战队信息
/cs2排名              查看战队Top10排名
/cs2结果              查看最近比赛结果
/cs2选手 <选手名>      查询选手信息
帮助 / help           显示此帮助信息
exit / quit           退出程序
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        print(help_text)

    def show_welcome(self):
        welcome = """
🎮 欢迎使用本地测试工具！

输入 '/帮助' 或 'help' 查看所有可用命令
输入 'exit' 或 'quit' 退出程序

开始测试吧！👇
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        print(welcome)

    async def handle_matches(self, args: str = ""):
        """处理比赛查询"""
        print("\n⏳ 正在查询CS2比赛...")
        result = await self.client.get_cs2_matches()

        if result.get("success"):
            matches = result.get("data", [])
            if matches:
                msg = "【CS2实时比赛】\n"
                for i, match in enumerate(matches[:8], 1):
                    team1 = match.get("team1", "TBD")
                    team2 = match.get("team2", "TBD")
                    event = match.get("event", "Unknown")
                    time_text = match.get("time", "TBD")
                    bo_type = match.get("bo_type", "bo3")

                    msg += f"{i}. ⏰ {team1} vs {team2}\n"
                    msg += f"   时间: {time_text} | {bo_type.upper()}\n"
                    msg += f"   赛事: {event}\n"
            else:
                msg = "当前没有找到比赛信息。"
        else:
            msg = result.get("message", "获取比赛信息失败")

        print(f"\n📤 机器人回复:\n{msg}")

    async def handle_team(self, args: str = ""):
        """处理战队查询"""
        team_name = args.strip()
        if not team_name:
            print("\n⚠️  请提供战队名称")
            print("📝 格式: /cs2战队 <战队名>")
            print("💡 例如: /cs2战队 Vitality")
            return

        print(f"\n⏳ 正在查询 '{team_name}' 的战队信息...")
        result = await self.client.get_team_info(team_name)

        if result.get("success"):
            team_data = result.get("data", {})
            msg = f"【{team_data.get('name', team_name)} 战队信息】\n"
            msg += f"排名: {team_data.get('rank', 'N/A')}\n"
            members = team_data.get('members', [])
            if members:
                msg += f"阵容: {', '.join(members)}\n"
            coach = team_data.get('coach')
            if coach and coach != 'Unknown':
                msg += f"教练: {coach}\n"
            msg += f"详情: {team_data.get('url', 'N/A')}\n"
        else:
            msg = result.get("message", f"无法获取 {team_name} 的战队信息")

        print(f"\n📤 机器人回复:\n{msg}")

    async def handle_ranking(self, args: str = ""):
        """处理排名查询"""
        print("\n⏳ 正在查询战队排名...")
        result = await self.client.get_team_rankings(limit=10)

        if result.get("success"):
            teams = result.get("data", [])
            if teams:
                msg = "【CS2战队排名 Top 10】\n"
                for team in teams[:10]:
                    rank = team.get("rank", "N/A")
                    name = team.get("title", "Unknown")
                    points = team.get("points", "N/A")
                    msg += f"{rank}. {name} ({points}分)\n"
            else:
                msg = "当前没有战队排名数据。"
        else:
            msg = result.get("message", "获取战队排名失败")

        print(f"\n📤 机器人回复:\n{msg}")

    async def handle_results(self, args: str = ""):
        """处理结果查询"""
        print("\n⏳ 正在查询比赛结果...")
        result = await self.client.get_match_results(days=7)

        if result.get("success"):
            matches = result.get("data", [])
            if matches:
                msg = "【最近比赛结果】\n"
                for i, match in enumerate(matches[:5], 1):
                    team1 = match.get("team1", "TBD")
                    team2 = match.get("team2", "TBD")
                    score1 = match.get("score1", 0)
                    score2 = match.get("score2", 0)
                    event = match.get("event", "Unknown")

                    winner = team1 if int(score1) > int(score2) else team2
                    msg += f"{i}. {team1} {score1}-{score2} {team2}\n"
                    msg += f"   胜者: {winner} | 赛事: {event}\n"
            else:
                msg = "当前没有找到比赛结果。"
        else:
            msg = result.get("message", "获取比赛结果失败")

        print(f"\n📤 机器人回复:\n{msg}")

    async def handle_player(self, args: str = ""):
        """处理选手查询"""
        player_name = args.strip()
        if not player_name:
            print("\n⚠️  请提供选手名称")
            print("📝 格式: /cs2选手 <选手名>")
            print("💡 例如: /cs2选手 ZywOo")
            return

        print(f"\n⏳ 正在查询 '{player_name}' 的选手信息...")
        result = await self.client.get_player_info(player_name)

        if result.get("success"):
            player_data = result.get("data", {})
            msg = f"【{player_data.get('full_name', player_name)} 选手信息】\n"
            msg += f"ID: {player_data.get('name', player_name)}\n"
            msg += f"战队: {player_data.get('team', 'N/A')}\n"
            msg += f"国籍: {player_data.get('country', 'N/A')}\n"
            if player_data.get('rating') and player_data['rating'] != 'N/A':
                msg += f"Rating 2.0: {player_data.get('rating', 'N/A')}\n"
            if player_data.get('kpr') and player_data['kpr'] != 'N/A':
                msg += f"KPR: {player_data.get('kpr', 'N/A')}\n"
            if player_data.get('adr') and player_data['adr'] != 'N/A':
                msg += f"ADR: {player_data.get('adr', 'N/A')}\n"
            msg += f"详情: {player_data.get('url', 'N/A')}\n"
        else:
            msg = result.get("message", f"无法获取 {player_name} 的选手信息")

        print(f"\n📤 机器人回复:\n{msg}")

    def exit_app(self, args: str = ""):
        """退出应用"""
        print("\n👋 感谢使用！再见！\n")
        sys.exit(0)

    async def process_command(self, user_input: str):
        """处理用户命令"""
        user_input = user_input.strip()

        if not user_input:
            return

        # 移除前导斜杠
        if user_input.startswith("/"):
            user_input = user_input[1:]

        # 分割命令和参数
        parts = user_input.split(" ", 1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        # 查找处理器
        handler = None
        for cmd_key, cmd_handler in self.commands.items():
            if cmd_key.startswith(command):
                handler = cmd_handler
                break

        if handler:
            # 检查处理器是否需要异步
            if command in ["帮助", "help", "exit", "quit"]:
                handler(args)
            else:
                await handler(args)
        else:
            print(f"\n❌ 未知命令: /{command}")
            print("💡 输入 'help' 查看所有可用命令")

    async def run_interactive(self):
        """运行交互式界面"""
        self.show_welcome()

        while True:
            try:
                # 获取用户输入
                user_input = input("\n👤 你: ").strip()

                if not user_input:
                    continue

                # 处理命令
                await self.process_command(user_input)

            except KeyboardInterrupt:
                self.exit_app()
            except EOFError:
                self.exit_app()
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")


def main():
    """主函数"""
    try:
        bot = LocalTestBot()
        asyncio.run(bot.run_interactive())
    except KeyboardInterrupt:
        print("\n\n👋 程序已中断\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
