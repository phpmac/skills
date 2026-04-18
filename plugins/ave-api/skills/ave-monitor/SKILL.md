---
name: ave-monitor
description: Ave.ai 新收录代币定时监控与自动侦查. 当需要定时监控新币/批量收集代币官网/自动信息侦查, 或用户提到新币监控/定时收集/ave监控时使用.
---

# Ave 新币定时监控

**优先使用 MCP 工具**: 全部操作通过 MCP 工具完成, 禁止手动调用 API.

## 流程

```
1. ave_new_tokens 采集9链新币 (有官网的)
2. 提取官网顶级域名, 用 hacker-tools 侦查
3. 整理结果, 按项目结构保存
```

## 第1步: 采集代币

遍历 9 条链, 取第1页新收录:

```
ave_new_tokens(chain="<链>", page=1, page_size=10)
```

链: bsc/eth/solana/base/arbitrum/polygon/optimism/avalanche/fantom

只保留有 website 的代币, 按 contract+chain 去重.

## 第2步: 信息侦查

对官网顶级域名, 依次调用 hacker-tools:

| 工具 | 查询内容 |
|------|---------|
| `dnsdumpster_query` | DNS 解析记录/子域名 |
| `virustotal_query` | 域名安全信息 |
| `fofa_search` | 网络空间测绘 |
| `hunter_search` | 网络空间测绘 |
| `censys_search` | 证书/Web 属性 |
| `ip_query` | IP 地理位置 |

## 第3步: 保存结果

按项目结构保存到项目文档:

```markdown
## [代币名] ([链])

- 合约: (完整地址)
- 官网: (URL)
- X/TG: (有则记录)
- 介绍: (原样)

### 侦查结果
- DNS: (dnsdumpster 结果摘要)
- VirusTotal: (安全评估)
- FOFA: (资产信息)
- HUNTER: (资产信息)
- Censys: (证书/Web信息)
- IP: (地理位置)

### ARL
- task_id: (提交后记录)
```
