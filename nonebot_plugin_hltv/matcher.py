#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
from typing import Optional

from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.rule import to_me

from .real_client import HLTVClient
from .config import ConfigModel

logger = logging.getLogger(__name__)

hltv_client = HLTVClient()
config = ConfigModel()

# 命令定义 - 使用 to_me() 规则，支持 @机器人 触发
matcher_cs2_matches = on_command("cs2比赛", aliases={"cs2匹配", "查看cs2比赛"}, rule=to_me(), priority=1, block=True)
matcher_cs2_team = on_command("cs2战队", aliases={"查询战队", "cs2队伍"}, rule=to_me(), priority=1, block=True)
matcher_cs2_results = on_command("cs2结果", aliases={"查看结果", "cs2结果查询"}, rule=to_me(), priority=1, block=True)
matcher_cs2_ranking = on_command("cs2排名", aliases={"战队排名", "csgo排名"}, rule=to_me(), priority=1, block=True)
matcher_cs2_player = on_command("cs2选手", aliases={"查询选手", "cs2选手查询"}, rule=to_me(), priority=1, block=True)

# 同时也支持不@直接使用命令
matcher_cs2_matches_no_at = on_command("cs2比赛", aliases={"cs2匹配", "查看cs2比赛"}, priority=2, block=True)
matcher_cs2_team_no_at = on_command("cs2战队", aliases={"查询战队", "cs2队伍"}, priority=2, block=True)
matcher_cs2_results_no_at = on_command("cs2结果", aliases={"查看结果", "cs2结果查询"}, priority=2, block=True)
matcher_cs2_ranking_no_at = on_command("cs2排名", aliases={"战队排名", "csgo排名"}, priority=2, block=True)
matcher_cs2_player_no_at = on_command("cs2选手", aliases={"查询选手", "cs2选手查询"}, priority=2, block=True)

# 话题检测（无需@，被动检测）
matcher_topic_detection = on_message(priority=50, block=False)


@matcher_cs2_matches.handle()
@matcher_cs2_matches_no_at.handle()
async def handle_cs2_matches(bot: Bot, event: MessageEvent, matcher: Matcher):
    """处理CS2比赛查询"""
    result = await hltv_client.get_cs2_matches()

    if result.get("success"):
        matches = result.get("data", [])
        if matches:
            msg = "【CS2实时比赛】\n"
            for i, match in enumerate(matches[:8], 1):
                team1 = match.get("team1", "TBD")
                team2 = match.get("team2", "TBD")
                match_event = match.get("event", "Unknown")
                time_text = match.get("time", "TBD")
                bo_type = match.get("bo_type", "bo3")

                msg += f"{i}. ⏰ {team1} vs {team2}\n"
                msg += f"   时间: {time_text} | {bo_type.upper()}\n"
                msg += f"   赛事: {match_event}\n"
        else:
            msg = "当前没有找到比赛信息。\n"
    else:
        msg = result.get("message", "获取比赛信息失败")

    await matcher.finish(msg)


@matcher_cs2_team.handle()
@matcher_cs2_team_no_at.handle()
async def handle_cs2_team(
    bot: Bot, event: MessageEvent, matcher: Matcher, args: str = CommandArg()
):
    team_name = args.extract_plain_text().strip()

    if not team_name:
        await matcher.finish("请提供战队名称。\n示例: /cs2战队 Vitality")
        return

    result = await hltv_client.get_team_info(team_name)

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

    await matcher.finish(msg)


@matcher_cs2_results.handle()
@matcher_cs2_results_no_at.handle()
async def handle_cs2_results(bot: Bot, event: MessageEvent, matcher: Matcher):
    result = await hltv_client.get_match_results(days=7)

    if result.get("success"):
        matches = result.get("data", [])
        if matches:
            msg = f"【最近比赛结果】\n"
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
            msg = "当前没有找到比赛结果。\n"
    else:
        msg = result.get("message", "获取比赛结果失败")

    await matcher.finish(msg)


@matcher_cs2_ranking.handle()
@matcher_cs2_ranking_no_at.handle()
async def handle_cs2_ranking(bot: Bot, event: MessageEvent, matcher: Matcher):
    result = await hltv_client.get_team_rankings(limit=10)

    if result.get("success"):
        teams = result.get("data", [])
        if teams:
            msg = f"【CS2战队排名 Top 10】\n"
            for team in teams[:10]:
                rank = team.get("rank", "N/A")
                name = team.get("title", "Unknown")
                points = team.get("points", "N/A")
                msg += f"{rank}. {name} ({points}分)\n"
        else:
            msg = "当前没有战队排名数据。\n"
    else:
        msg = result.get("message", "获取战队排名失败")

    await matcher.finish(msg)


@matcher_cs2_player.handle()
@matcher_cs2_player_no_at.handle()
async def handle_cs2_player(
    bot: Bot, event: MessageEvent, matcher: Matcher, args: str = CommandArg()
):
    player_name = args.extract_plain_text().strip()

    if not player_name:
        await matcher.finish("请提供选手名称。\n示例: /cs2选手 ZywOo")
        return

    result = await hltv_client.get_player_info(player_name)

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

    await matcher.finish(msg)


@matcher_topic_detection.handle()
async def handle_topic_detection(bot: Bot, event: MessageEvent):
    """被动检测CS2相关话题"""
    if not config.enable_topic_detection:
        return

    if not isinstance(event, MessageEvent):
        return

    message_text = event.get_plaintext().lower()

    # CS2相关关键词
    cs2_keywords = [
        "cs2",
        "csgo",
        "反恐精英",
        "hltv",
        "major",
        "比赛",
        "战队",
        "navi",
        "faze",
        "vitality",
        "astralis",
        "g2",
        "spirit",
    ]

    # 检测关键词
    detected_keywords = [kw for kw in cs2_keywords if kw in message_text]

    if detected_keywords:
        logger.info(f"检测到CS2话题: {detected_keywords}")

