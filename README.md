<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-hltv

_✨ CS2/CSGO HLTV 信息查询插件 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/KawakazeNotFound/nonebot-plugin-hltv.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-hltv">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-hltv.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

## 📖 介绍

一个用于查询 [HLTV](https://www.hltv.org) CS2/CSGO 电竞数据的 NoneBot2 插件。

支持查询：
- 实时比赛信息
- 战队世界排名
- 比赛结果
- 选手详细数据（Rating、KPR、ADR、KAST 等）
- 战队信息（阵容、教练、排名）

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-hltv

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-hltv
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-hltv
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-hltv
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_hltv"]

</details>

## 📦 依赖

- `nonebot2` >= 2.0.0
- `nonebot-adapter-onebot` >= 2.0.0
- `aiohttp` >= 3.8.0

## ⚙️ 配置

在 nonebot2 项目的 `.env` 文件中添加以下配置（均为可选）：

### API Server 配置

插件默认使用内置的 Cloudflare Workers API 代理，无需额外配置即可使用。

如果你想使用自己部署的 API Server：

| 配置项 | 默认值 | 说明 |
|:------|:------:|:-----|
| `hltv_api_url` | 内置API | 自定义 API Server 地址 |

> 💡 **提示**: 插件开箱即用，无需任何配置。如需自建 API Server，请参考下方的 [API Server 部署](#-api-server-部署) 章节。

### 缓存配置

| 配置项 | 默认值 | 说明 |
|:------|:------:|:-----|
| `cache_duration_matches` | 60 | 比赛数据缓存时间（秒） |
| `cache_duration_teams` | 3600 | 战队排名缓存时间（秒） |
| `cache_duration_results` | 300 | 比赛结果缓存时间（秒） |

### 查询配置

| 配置项 | 默认值 | 说明 |
|:------|:------:|:-----|
| `max_matches_per_query` | 10 | 每次查询最大比赛数量 |
| `max_teams_in_ranking` | 30 | 战队排名最大数量 |
| `max_results_per_query` | 20 | 每次查询最大结果数量 |
| `default_query_days` | 1 | 默认查询天数 |

### 功能开关

| 配置项 | 默认值 | 说明 |
|:------|:------:|:-----|
| `enable_caching` | True | 启用缓存机制 |
| `enable_detailed_logging` | True | 启用详细日志 |
| `enable_topic_detection` | True | 启用话题检测（被动识别CS2相关话题） |

### 显示配置

| 配置项 | 默认值 | 说明 |
|:------|:------:|:-----|
| `include_match_ratings` | True | 包含比赛重要程度 |
| `show_live_scores` | True | 显示实时比分 |
| `show_ranking_changes` | True | 显示排名变化 |

## 🎉 使用

### 指令表

| 指令 | 别名 | 说明 |
|:-----|:-----|:-----|
| `/cs2比赛` | `cs2匹配`、`查看cs2比赛` | 查看当前 CS2 实时比赛 |
| `/cs2战队 <战队名>` | `查询战队`、`cs2队伍` | 查询战队信息（排名、阵容、教练） |
| `/cs2结果` | `查看结果`、`cs2结果查询` | 查看最近比赛结果 |
| `/cs2排名` | `战队排名`、`csgo排名` | 查看战队世界排名 Top 10 |
| `/cs2选手 <选手名>` | `查询选手`、`cs2选手查询` | 查询选手详细信息 |

### 示例

```
/cs2比赛
/cs2战队 Vitality
/cs2选手 ZywOo
/cs2排名
/cs2结果
```

### 选手数据说明

查询选手时返回的数据包括：

| 字段 | 说明 |
|:-----|:-----|
| Rating 2.0 | HLTV 综合评分 |
| KPR | 每回合击杀数 |
| ADR | 每回合伤害 |
| KAST | 击杀/助攻/存活/换人回合占比 |
| K/D | 击杀死亡比 |
| Impact | 影响力评分 |

## 📝 更新日志

### v3.1.0
- 新增 API Server 支持，解决服务器 IP 被屏蔽问题
- 配置项 `hltv_api_url` 用于指定 API Server 地址

### v1.0.0
- 首次发布
- 支持查询实时比赛、战队排名、比赛结果
- 支持查询选手和战队详细信息
- 使用 cloudscraper 获取真实 HLTV 数据

## 🌐 API Server 部署

如果你的服务器 IP 被 HLTV/Cloudflare 屏蔽，可以部署一个 API Server 作为代理。

### Vercel 部署

1. 在你的项目中创建 `api-server/` 目录

2. 创建 `api-server/vercel.json`：
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

3. 创建 `api-server/requirements.txt`：
```
cloudscraper>=1.2.71
beautifulsoup4>=4.12.0
flask>=3.0.0
```

4. 创建 `api-server/api/index.py`（完整代码见项目的 `api-server/` 目录）

5. 部署到 Vercel：
```bash
cd api-server
npx vercel --prod
```

6. 配置 `.env`：
```
hltv_api_url=https://your-app.vercel.app
```

### Cloudflare Workers 部署

参考项目中的 `api-server/cloudflare-worker.js` 文件。

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](./LICENSE) 文件
