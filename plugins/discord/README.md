# Discord

通过 Discord Bot 将消息桥接到 Claude Code.

Bot 收到消息后, MCP 服务转发给 Claude, 并提供回复/反应/编辑等工具.

## 前置条件

- [Bun](https://bun.sh) — MCP 服务运行在 Bun 上. 安装: `curl -fsSL https://bun.sh/install | bash`

## 快速设置

**1. 创建 Discord 应用和 Bot.**

前往 [Discord 开发者门户](https://discord.com/developers/applications) 点击 **New Application**.

在侧栏选择 **Bot**, 设置 Bot 用户名.

在 **Privileged Gateway Intents** 启用 **Message Content Intent** — 否则 Bot 收到的消息内容为空.

**2. 生成 Bot Token.**

在 **Bot** 页面, 点击 **Token** 下的 **Reset Token**. 复制 Token (仅显示一次).

**3. 邀请 Bot 到服务器.**

进入 **OAuth2** -> **URL Generator**. 选择 `bot` scope. 在 **Bot Permissions** 启用:

- View Channels / Send Messages / Send Messages in Threads
- Read Message History / Attach Files / Add Reactions

复制生成的 URL 并打开, 将 Bot 添加到服务器.

**4. 配置 Token.**

```
/discord:configure <你的Bot Token>
```

Token 写入 `~/.claude/channels/discord/.env`.

**5. 启动频道.**

```sh
claude --channels plugin:discord@phpmac-skills
```

**6. 配对.**

在 Discord 给 Bot 发私信, Bot 回复配对码. 在 Claude Code 中:

```
/discord:access pair <配对码>
```

**7. 锁定访问.**

配对完成后切换到白名单模式:

```
/discord:access policy allowlist
```

## 提供的工具

| 工具 | 用途 |
|------|------|
| `reply` | 发送消息, 支持 `reply_to` 线程回复和 `files` 附件 (最多10个, 25MB/个) |
| `react` | 对消息添加 emoji 反应. Unicode emoji 直接使用, 自定义 emoji 用 `<:name:id>` |
| `edit_message` | 编辑 Bot 已发送的消息, 适合进度更新 |
| `fetch_messages` | 拉取频道最近消息 (最多100条), 带消息ID用于回复 |
| `download_attachment` | 下载指定消息的附件到 `~/.claude/channels/discord/inbox/` |

## 访问控制

详见 [ACCESS.md](./ACCESS.md).

状态文件: `~/.claude/channels/discord/access.json`, 每次消息到达时重新读取, 修改即时生效.
