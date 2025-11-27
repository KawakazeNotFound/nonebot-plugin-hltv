from flask import Flask, jsonify, request
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)

BASE_URL = "https://www.hltv.org"

def get_scraper():
    return cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

@app.route('/')
def index():
    return jsonify({
        "status": "ok",
        "endpoints": [
            "/api/matches",
            "/api/rankings",
            "/api/results",
            "/api/player?name=<player_name>",
            "/api/team?name=<team_name>"
        ]
    })

@app.route('/api/matches')
def get_matches():
    try:
        scraper = get_scraper()
        resp = scraper.get(f"{BASE_URL}/matches", timeout=15)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        matches = []
        
        for match_elem in soup.select("div.match")[:15]:
            try:
                match_link = match_elem.select_one("a[href*='/matches/']")
                if not match_link:
                    continue
                
                href = str(match_link.get("href", ""))
                time_elem = match_elem.select_one(".match-time")
                time_text = time_elem.get_text(strip=True) if time_elem else "TBD"
                
                meta_elem = match_elem.select_one(".match-meta")
                bo_type = meta_elem.get_text(strip=True) if meta_elem else "bo3"
                
                team_names = match_elem.select("div.match-teamname")
                if len(team_names) >= 2:
                    team1 = team_names[0].get_text(strip=True)
                    team2 = team_names[1].get_text(strip=True)
                else:
                    continue
                
                event_name = "Unknown"
                if href:
                    parts = str(href).split("/")[-1].split("-vs-")
                    if len(parts) > 1:
                        event_parts = parts[1].split("-", 1)
                        if len(event_parts) > 1:
                            event_name = event_parts[1].replace("-", " ").title()
                
                matches.append({
                    "team1": team1,
                    "team2": team2,
                    "event": event_name,
                    "time": time_text,
                    "bo_type": bo_type,
                    "url": f"{BASE_URL}{href}" if href else ""
                })
            except:
                continue
        
        return jsonify({"success": True, "data": matches})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/rankings')
def get_rankings():
    try:
        limit = request.args.get('limit', 30, type=int)
        scraper = get_scraper()
        resp = scraper.get(f"{BASE_URL}/ranking/teams", timeout=15)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        teams = []
        
        for team_elem in soup.select(".ranked-team")[:limit]:
            try:
                rank_elem = team_elem.select_one("span.position")
                rank_text = rank_elem.get_text(strip=True) if rank_elem else ""
                rank = rank_text.replace("#", "") if rank_text else str(len(teams) + 1)
                
                name_elem = team_elem.select_one("span.name")
                team_name = name_elem.get_text(strip=True) if name_elem else "Unknown"
                
                points_elem = team_elem.select_one("span.points")
                points_text = points_elem.get_text(strip=True) if points_elem else "(0)"
                points = "".join(c for c in points_text if c.isdigit())
                
                members_elems = team_elem.select(".rankingNicknames")
                members = [m.get_text(strip=True) for m in members_elems[:5]]
                
                teams.append({
                    "rank": int(rank) if rank.isdigit() else len(teams) + 1,
                    "title": team_name,
                    "points": int(points) if points else 0,
                    "members": members
                })
            except:
                continue
        
        return jsonify({"success": True, "data": teams})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/results')
def get_results():
    try:
        scraper = get_scraper()
        resp = scraper.get(f"{BASE_URL}/results", timeout=15)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        
        for result_con in soup.select(".result-con")[:20]:
            try:
                result_div = result_con.select_one("div.result")
                if not result_div:
                    continue
                
                team1_elem = result_div.select_one("div.team1 .team") or result_div.select_one(".line-align.team1 .team")
                team1 = team1_elem.get_text(strip=True) if team1_elem else "Unknown"
                
                team2_elem = result_div.select_one("div.team2 .team") or result_div.select_one(".line-align.team2 .team")
                team2 = team2_elem.get_text(strip=True) if team2_elem else "Unknown"
                
                score_elem = result_div.select_one("td.result-score")
                if score_elem:
                    score_text = score_elem.get_text(strip=True)
                    parts = score_text.split("-")
                    score1 = int(parts[0].strip()) if parts[0].strip().isdigit() else 0
                    score2 = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip().isdigit() else 0
                else:
                    score1, score2 = 0, 0
                
                event_elem = result_con.select_one(".event-name")
                event = event_elem.get_text(strip=True) if event_elem else "Unknown"
                
                results.append({
                    "team1": team1,
                    "team2": team2,
                    "score1": score1,
                    "score2": score2,
                    "event": event
                })
            except:
                continue
        
        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/player')
def get_player():
    name = request.args.get('name', '')
    if not name:
        return jsonify({"success": False, "error": "请提供选手名称"}), 400
    
    try:
        scraper = get_scraper()
        
        # 搜索选手
        search_resp = scraper.get(f"{BASE_URL}/search?query={name}", timeout=15)
        search_resp.raise_for_status()
        soup = BeautifulSoup(search_resp.text, "html.parser")
        
        player_link = soup.select_one("a[href*='/player/']")
        if not player_link:
            return jsonify({"success": False, "error": f"未找到选手 '{name}'"})
        
        href = str(player_link.get("href", ""))
        player_url = BASE_URL + href
        
        href_parts = href.strip("/").split("/")
        player_id = href_parts[1] if len(href_parts) > 1 else ""
        player_slug = href_parts[2] if len(href_parts) > 2 else ""
        
        # 获取选手页面
        player_resp = scraper.get(player_url, timeout=15)
        player_resp.raise_for_status()
        player_soup = BeautifulSoup(player_resp.text, "html.parser")
        
        full_name_elem = player_soup.select_one(".playerRealname")
        full_name = full_name_elem.get_text(strip=True) if full_name_elem else name
        
        team_elem = player_soup.select_one(".playerTeam a")
        team = team_elem.get_text(strip=True) if team_elem else "Unknown"
        
        country_elem = player_soup.select_one(".playerRealname .flag")
        country = country_elem.get("title", "Unknown") if country_elem else "Unknown"
        
        rating_elem = player_soup.select_one(".player-stat .statsVal")
        rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"
        
        # 获取统计页面
        stats = {}
        summary_stats = {}
        if player_id and player_slug:
            try:
                stats_url = f"{BASE_URL}/stats/players/{player_id}/{player_slug}"
                stats_resp = scraper.get(stats_url, timeout=15)
                stats_resp.raise_for_status()
                stats_soup = BeautifulSoup(stats_resp.text, "html.parser")
                
                for row in stats_soup.select(".stats-row"):
                    spans = row.select("span")
                    if len(spans) >= 2:
                        label = spans[0].get_text(strip=True).lower()
                        value = spans[1].get_text(strip=True)
                        stats[label] = value
                
                for wrapper in stats_soup.select(".player-summary-stat-box-data-wrapper"):
                    label_elem = wrapper.select_one(".player-summary-stat-box-data-text")
                    value_elem = wrapper.select_one(".player-summary-stat-box-data")
                    if label_elem and value_elem:
                        label_text = label_elem.get_text(strip=True)
                        for key in ["KAST", "DPR", "ADR", "KPR", "Rating"]:
                            if label_text.startswith(key):
                                summary_stats[key.lower()] = value_elem.get_text(strip=True)
                                break
            except:
                pass
        
        player_data = {
            "name": name,
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
            "url": player_url
        }
        
        return jsonify({"success": True, "data": player_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/team')
def get_team():
    name = request.args.get('name', '')
    if not name:
        return jsonify({"success": False, "error": "请提供战队名称"}), 400
    
    try:
        scraper = get_scraper()
        
        search_resp = scraper.get(f"{BASE_URL}/search?query={name}", timeout=15)
        search_resp.raise_for_status()
        soup = BeautifulSoup(search_resp.text, "html.parser")
        
        team_link = soup.select_one("a[href*='/team/']")
        if not team_link:
            return jsonify({"success": False, "error": f"未找到战队 '{name}'"})
        
        href = str(team_link.get("href", ""))
        team_url = BASE_URL + href
        
        team_resp = scraper.get(team_url, timeout=15)
        team_resp.raise_for_status()
        team_soup = BeautifulSoup(team_resp.text, "html.parser")
        
        name_elem = team_soup.select_one(".profile-team-name")
        actual_name = name_elem.get_text(strip=True) if name_elem else name
        
        rank_elem = team_soup.select_one(".profile-team-stat:first-child .right")
        rank = rank_elem.get_text(strip=True) if rank_elem else "N/A"
        
        members = []
        for player in team_soup.select(".bodyshot-team-bg a")[:5]:
            nick = player.select_one(".text-ellipsis")
            if nick:
                members.append(nick.get_text(strip=True))
        
        coach_elem = team_soup.select_one(".profile-team-coach .text-ellipsis")
        coach = coach_elem.get_text(strip=True) if coach_elem else "Unknown"
        
        team_data = {
            "name": actual_name,
            "rank": rank,
            "members": members,
            "coach": coach,
            "url": team_url
        }
        
        return jsonify({"success": True, "data": team_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Vercel 需要这个
app = app
