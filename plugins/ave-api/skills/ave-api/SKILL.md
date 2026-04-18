---
name: ave-api
description: Ave.ai 代币数据查询. 当需要查询新收录代币/代币详情/热门代币/涨幅榜/搜索代币/合约审计, 或用户提到ave/收录/新币/代币信息时使用.
---

# Ave.ai 代币数据查询

**优先使用 MCP 工具**: 本插件已提供 MCP 工具 (`mcp__ave-api__ave_*`), 所有查询必须优先通过 MCP 工具完成, 禁止手动调用 API 或使用脚本.

## 环境配置

Token 文件: `~/.claude/ave/.env`

```env
AVE_TOKEN=your_token
```

## 工具列表

| 工具 | 用途 |
|------|------|
| `ave_new_tokens` | 最新收录代币列表 |
| `ave_token_info` | 代币详情 |
| `ave_hot_tokens` | 热门代币 |
| `ave_gainers` | 涨幅榜 |
| `ave_search` | 搜索代币 |
| `ave_contract_info` | 合约审计信息 |

## 输出规范

查询结果必须完整展示, 禁止省略/截断/转换:

- 合约地址: 显示完整地址, 禁止缩写
- 官网/Website/X(Twitter)/Telegram: 有则必显
- TVL/价格/涨跌幅/持有人数/风险分: 默认显示
- 项目介绍 (intro_cn): 原样展示, 禁止概括/缩短
- 买卖税: 代币详情时显示

表格列顺序: 代币名/合约地址/价格/涨跌幅/TVL/持有人/风险/官网/X/TG/介绍

## 支持的链

bsc, eth, solana, base, arbitrum, polygon, optimism, avalanche, fantom

## 常用操作

### 查看最新收录

```
ave_new_tokens(chain="bsc", page=1, page_size=10)
```

### 查看代币详情

```
ave_token_info(address="0x...", chain="bsc")
```

### 搜索代币

```
ave_search(keyword="TOKEN")
```

## API 参考

详细 API 接口文档见 [API 参考](references/api-reference.md).
