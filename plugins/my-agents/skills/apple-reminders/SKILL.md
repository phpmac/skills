---
name: apple-reminders
description: 当用户要求 "查看提醒事项", "添加提醒", "管理提醒", "Apple Reminders", "提醒列表", 或需要通过终端管理 macOS 提醒事项时应使用此技能. 需要安装 remindctl CLI 工具
homepage: https://github.com/steipete/remindctl
metadata: {"clawdbot":{"emoji":"⏰","os":["darwin"],"requires":{"bins":["remindctl"]},"install":[{"id":"brew","kind":"brew","formula":"steipete/tap/remindctl","bins":["remindctl"],"label":"Install remindctl via Homebrew"}]}}
---

# Apple 提醒事项管理 (remindctl)

通过 `remindctl` 在终端管理 macOS 提醒事项, 支持列表筛选/日期查询/脚本输出.

## 安装与权限

```bash
# 安装
brew install steipete/tap/remindctl

# 检查权限状态
remindctl status

# 请求访问权限
remindctl authorize
```

> 仅限 macOS, 首次使用需在弹窗中授予提醒事项权限. SSH 环境下需在本机授权.

## 查看提醒

| 命令 | 说明 |
|------|------|
| `remindctl` | 今日提醒(默认) |
| `remindctl today` | 今日 |
| `remindctl tomorrow` | 明日 |
| `remindctl week` | 本周 |
| `remindctl overdue` | 已逾期 |
| `remindctl upcoming` | 即将到来 |
| `remindctl completed` | 已完成 |
| `remindctl all` | 全部 |
| `remindctl 2026-01-04` | 指定日期 |

## 管理列表

| 命令 | 说明 |
|------|------|
| `remindctl list` | 列出所有列表 |
| `remindctl list Work` | 查看指定列表 |
| `remindctl list Projects --create` | 创建列表 |
| `remindctl list Work --rename Office` | 重命名列表 |
| `remindctl list Work --delete` | 删除列表 |

## 操作提醒

| 操作 | 命令 |
|------|------|
| 快速添加 | `remindctl add "买菜"` |
| 指定列表+日期 | `remindctl add --title "打电话" --list Personal --due tomorrow` |
| 编辑 | `remindctl edit 1 --title "新标题" --due 2026-01-04` |
| 完成 | `remindctl complete 1 2 3` |
| 删除 | `remindctl delete 4A83 --force` |

## 输出格式

| 参数 | 说明 |
|------|------|
| `--json` | JSON 格式(脚本用) |
| `--plain` | 纯文本 TSV |
| `--quiet` | 仅显示数量 |

## 日期格式

`--due` 和日期筛选支持: `today` / `tomorrow` / `yesterday` / `YYYY-MM-DD` / `YYYY-MM-DD HH:mm` / ISO 8601
