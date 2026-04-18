# x-search

X (Twitter) 搜索 MCP 插件, 通过 xAI Grok API 搜索推文和网页内容.

## 工具列表

| 工具 | 功能 |
|------|------|
| `x_search` | 搜索 X/Twitter 推文 (支持用户/日期/图片/视频过滤) |
| `x_read_tweet` | 读取指定推文或线程的完整内容 |
| `x_web_search` | 使用 xAI 搜索互联网 |

## 环境变量配置

在 `~/.claude/x-search/.env` 中配置:

```bash
XAI_API_KEY=xxx
```

## x_search 参数

| 参数 | 说明 |
|------|------|
| `prompt` | 搜索关键词/语义描述 (必填) |
| `handles` | 筛选指定用户 (最多 10 个) |
| `exclude` | 排除指定用户 (最多 10 个) |
| `from_date` | 起始日期 YYYY-MM-DD |
| `to_date` | 结束日期 YYYY-MM-DD |
| `images` | 启用图片理解 |
| `video` | 启用视频理解 |

## 安装

插件通过 `.mcp.json` 自动加载, 使用 `uv run` 启动 MCP 服务器.
