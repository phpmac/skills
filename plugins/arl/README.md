# ARL

ARL (Asset Reconnaissance Lighthouse) 资产侦察灯塔 MCP 插件, 通过 ARL 平台 API 管理扫描任务和查询结果.

## 工具列表

| 工具 | 功能 |
|------|------|
| `get_policies` | 查询扫描策略列表 |
| `get_tasks` | 查询任务列表/状态 |
| `add_task` | 添加扫描任务 (直接参数) |
| `task_by_policy` | 通过策略提交扫描任务 |
| `get_sites` | 查询站点/指纹信息 |
| `get_domains` | 查询域名解析信息 |
| `get_ips` | 查询 IP/端口/服务信息 |
| `get_wihs` | 查询 WIH 敏感信息 (API/密钥) |
| `restart_tasks` | 按任务 ID 重启任务 |
| `restart_tasks_by_status` | 按状态批量重启任务 |

## 环境变量配置

在 `~/.claude/arl/.env` 中配置:

```bash
ARL_URL=http://your-arl-server:5002
ARL_TOKEN=xxx
```

## 使用说明

- 提交任务后扫描需要时间, 记录 task_id 稍后查询
- 必须使用策略提交任务, 禁止直接配置参数
- `size` 参数不超过 100, 防止系统崩溃

## 安装

插件通过 `.mcp.json` 自动加载, 使用 `uv run` 启动 MCP 服务器.
