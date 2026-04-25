# ave-api

Ave.ai 代币数据查询 MCP 插件, 支持新收录代币/详情/热门/涨幅榜/搜索/合约审计.

## 工具列表

| 工具 | 功能 |
|------|------|
| `ave_new_tokens` | 最新收录代币列表 (支持按链筛选) |
| `ave_token_info` | 代币详情 (官网/TG/X/买卖税/风险/持有人) |
| `ave_hot_tokens` | 热门代币列表 |
| `ave_gainers` | 涨幅榜 |
| `ave_search` | 代币搜索 (名称/符号/合约地址) |
| `ave_contract_info` | 代币合约安全审计信息 |
| `ave_get_captcha` | 获取验证码图片 (自动打开, 用户识别后提交答案) |
| `ave_verify_captcha` | 提交验证码答案, 获取 ave_token |

## 环境变量配置

在 `~/.claude/ave/.env` 中配置:

```bash
AVE_TOKEN=xxx
```

## 认证流程

1. 调用 `ave_get_captcha` 获取验证码图片 (自动弹出)
2. 识别图片中的数学答案
3. 调用 `ave_verify_captcha` 提交答案获取 token
4. 手动更新 `~/.claude/ave/.env` 中的 `AVE_TOKEN`

## 支持的链

bsc, eth, solana, base, arbitrum, polygon, optimism, avalanche, fantom

## 安装

插件通过 `.mcp.json` 自动加载, 使用 `uv run` 启动 MCP 服务器.
