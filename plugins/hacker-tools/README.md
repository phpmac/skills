# hacker-tools

资产侦查和网络空间测绘工具集 MCP 插件, 聚合多个搜索引擎和安全查询 API.

## 工具列表

| 工具 | 功能 | 数据源 |
|------|------|--------|
| `fofa_search` | FOFA 网络空间测绘搜索 | FOFA API |
| `hunter_search` | Hunter 网络空间测绘搜索 | Hunter API |
| `censys_search` | Censys 网络空间测绘搜索 (Platform API v3) | Censys API |
| `dnsdumpster_query` | DNS 域名信息查询 | DNSDumpster |
| `virustotal_query` | 域名安全信息查询 | VirusTotal API |
| `nvd_search` | NVD CVE 漏洞搜索 | NVD API |
| `nvd_get_cve` | NVD 单个 CVE 详情 | NVD API |
| `ip_query` | IP 地理位置查询 | IP API |
| `http_request` | 模拟浏览器 HTTP 请求 | 内置 |

## 环境变量配置

在 `~/.claude/hacker-tools/.env` 中配置:

```bash
# FOFA (二选一, 优先用 key)
FOFA_KEY=xxx
FOFA_EMAIL=xxx

# Hunter
HUNTER_API_KEY=xxx

# Censys
CENSYS_TOKEN=xxx
CENSYS_ORGANIZATION_ID=xxx

# VirusTotal
VIRUSTOTAL_API_KEY=xxx
```

> 未配置的 API Key 不会影响其他工具使用, 缺少 Key 的工具会返回提示.

## Censys 搜索语法 (CenQL)

```
# 全文本搜索 (推荐搜索域名)
"example.com"

# 字段查询
host.ip="1.1.1.1"
host.services.port=443
host.services:(port="22" and protocol="SSH")
web.hostname: "example.com"
host.services.scan_time > "now-1d"
```

## 安装

插件通过 `.mcp.json` 自动加载, 使用 `uv run` 启动 MCP 服务器.
