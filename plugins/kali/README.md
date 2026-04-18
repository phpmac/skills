# kali

Kali Linux 远程 MCP 服务器, 通过 SSH 连接远程 Kali 主机执行安全工具.

## 工具列表

| 工具 | 用途 |
|------|------|
| `nmap_scan` | Nmap 端口扫描/服务探测 |
| `nikto_scan` | Nikto Web 服务器扫描 |
| `dirb_scan` | Dirb 目录扫描 |
| `gobuster_scan` | Gobuster 目录/DNS/vhost 发现 |
| `sqlmap_scan` | SQLmap SQL 注入检测 |
| `hydra_attack` | Hydra 密码爆破 |
| `john_crack` | John the Ripper 密码破解 |
| `wpscan_analyze` | WPScan WordPress 漏洞扫描 |
| `enum4linux_scan` | Enum4linux Windows/Samba 枚举 |
| `metasploit_run` | Metasploit 模块执行 |
| `execute_command` | 任意命令执行 |
| `server_health` | 服务器健康检查 |

## SSH 连接配置

插件通过 SSH alias `kali` 连接, 需在 `~/.ssh/config` 中配置:

```
Host kali
    HostName <KALI_SERVER_IP>
    User root
    IdentityAgent "~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock"
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 600
```

### 前置条件

- SSH 密钥已配置 (推荐使用 1Password SSH Agent)
- Kali 服务器已安装 `mcp-server`
- `~/.ssh/sockets/` 目录存在: `mkdir -p ~/.ssh/sockets`

### 测试连接

```bash
ssh kali mcp-server
```

MCP 配置已内置在 `.mcp.json` 中: `"command": "ssh", "args": ["kali", "mcp-server"]`

## 技术栈

- SSH stdio 传输
- Kali Linux 远程 MCP Server
