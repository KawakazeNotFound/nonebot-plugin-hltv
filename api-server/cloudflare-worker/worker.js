/**
 * HLTV API Proxy - Cloudflare Worker
 * 部署到 Cloudflare Workers 以绕过 HLTV 的 IP 封锁
 */

const BASE_URL = "https://www.hltv.org";

// CORS 头
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

// 模拟浏览器请求头
const browserHeaders = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
  "Accept-Language": "en-US,en;q=0.9",
  "Accept-Encoding": "gzip, deflate, br",
  "Cache-Control": "no-cache",
  "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
  "Sec-Ch-Ua-Mobile": "?0",
  "Sec-Ch-Ua-Platform": '"Windows"',
  "Sec-Fetch-Dest": "document",
  "Sec-Fetch-Mode": "navigate",
  "Sec-Fetch-Site": "none",
  "Sec-Fetch-User": "?1",
  "Upgrade-Insecure-Requests": "1",
};

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // 处理 CORS 预检请求
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // 路由处理
      if (path === "/" || path === "/api") {
        return jsonResponse({
          status: "ok",
          message: "HLTV API Proxy powered by Cloudflare Workers",
          endpoints: [
            "/api/matches",
            "/api/rankings?limit=30",
            "/api/results",
            "/api/events",
            "/api/player?name=device",
            "/api/team?name=Tyloo",
            "/api/proxy?path=/matches"
          ]
        });
      }

      if (path === "/api/matches") {
        return await handleMatches();
      }

      if (path === "/api/rankings") {
        const limit = parseInt(url.searchParams.get("limit") || "30");
        return await handleRankings(limit);
      }

      if (path === "/api/results") {
        return await handleResults();
      }

      if (path === "/api/events") {
        return await handleEvents();
      }

      if (path === "/api/player") {
        const name = url.searchParams.get("name");
        if (!name) {
          return jsonResponse({ success: false, error: "请提供选手名称 ?name=xxx" }, 400);
        }
        return await handlePlayer(name);
      }

      if (path === "/api/team") {
        const name = url.searchParams.get("name");
        if (!name) {
          return jsonResponse({ success: false, error: "请提供战队名称 ?name=xxx" }, 400);
        }
        return await handleTeam(name);
      }

      // 通用代理端点 - 直接转发到 HLTV
      if (path === "/api/proxy") {
        const hltvPath = url.searchParams.get("path") || "/";
        return await proxyToHLTV(hltvPath);
      }

      return jsonResponse({ error: "Not Found" }, 404);

    } catch (error) {
      return jsonResponse({ success: false, error: error.message }, 500);
    }
  }
};

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders
    }
  });
}

async function fetchHLTV(path) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: browserHeaders,
    cf: {
      // Cloudflare 特有的配置
      cacheTtl: 60,
      cacheEverything: false,
    }
  });
  
  if (!response.ok) {
    throw new Error(`HLTV 请求失败: ${response.status}`);
  }
  
  return await response.text();
}

async function proxyToHLTV(path) {
  const html = await fetchHLTV(path);
  return new Response(html, {
    headers: {
      "Content-Type": "text/html",
      ...corsHeaders
    }
  });
}

// 简单的 HTML 解析辅助函数
function extractText(html, selector) {
  // 这是一个简化版本，实际可能需要更复杂的解析
  const regex = new RegExp(`<[^>]*class="[^"]*${selector}[^"]*"[^>]*>([^<]*)<`, 'i');
  const match = html.match(regex);
  return match ? match[1].trim() : null;
}

function extractAllMatches(html, pattern) {
  const results = [];
  let match;
  const regex = new RegExp(pattern, 'gi');
  while ((match = regex.exec(html)) !== null) {
    results.push(match);
  }
  return results;
}

async function handleMatches() {
  try {
    const html = await fetchHLTV("/matches");
    
    // 提取比赛信息 - 使用正则表达式解析
    const matches = [];
    
    // 匹配 match 容器
    const matchPattern = /<div[^>]*class="[^"]*\bmatch\b[^"]*"[^>]*>([\s\S]*?)<\/div>\s*<\/div>\s*<\/div>/gi;
    const matchBlocks = html.match(matchPattern) || [];
    
    for (const block of matchBlocks.slice(0, 15)) {
      try {
        // 提取队伍名
        const teamPattern = /<div[^>]*class="[^"]*match-teamname[^"]*"[^>]*>([^<]+)<\/div>/gi;
        const teams = [];
        let teamMatch;
        while ((teamMatch = teamPattern.exec(block)) !== null) {
          teams.push(teamMatch[1].trim());
        }
        
        if (teams.length < 2) continue;
        
        // 提取时间
        const timeMatch = block.match(/<div[^>]*class="[^"]*match-time[^"]*"[^>]*>([^<]+)<\/div>/i);
        const time = timeMatch ? timeMatch[1].trim() : "TBD";
        
        // 提取 BO 类型
        const metaMatch = block.match(/<div[^>]*class="[^"]*match-meta[^"]*"[^>]*>([^<]+)<\/div>/i);
        const boType = metaMatch ? metaMatch[1].trim() : "bo3";
        
        // 提取链接和赛事
        const hrefMatch = block.match(/href="(\/matches\/[^"]+)"/i);
        const href = hrefMatch ? hrefMatch[1] : "";
        
        let event = "Unknown";
        if (href) {
          const parts = href.split("/").pop().split("-vs-");
          if (parts.length > 1) {
            const eventParts = parts[1].split("-").slice(1);
            event = eventParts.join(" ").replace(/\b\w/g, c => c.toUpperCase());
          }
        }
        
        matches.push({
          team1: teams[0],
          team2: teams[1],
          time: time,
          bo_type: boType,
          event: event,
          url: href ? `${BASE_URL}${href}` : ""
        });
      } catch (e) {
        continue;
      }
    }
    
    return jsonResponse({
      success: true,
      message: `成功获取 ${matches.length} 场比赛`,
      data: matches,
      source: "hltv-cf-worker"
    });
  } catch (error) {
    return jsonResponse({ success: false, error: error.message }, 500);
  }
}

async function handleRankings(limit = 30) {
  try {
    const html = await fetchHLTV("/ranking/teams");
    
    const teams = [];
    
    // 匹配排名行
    const rankPattern = /<div[^>]*class="[^"]*ranked-team[^"]*"[^>]*>([\s\S]*?)<\/div>\s*<\/div>\s*<\/div>\s*<\/div>/gi;
    const rankBlocks = html.match(rankPattern) || [];
    
    for (const block of rankBlocks.slice(0, limit)) {
      try {
        // 排名
        const posMatch = block.match(/<span[^>]*class="[^"]*position[^"]*"[^>]*>#?(\d+)<\/span>/i);
        const rank = posMatch ? parseInt(posMatch[1]) : teams.length + 1;
        
        // 队名
        const nameMatch = block.match(/<span[^>]*class="[^"]*name[^"]*"[^>]*>([^<]+)<\/span>/i);
        const name = nameMatch ? nameMatch[1].trim() : "Unknown";
        
        // 积分 - 格式: <span class="points">(930 points)</span>
        const pointsMatch = block.match(/<span[^>]*class="[^"]*points[^"]*"[^>]*>\((\d+)/i);
        const points = pointsMatch ? parseInt(pointsMatch[1]) : 0;
        
        teams.push({
          rank: rank,
          title: name,
          points: points
        });
      } catch (e) {
        continue;
      }
    }
    
    return jsonResponse({
      success: true,
      message: `成功获取 ${teams.length} 支战队排名`,
      data: teams,
      source: "hltv-cf-worker"
    });
  } catch (error) {
    return jsonResponse({ success: false, error: error.message }, 500);
  }
}

async function handleResults() {
  try {
    const html = await fetchHLTV("/results");
    
    const results = [];
    
    // 简化解析 - 提取结果容器
    const resultPattern = /<div[^>]*class="[^"]*result-con[^"]*"[^>]*>([\s\S]*?)<\/a>/gi;
    const resultBlocks = html.match(resultPattern) || [];
    
    for (const block of resultBlocks.slice(0, 20)) {
      try {
        // 提取队伍
        const teamPattern = /<div[^>]*class="[^"]*team[^"]*"[^>]*>([^<]+)<\/div>/gi;
        const teams = [];
        let teamMatch;
        while ((teamMatch = teamPattern.exec(block)) !== null) {
          const text = teamMatch[1].trim();
          if (text && !text.match(/^\d/)) {
            teams.push(text);
          }
        }
        
        // 比分 - 格式: <span class="score-won">13</span> - <span class="score-lost">7</span>
        // 或者: <td class="result-score">..scores..</td>
        let score1 = 0, score2 = 0;
        
        // 方法1: 匹配 score-won 和 score-lost
        const scoreWonMatch = block.match(/<span[^>]*class="[^"]*score-won[^"]*"[^>]*>(\d+)<\/span>/i);
        const scoreLostMatch = block.match(/<span[^>]*class="[^"]*score-lost[^"]*"[^>]*>(\d+)<\/span>/i);
        
        if (scoreWonMatch && scoreLostMatch) {
          // 需要判断哪个队伍赢了
          // 在 result-score 中，第一个 span 是左边队伍的分数
          const scoreSection = block.match(/<td[^>]*class="[^"]*result-score[^"]*"[^>]*>([\s\S]*?)<\/td>/i);
          if (scoreSection) {
            const scores = scoreSection[1].match(/>(\d+)</g);
            if (scores && scores.length >= 2) {
              score1 = parseInt(scores[0].replace(/[><]/g, ''));
              score2 = parseInt(scores[1].replace(/[><]/g, ''));
            }
          }
        }
        
        // 方法2: 如果上面失败，尝试简单的数字匹配
        if (score1 === 0 && score2 === 0) {
          const simpleScoreMatch = block.match(/>(\d+)<\/span>\s*-\s*<span[^>]*>(\d+)</i);
          if (simpleScoreMatch) {
            score1 = parseInt(simpleScoreMatch[1]);
            score2 = parseInt(simpleScoreMatch[2]);
          }
        }
        
        // 赛事
        const eventMatch = block.match(/<span[^>]*class="[^"]*event-name[^"]*"[^>]*>([^<]+)<\/span>/i);
        const event = eventMatch ? eventMatch[1].trim() : "Unknown";
        
        if (teams.length >= 2) {
          results.push({
            team1: teams[0],
            team2: teams[1],
            score1: score1,
            score2: score2,
            event: event
          });
        }
      } catch (e) {
        continue;
      }
    }
    
    return jsonResponse({
      success: true,
      message: `成功获取 ${results.length} 场比赛结果`,
      data: results,
      source: "hltv-cf-worker"
    });
  } catch (error) {
    return jsonResponse({ success: false, error: error.message }, 500);
  }
}

async function handlePlayer(name) {
  try {
    // 搜索选手
    const searchHtml = await fetchHLTV(`/search?query=${encodeURIComponent(name)}`);
    
    // 查找选手链接
    const playerMatch = searchHtml.match(/href="(\/player\/\d+\/[^"]+)"/i);
    if (!playerMatch) {
      return jsonResponse({ success: false, error: `未找到选手 '${name}'` });
    }
    
    const playerPath = playerMatch[1];
    const playerHtml = await fetchHLTV(playerPath);
    
    // 解析选手信息 - 结构: <div class="playerRealname"...><img...> Mathieu Herbaut</div>
    // 名字在 <img> 标签之后
    const fullNameMatch = playerHtml.match(/<div[^>]*class="[^"]*playerRealname[^"]*"[^>]*>(?:<img[^>]*>)?\s*([^<]+)<\/div>/i);
    const fullName = fullNameMatch ? fullNameMatch[1].trim() : name;
    
    // 提取战队名 - 从 team 链接: <a href="/team/..." itemprop="text">Vitality</a>
    const teamMatch = playerHtml.match(/<a[^>]*href="\/team\/\d+\/[^"]*"[^>]*itemprop="text"[^>]*>([^<]+)<\/a>/i);
    const team = teamMatch ? teamMatch[1].trim() : "Unknown";
    
    // 提取 Rating 3.0 - 结构: <div class="player-stat"><b>Rating 3.0</b><span class="statsVal">\n<p>1.27</p>
    const ratingMatch = playerHtml.match(/<b>Rating 3\.0<\/b><span[^>]*class="[^"]*statsVal[^"]*"[^>]*>\s*<p>([0-9.]+)<\/p>/i);
    const rating = ratingMatch ? ratingMatch[1] : "N/A";
    
    // 获取统计页面
    const pathParts = playerPath.split("/");
    const playerId = pathParts[2];
    const playerSlug = pathParts[3];
    
    let stats = {};
    try {
      const statsHtml = await fetchHLTV(`/stats/players/${playerId}/${playerSlug}`);
      
      // KPR
      const kprMatch = statsHtml.match(/Kills\s*\/\s*round[\s\S]*?<span[^>]*>([0-9.]+)<\/span>/i);
      if (kprMatch) stats.kpr = kprMatch[1];
      
      // ADR
      const adrMatch = statsHtml.match(/Damage\s*\/\s*round[\s\S]*?<span[^>]*>([0-9.]+)<\/span>/i);
      if (adrMatch) stats.adr = adrMatch[1];
      
      // KAST
      const kastMatch = statsHtml.match(/KAST[\s\S]*?([0-9.]+)%/i);
      if (kastMatch) stats.kast = kastMatch[1] + "%";
    } catch (e) {
      // 统计页面获取失败，继续
    }
    
    return jsonResponse({
      success: true,
      data: {
        name: name,
        full_name: fullName,
        team: team,
        rating: rating,
        kpr: stats.kpr || "N/A",
        adr: stats.adr || "N/A",
        kast: stats.kast || "N/A",
        url: `${BASE_URL}${playerPath}`
      },
      source: "hltv-cf-worker"
    });
  } catch (error) {
    return jsonResponse({ success: false, error: error.message }, 500);
  }
}

// 赛事级别定义
const EVENT_TIERS = {
  MAJOR: { tier: "S", name: "Major" },
  INTLLAN: { tier: "A", name: "国际LAN" },
  // 以下级别不再获取
  // REGIONALLAN: { tier: "B", name: "地区LAN" },
  // LOCALLAN: { tier: "C", name: "本地LAN" },
  // ONLINE: { tier: "C", name: "线上赛" },
  // OTHER: { tier: "D", name: "其他" },
};

async function handleEvents() {
  try {
    const events = [];
    
    // 只获取 S 和 A 级别赛事 (MAJOR 和 INTLLAN)
    for (const [eventType, tierInfo] of Object.entries(EVENT_TIERS)) {
      try {
        const html = await fetchHLTV(`/events?eventType=${eventType}`);
        
        // 解析大型赛事 (big-event) - 结构: <a href="/events/xxx" class="... big-event ...">内容</a>
        const bigEventPattern = /<a[^>]*href="(\/events\/\d+\/[^"]+)"[^>]*class="[^"]*big-event[^"]*"[^>]*>([\s\S]*?)<\/a>/gi;
        let match;
        
        while ((match = bigEventPattern.exec(html)) !== null) {
          const eventUrl = match[1];
          const eventBlock = match[2];
          
          // 提取赛事名称
          const nameMatch = eventBlock.match(/<div[^>]*class="[^"]*big-event-name[^"]*"[^>]*>([^<]+)<\/div>/i);
          const name = nameMatch ? nameMatch[1].trim() : "Unknown";
          
          // 提取地点
          const locationMatch = eventBlock.match(/<span[^>]*class="[^"]*big-event-location[^"]*"[^>]*>([^<]+)<\/span>/i);
          const location = locationMatch ? locationMatch[1].trim() : "TBD";
          
          // 提取日期
          const dateMatches = eventBlock.match(/data-unix="(\d+)"/g);
          let startDate = null, endDate = null;
          if (dateMatches && dateMatches.length >= 2) {
            startDate = parseInt(dateMatches[0].match(/\d+/)[0]);
            endDate = parseInt(dateMatches[1].match(/\d+/)[0]);
          }
          
          events.push({
            name: name,
            tier: tierInfo.tier,
            tier_name: tierInfo.name,
            event_type: eventType,
            location: location,
            start_date: startDate ? new Date(startDate).toISOString().split('T')[0] : null,
            end_date: endDate ? new Date(endDate).toISOString().split('T')[0] : null,
            url: `${BASE_URL}${eventUrl}`
          });
        }
        
        // 解析小型赛事 (small-event) - 结构: <a href="/events/xxx" class="... small-event ...">内容</a>
        const smallEventPattern = /<a[^>]*href="(\/events\/\d+\/[^"]+)"[^>]*class="[^"]*small-event[^"]*"[^>]*>([\s\S]*?)<\/a>/gi;
        
        while ((match = smallEventPattern.exec(html)) !== null) {
          const eventUrl = match[1];
          const eventBlock = match[2];
          
          // 提取赛事名称 - <div class="table-cell name">xxx</div>
          const nameMatch = eventBlock.match(/<div[^>]*class="[^"]*\bname\b[^"]*"[^>]*>([^<]+)<\/div>/i);
          const name = nameMatch ? nameMatch[1].trim() : "Unknown";
          
          // 提取日期
          const dateMatches = eventBlock.match(/data-unix="(\d+)"/g);
          let startDate = null, endDate = null;
          if (dateMatches && dateMatches.length >= 2) {
            startDate = parseInt(dateMatches[0].match(/\d+/)[0]);
            endDate = parseInt(dateMatches[1].match(/\d+/)[0]);
          }
          
          events.push({
            name: name,
            tier: tierInfo.tier,
            tier_name: tierInfo.name,
            event_type: eventType,
            location: "TBD",
            start_date: startDate ? new Date(startDate).toISOString().split('T')[0] : null,
            end_date: endDate ? new Date(endDate).toISOString().split('T')[0] : null,
            url: `${BASE_URL}${eventUrl}`
          });
        }
      } catch (e) {
        // 某个类型获取失败，继续下一个
        continue;
      }
    }
    
    // 按开始日期排序（最近的在前）
    events.sort((a, b) => {
      if (!a.start_date) return 1;
      if (!b.start_date) return -1;
      return new Date(a.start_date) - new Date(b.start_date);
    });
    
    return jsonResponse({
      success: true,
      message: `成功获取 ${events.length} 场重要赛事 (S级: Major, A级: 国际LAN)`,
      data: events,
      source: "hltv-cf-worker"
    });
  } catch (error) {
    return jsonResponse({ success: false, error: error.message }, 500);
  }
}

async function handleTeam(name) {
  try {
    // 搜索战队
    const searchHtml = await fetchHLTV(`/search?query=${encodeURIComponent(name)}`);
    
    // 查找战队链接
    const teamMatch = searchHtml.match(/href="(\/team\/\d+\/[^"]+)"/i);
    if (!teamMatch) {
      return jsonResponse({ success: false, error: `未找到战队 '${name}'` });
    }
    
    const teamPath = teamMatch[1];
    const teamHtml = await fetchHLTV(teamPath);
    
    // 解析战队信息
    const nameMatch = teamHtml.match(/<h1[^>]*class="[^"]*profile-team-name[^"]*"[^>]*>([^<]+)<\/h1>/i);
    const actualName = nameMatch ? nameMatch[1].trim() : name;
    
    // 排名
    const rankMatch = teamHtml.match(/#(\d+)/);
    const rank = rankMatch ? `#${rankMatch[1]}` : "N/A";
    
    // 成员
    const members = [];
    const memberPattern = /<span[^>]*class="[^"]*text-ellipsis[^"]*"[^>]*>([^<]+)<\/span>/gi;
    let memberMatch;
    while ((memberMatch = memberPattern.exec(teamHtml)) !== null && members.length < 5) {
      const text = memberMatch[1].trim();
      if (text && text.length > 1 && text.length < 20) {
        members.push(text);
      }
    }
    
    return jsonResponse({
      success: true,
      data: {
        name: actualName,
        rank: rank,
        members: members.slice(0, 5),
        url: `${BASE_URL}${teamPath}`
      },
      source: "hltv-cf-worker"
    });
  } catch (error) {
    return jsonResponse({ success: false, error: error.message }, 500);
  }
}
