#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
import asyncio
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import cloudscraper

logger = logging.getLogger(__name__)


class HLTVClient:
    """HLTV数据客户端"""

    BASE_URL = "https://www.hltv.org"
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.scraper = cloudscraper.create_scraper()
        self.logger.info("HLTV客户端初始化完成")

    async def _fetch(self, url: str) -> str:
        """异步获取URL内容（通过cloudscraper）"""
        try:
            response = await asyncio.to_thread(self.scraper.get, url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"获取URL失败 {url}: {e}")
            raise

    async def get_cs2_matches(self) -> Dict[str, Any]:
        """获取CS2比赛数据"""
        try:
            url = f"{self.BASE_URL}/matches"
            self.logger.info(f"正在获取比赛数据: {url}")
            
            html = await self._fetch(url)
            soup = BeautifulSoup(html, "html.parser")
            
            matches = []
            # 使用正确的选择器 - div.match 包含整个比赛元素
            match_elements = soup.select("div.match")
            
            for match_elem in match_elements[:15]:
                try:
                    # 获取比赛链接和信息
                    match_link = match_elem.select_one("a[href*='/matches/']")
                    if not match_link:
                        continue
                    
                    href = match_link.get("href", "")
                    
                    # 获取时间 - .match-time 包含时间文本
                    time_elem = match_elem.select_one(".match-time")
                    time_text = time_elem.get_text(strip=True) if time_elem else "TBD"
                    
                    # 获取BO类型 - .match-meta 包含 bo1/bo3/bo5
                    meta_elem = match_elem.select_one(".match-meta")
                    bo_type = meta_elem.get_text(strip=True) if meta_elem else "bo3"
                    
                    # 获取两支队伍名称 - 在 div.match-teamname 中
                    team_names = match_elem.select("div.match-teamname")
                    
                    if len(team_names) >= 2:
                        team1 = team_names[0].get_text(strip=True)
                        team2 = team_names[1].get_text(strip=True)
                    else:
                        continue
                    
                    # 从链接中提取赛事名（链接格式：/matches/id/team1-vs-team2-event-name）
                    event_name = "Unknown"
                    if href:
                        parts = href.split("/")[-1].split("-vs-")
                        if len(parts) > 1:
                            event_parts = parts[1].split("-", 1)
                            if len(event_parts) > 1:
                                event_name = event_parts[1].replace("-", " ").title()
                    
                    match_data = {
                        "team1": team1,
                        "team2": team2,
                        "score1": 0,
                        "score2": 0,
                        "event": event_name,
                        "time": time_text,
                        "status": "scheduled",
                        "bo_type": bo_type,
                        "url": f"{self.BASE_URL}{href}" if href else ""
                    }
                    
                    matches.append(match_data)
                except Exception as e:
                    self.logger.debug(f"解析比赛元素失败: {e}")
                    continue
            
            return {
                "message": f"成功获取 {len(matches)} 场比赛数据",
                "data": matches,
                "source": "hltv",
                "success": len(matches) > 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取比赛数据失败: {e}")
            return {
                "message": f"获取比赛数据失败: {str(e)}",
                "data": [],
                "source": "hltv",
                "success": False,
                "error": str(e)
            }

    async def get_team_rankings(self, limit: int = 30) -> Dict[str, Any]:
        """获取战队排名数据 - 使用正确的选择器从 .ranked-team 提取"""
        try:
            url = f"{self.BASE_URL}/ranking/teams"
            self.logger.info(f"正在获取战队排名: {url}")
            
            html = await self._fetch(url)
            soup = BeautifulSoup(html, "html.parser")
            
            teams = []
            # 使用正确的选择器 - .ranked-team 包含每个战队的排名信息
            ranked_teams = soup.select(".ranked-team")
            
            for team_elem in ranked_teams[:limit]:
                try:
                    # 排名 - span.position 包含 #1, #2 等
                    rank_elem = team_elem.select_one("span.position")
                    rank_text = rank_elem.get_text(strip=True) if rank_elem else ""
                    rank = rank_text.replace("#", "") if rank_text else str(len(teams) + 1)
                    
                    # 战队名 - span.name
                    name_elem = team_elem.select_one("span.name")
                    team_name = name_elem.get_text(strip=True) if name_elem else "Unknown"
                    
                    # 积分 - span.points 包含 (930HLTVpoints)
                    points_elem = team_elem.select_one("span.points")
                    points_text = points_elem.get_text(strip=True) if points_elem else "(0)"
                    # 提取数字
                    points = "".join(c for c in points_text if c.isdigit())
                    
                    # 战队链接
                    team_link = team_elem.select_one("a[href*='/team/']")
                    href = team_link.get("href", "") if team_link else ""
                    
                    # 成员 - .rankingNicknames
                    members_elems = team_elem.select(".rankingNicknames")
                    members = [m.get_text(strip=True) for m in members_elems[:5]]
                    
                    team_data = {
                        "rank": int(rank) if rank.isdigit() else len(teams) + 1,
                        "title": team_name,
                        "points": int(points) if points else 0,
                        "members": members,
                        "url": f"{self.BASE_URL}{href}" if href else ""
                    }
                    
                    teams.append(team_data)
                except Exception as e:
                    self.logger.debug(f"解析排名行失败: {e}")
                    continue
            
            return {
                "message": f"成功获取 {len(teams)} 支战队排名",
                "data": teams,
                "source": "hltv",
                "success": len(teams) > 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取战队排名失败: {e}")
            return {
                "message": f"获取战队排名失败: {str(e)}",
                "data": [],
                "source": "hltv",
                "success": False,
                "error": str(e)
            }

    async def get_match_results(self, days: int = 7) -> Dict[str, Any]:
        """获取比赛结果数据"""
        try:
            url = f"{self.BASE_URL}/results"
            self.logger.info(f"正在获取比赛结果: {url}")
            
            html = await self._fetch(url)
            soup = BeautifulSoup(html, "html.parser")
            
            results = []
            # 使用正确的选择器 - .result-con 包含每个结果
            result_cons = soup.select(".result-con")
            
            for result_con in result_cons[:20]:
                try:
                    # 获取 div.result 内的数据
                    result_div = result_con.select_one("div.result")
                    if not result_div:
                        continue
                    
                    # 战队1 - td.team-cell 内的 div.team
                    team1_elem = result_div.select_one("div.team1 .team") or result_div.select_one(".line-align.team1 .team")
                    team1 = team1_elem.get_text(strip=True) if team1_elem else "Unknown"
                    
                    # 战队2 - 第二个 td.team-cell
                    team2_elem = result_div.select_one("div.team2 .team") or result_div.select_one(".line-align.team2 .team")
                    team2 = team2_elem.get_text(strip=True) if team2_elem else "Unknown"
                    
                    # 比分 - td.result-score 内的 span.score-won 和 span.score-lost
                    score_elem = result_div.select_one("td.result-score")
                    if score_elem:
                        score_text = score_elem.get_text(strip=True)
                        parts = score_text.split("-")
                        score1 = int(parts[0].strip()) if parts[0].strip().isdigit() else 0
                        score2 = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip().isdigit() else 0
                    else:
                        score1, score2 = 0, 0
                    
                    # 赛事名
                    event_elem = result_con.select_one(".event-name") or result_con.select_one("td:last-child")
                    event = event_elem.get_text(strip=True) if event_elem else "Unknown"
                    
                    # 链接
                    link_elem = result_con.select_one("a[href*='/matches/']")
                    href = link_elem.get("href", "") if link_elem else ""
                    
                    result_data = {
                        "team1": team1,
                        "team2": team2,
                        "score1": score1,
                        "score2": score2,
                        "event": event,
                        "url": f"{self.BASE_URL}{href}" if href else ""
                    }
                    
                    results.append(result_data)
                except Exception as e:
                    self.logger.debug(f"解析结果行失败: {e}")
                    continue
            
            return {
                "message": f"成功获取 {len(results)} 场比赛结果",
                "data": results,
                "source": "hltv",
                "success": len(results) > 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取比赛结果失败: {e}")
            return {
                "message": f"获取比赛结果失败: {str(e)}",
                "data": [],
                "source": "hltv",
                "success": False,
                "error": str(e)
            }

    async def get_player_info(self, player_name: str) -> Dict[str, Any]:
        """获取选手信息"""
        try:
            # 使用正确的搜索URL
            search_url = f"{self.BASE_URL}/search?query={player_name}"
            self.logger.info(f"正在搜索选手: {search_url}")
            
            html = await self._fetch(search_url)
            soup = BeautifulSoup(html, "html.parser")
            
            # 使用正确的选择器 - a[href*='/player/']
            player_link = soup.select_one("a[href*='/player/']")
            if not player_link:
                return {
                    "message": f"未找到选手 '{player_name}'",
                    "data": {},
                    "source": "hltv",
                    "success": False
                }
            
            href = player_link.get("href", "")
            player_url = self.BASE_URL + str(href) if href else ""
            
            # 从href提取选手ID和名称 (格式: /player/11893/zywoo)
            href_parts = href.strip("/").split("/")
            player_id = href_parts[1] if len(href_parts) > 1 else ""
            player_slug = href_parts[2] if len(href_parts) > 2 else ""
            
            # 获取选手详情页
            player_html = await self._fetch(player_url)
            player_soup = BeautifulSoup(player_html, "html.parser")
            
            # 获取选手全名
            full_name_elem = player_soup.select_one(".playerRealname")
            full_name = full_name_elem.get_text(strip=True) if full_name_elem else player_name
            
            # 获取战队
            team_elem = player_soup.select_one(".playerTeam a")
            team = team_elem.get_text(strip=True) if team_elem else "Unknown"
            
            # 获取国籍
            country_elem = player_soup.select_one(".playerRealname .flag")
            country = country_elem.get("title", "Unknown") if country_elem else "Unknown"
            
            # 获取Rating 3.0 (从选手主页的 .player-stat)
            rating_elem = player_soup.select_one(".player-stat .statsVal")
            rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"
            
            # 获取详细统计数据 - 访问 /stats/players/{id}/{name} 页面
            stats = {}
            summary_stats = {}
            if player_id and player_slug:
                try:
                    stats_url = f"{self.BASE_URL}/stats/players/{player_id}/{player_slug}"
                    self.logger.info(f"正在获取选手统计: {stats_url}")
                    stats_html = await self._fetch(stats_url)
                    stats_soup = BeautifulSoup(stats_html, "html.parser")
                    
                    # 解析 .stats-row 获取详细统计
                    stat_rows = stats_soup.select(".stats-row")
                    for row in stat_rows:
                        spans = row.select("span")
                        if len(spans) >= 2:
                            label = spans[0].get_text(strip=True).lower()
                            value = spans[1].get_text(strip=True)
                            stats[label] = value
                    
                    # 解析 .player-summary-stat-box-data-wrapper 获取KAST等数据
                    summary_wrappers = stats_soup.select(".player-summary-stat-box-data-wrapper")
                    for wrapper in summary_wrappers:
                        label_elem = wrapper.select_one(".player-summary-stat-box-data-text")
                        value_elem = wrapper.select_one(".player-summary-stat-box-data")
                        if label_elem and value_elem:
                            # 标签格式: "KASTKASTPercentage..." 取前几个字符
                            label_text = label_elem.get_text(strip=True)
                            # 提取主标签 (如 KAST, DPR, ADR, KPR)
                            for key in ["KAST", "DPR", "ADR", "KPR", "Rating", "Multi-kill", "Round swing"]:
                                if label_text.startswith(key):
                                    value = value_elem.get_text(strip=True)
                                    summary_stats[key.lower()] = value
                                    break
                except Exception as e:
                    self.logger.debug(f"获取统计页面失败: {e}")
            
            player_data = {
                "name": player_name,
                "full_name": full_name,
                "team": team,
                "country": country,
                "rating": rating if rating != "N/A" else stats.get("rating 2.0", "N/A"),
                "kd_ratio": stats.get("k/d ratio", "N/A"),
                "dpr": stats.get("deaths / round", summary_stats.get("dpr", "N/A")),
                "kast": summary_stats.get("kast", "N/A"),
                "impact": stats.get("impact rating", "N/A"),
                "adr": stats.get("damage / round", summary_stats.get("adr", "N/A")),
                "kpr": stats.get("kills / round", summary_stats.get("kpr", "N/A")),
                "apr": stats.get("assists / round", "N/A"),
                "headshot_pct": stats.get("headshot %", "N/A"),
                "maps_played": stats.get("maps played", "N/A"),
                "rounds_played": stats.get("rounds played", "N/A"),
                "total_kills": stats.get("total kills", "N/A"),
                "total_deaths": stats.get("total deaths", "N/A"),
                "url": player_url
            }
            
            return {
                "message": f"成功获取选手 '{player_name}' 的信息",
                "data": player_data,
                "source": "hltv",
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取选手信息失败: {e}")
            return {
                "message": f"获取选手信息失败: {str(e)}",
                "data": {},
                "source": "hltv",
                "success": False,
                "error": str(e)
            }

    async def get_team_info(self, team_name: str) -> Dict[str, Any]:
        """获取战队详细信息"""
        try:
            # 使用正确的搜索URL
            search_url = f"{self.BASE_URL}/search?query={team_name}"
            self.logger.info(f"正在搜索战队: {search_url}")
            
            html = await self._fetch(search_url)
            soup = BeautifulSoup(html, "html.parser")
            
            # 使用正确的选择器 - a[href*='/team/']
            team_link = soup.select_one("a[href*='/team/']")
            if not team_link:
                return {
                    "message": f"未找到战队 '{team_name}'",
                    "data": {},
                    "source": "hltv",
                    "success": False
                }
            
            href = team_link.get("href", "")
            team_url = self.BASE_URL + str(href) if href else ""
            
            # 获取战队详情页
            team_html = await self._fetch(team_url)
            team_soup = BeautifulSoup(team_html, "html.parser")
            
            # 获取战队名
            name_elem = team_soup.select_one(".profile-team-name")
            actual_name = name_elem.get_text(strip=True) if name_elem else team_name
            
            # 获取排名
            rank_elem = team_soup.select_one(".profile-team-stat:first-child .right")
            rank = rank_elem.get_text(strip=True) if rank_elem else "N/A"
            
            # 获取成员
            members = []
            player_elems = team_soup.select(".bodyshot-team-bg a")
            for player in player_elems[:5]:
                nick = player.select_one(".text-ellipsis")
                if nick:
                    members.append(nick.get_text(strip=True))
            
            # 获取教练
            coach_elem = team_soup.select_one(".profile-team-coach .text-ellipsis")
            coach = coach_elem.get_text(strip=True) if coach_elem else "Unknown"
            
            team_data = {
                "name": actual_name,
                "rank": rank,
                "members": members,
                "coach": coach,
                "url": team_url
            }
            
            return {
                "message": f"成功获取战队 '{team_name}' 的信息",
                "data": team_data,
                "source": "hltv",
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取战队信息失败: {e}")
            return {
                "message": f"获取战队信息失败: {str(e)}",
                "data": {},
                "source": "hltv",
                "success": False,
                "error": str(e)
            }
