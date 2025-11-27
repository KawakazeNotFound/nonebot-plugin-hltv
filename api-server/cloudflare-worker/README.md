# HLTV API Proxy - Cloudflare Workers 版本

这是一个部署在 Cloudflare Workers 上的 HLTV API 代理服务，用于解决服务器 IP 被 HLTV/Cloudflare 屏蔽的问题。

## 为什么选择 Cloudflare Workers？

1. **不会被 Cloudflare 阻止** - Cloudflare 不会阻止自己的服务
2. **免费额度高** - 每天 10 万次请求免费
3. **全球 CDN** - 响应速度快
4. **无需 cloudscraper** - 直接用 fetch 就能访问 HLTV

## 部署步骤

### 1. 安装 Wrangler CLI

```bash
npm install -g wrangler
```

### 2. 登录 Cloudflare

```bash
wrangler login
```

### 3. 部署 Worker

```bash
cd api-server/cloudflare-worker
wrangler deploy
```

部署成功后会显示类似这样的 URL：
```
https://hltv-api-proxy.your-name.workers.dev
```

### 4. 配置插件

在你的 NoneBot2 项目的 `.env` 文件中添加：

```
hltv_api_url=https://hltv-api-proxy.your-name.workers.dev
```

## API 端点

| 端点 | 说明 |
|------|------|
| `/api/matches` | 获取实时比赛 |
| `/api/rankings?limit=30` | 获取战队排名 |
| `/api/results` | 获取比赛结果 |
| `/api/player?name=ZywOo` | 查询选手信息 |
| `/api/team?name=Vitality` | 查询战队信息 |
| `/api/proxy?path=/matches` | 通用代理（返回原始 HTML）|

## 测试

部署后可以直接访问测试：

```bash
curl https://hltv-api-proxy.your-name.workers.dev/api/matches
```

## 注意事项

- Cloudflare Workers 免费版有每天 10 万次请求的限制
- 单次请求最多运行 10ms CPU 时间（通常足够）
- 如果需要更多配额，可以升级到 Workers Paid（$5/月）
