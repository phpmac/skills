---
name: 插件结构
description: 当用户要求 "create a plugin", "scaffold a plugin", "understand plugin structure", "organize plugin components", "set up plugin.json", "use ${CLAUDE_PLUGIN_ROOT}", "add commands/agents/skills/hooks", "configure auto-discovery", 或需要关于插件目录布局, 清单配置, 组件组织, 文件命名约定或 Claude Code 插件架构最佳实践的指导时应使用此技能.
version: 0.1.0
---

# Claude Code 插件结构

## 概述

Claude Code 插件遵循标准化的目录结构, 具有自动组件发现功能. 理解此结构可以创建组织良好, 可维护的插件, 与 Claude Code 无缝集成.

**关键概念:**
- 用于自动发现的传统目录布局
- `.claude-plugin/plugin.json` 中的清单驱动配置
- 基于组件的组织 (commands, agents, skills, hooks)
- 使用 `${CLAUDE_PLUGIN_ROOT}` 的可移植路径引用
- 显式与自动发现的组件加载

## 目录结构

每个 Claude Code 插件都遵循此组织模式:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # 必需: 插件清单
├── commands/                 # 斜杠命令 (.md 文件)
├── agents/                   # 子 agent 定义 (.md 文件)
├── skills/                   # Agent 技能 (子目录)
│   └── skill-name/
│       └── SKILL.md         # 每个技能必需
├── hooks/
│   └── hooks.json           # 事件处理器配置
├── .mcp.json                # MCP 服务器定义
└── scripts/                 # 辅助脚本和工具
```

**关键规则:**

1. **清单位置**: `plugin.json` 清单必须在 `.claude-plugin/` 目录中
2. **组件位置**: 所有组件目录 (commands, agents, skills, hooks) 必须在插件根级别, 不能嵌套在 `.claude-plugin/` 中
3. **可选组件**: 仅为插件实际使用的组件创建目录
4. **命名约定**: 所有目录和文件名使用 kebab-case

## 插件清单 (plugin.json)

清单定义插件元数据和配置. 位于 `.claude-plugin/plugin.json`:

### 必需字段

```json
{
  "name": "plugin-name"
}
```

**名称要求:**
- 使用 kebab-case 格式 (带连字符的小写)
- 必须在已安装的插件中唯一
- 无空格或特殊字符
- 示例: `code-review-assistant`, `test-runner`, `api-docs`

### 推荐元数据

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "插件目的简要说明",
  "author": {
    "name": "作者姓名",
    "email": "author@example.com",
    "url": "https://example.com"
  },
  "homepage": "https://docs.example.com",
  "repository": "https://github.com/user/plugin-name",
  "license": "MIT",
  "keywords": ["testing", "automation", "ci-cd"]
}
```

**版本格式**: 遵循语义版本控制 (MAJOR.MINOR.PATCH)
**关键词**: 用于插件发现和分类

### 组件路径配置

指定组件的自定义路径 (补充默认目录):

```json
{
  "name": "plugin-name",
  "commands": "./custom-commands",
  "agents": ["./agents", "./specialized-agents"],
  "hooks": "./config/hooks.json",
  "mcpServers": "./.mcp.json"
}
```

**重要**: 自定义路径补充默认值 - 它们不会替换它们. 默认目录和自定义路径中的组件都会加载.

**路径规则:**
- 必须相对于插件根目录
- 必须以 `./` 开头
- 不能使用绝对路径
- 支持数组用于多个位置

## 组件组织

### 命令

**位置**: `commands/` 目录
**格式**: 带 YAML frontmatter 的 Markdown 文件
**自动发现**: `commands/` 中的所有 `.md` 文件自动加载

**示例结构**:
```
commands/
├── review.md        # /review 命令
├── test.md          # /test 命令
└── deploy.md        # /deploy 命令
```

**文件格式**:
```markdown
---
name: command-name
description: 命令描述
---

命令实现指令...
```

**用法**: 命令作为原生斜杠命令集成到 Claude Code 中

### Agents

**位置**: `agents/` 目录
**格式**: 带 YAML frontmatter 的 Markdown 文件
**自动发现**: `agents/` 中的所有 `.md` 文件自动加载

**示例结构**:
```
agents/
├── code-reviewer.md
├── test-generator.md
└── refactorer.md
```

**文件格式**:
```markdown
---
description: Agent 角色和专业知识
capabilities:
  - 特定任务 1
  - 特定任务 2
---

详细的 agent 指令和知识...
```

**用法**: 用户可以手动调用 agents, 或 Claude Code 根据任务上下文自动选择它们

### 技能

**位置**: `skills/` 目录, 每个技能一个子目录
**格式**: 每个技能在自己的目录中, 包含 `SKILL.md` 文件
**自动发现**: 技能子目录中的所有 `SKILL.md` 文件自动加载

**示例结构**:
```
skills/
├── api-testing/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── test-runner.py
│   └── references/
│       └── api-spec.md
└── database-migrations/
    ├── SKILL.md
    └── examples/
        └── migration-template.sql
```

**SKILL.md 格式**:
```markdown
---
name: 技能名称
description: 何时使用此技能
version: 1.0.0
---

技能指令和指导...
```

**支持文件**: 技能可以在子目录中包含脚本, 参考, 示例或资源

**用法**: Claude Code 根据与描述匹配的任务上下文自动激活技能

### Hooks

**位置**: `hooks/hooks.json` 或在 `plugin.json` 中内联
**格式**: 定义事件处理器的 JSON 配置
**注册**: 当插件启用时 hooks 自动注册

**示例结构**:
```
hooks/
├── hooks.json           # Hook 配置
└── scripts/
    ├── validate.sh      # Hook 脚本
    └── check-style.sh   # Hook 脚本
```

**配置格式**:
```json
{
  "PreToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{
      "type": "command",
      "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/validate.sh",
      "timeout": 30
    }]
  }]
}
```

**可用事件**: PreToolUse, PostToolUse, Stop, SubagentStop, SessionStart, SessionEnd, UserPromptSubmit, PreCompact, Notification

**用法**: Hooks 自动执行以响应 Claude Code 事件

### MCP 服务器

**位置**: 插件根目录的 `.mcp.json` 或在 `plugin.json` 中内联
**格式**: MCP 服务器定义的 JSON 配置
**自动启动**: 当插件启用时服务器自动启动

**示例格式**:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/server.js"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

**用法**: MCP 服务器与 Claude Code 的工具系统无缝集成

## 可移植路径引用

### ${CLAUDE_PLUGIN_ROOT}

对所有插件内部路径引用使用 `${CLAUDE_PLUGIN_ROOT}` 环境变量:

```json
{
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh"
}
```

**重要原因**: 插件安装在不同位置, 取决于:
- 用户安装方法 (marketplace, 本地, npm)
- 操作系统约定
- 用户偏好

**使用位置**:
- Hook 命令路径
- MCP 服务器命令参数
- 脚本执行引用
- 资源文件路径

**永远不要使用**:
- 硬编码的绝对路径 (`/Users/name/plugins/...`)
- 从工作目录的相对路径 (命令中的 `./scripts/...`)
- 主目录快捷方式 (`~/plugins/...`)

### 路径解析规则

**在清单 JSON 字段中** (hooks, MCP 服务器):
```json
"command": "${CLAUDE_PLUGIN_ROOT}/scripts/tool.sh"
```

**在组件文件中** (commands, agents, skills):
```markdown
引用脚本位于: ${CLAUDE_PLUGIN_ROOT}/scripts/helper.py
```

**在执行的脚本中**:
```bash
#!/bin/bash
# ${CLAUDE_PLUGIN_ROOT} 可作为环境变量使用
source "${CLAUDE_PLUGIN_ROOT}/lib/common.sh"
```

## 文件命名约定

### 组件文件

**命令**: 使用 kebab-case `.md` 文件
- `code-review.md` -> `/code-review`
- `run-tests.md` -> `/run-tests`
- `api-docs.md` -> `/api-docs`

**Agents**: 使用描述角色的 kebab-case `.md` 文件
- `test-generator.md`
- `code-reviewer.md`
- `performance-analyzer.md`

**技能**: 使用 kebab-case 目录名称
- `api-testing/`
- `database-migrations/`
- `error-handling/`

### 支持文件

**脚本**: 使用适当的扩展名和描述性的 kebab-case 名称
- `validate-input.sh`
- `generate-report.py`
- `process-data.js`

**文档**: 使用 kebab-case markdown 文件
- `api-reference.md`
- `migration-guide.md`
- `best-practices.md`

**配置**: 使用标准名称
- `hooks.json`
- `.mcp.json`
- `plugin.json`

## 自动发现机制

Claude Code 自动发现和加载组件:

1. **插件清单**: 当插件启用时读取 `.claude-plugin/plugin.json`
2. **命令**: 扫描 `commands/` 目录中的 `.md` 文件
3. **Agents**: 扫描 `agents/` 目录中的 `.md` 文件
4. **技能**: 扫描 `skills/` 中包含 `SKILL.md` 的子目录
5. **Hooks**: 从 `hooks/hooks.json` 或清单加载配置
6. **MCP 服务器**: 从 `.mcp.json` 或清单加载配置

**发现时机**:
- 插件安装: 组件向 Claude Code 注册
- 插件启用: 组件可供使用
- 无需重启: 更改在下一个 Claude Code 会话中生效

**覆盖行为**: `plugin.json` 中的自定义路径补充 (而不是替换) 默认目录

## 最佳实践

### 组织

1. **逻辑分组**: 将相关组件分组在一起
   - 将测试相关的命令, agents 和技能放在一起
   - 在 `scripts/` 中为不同目的创建子目录

2. **最小化清单**: 保持 `plugin.json` 精简
   - 仅在必要时指定自定义路径
   - 依赖标准布局的自动发现
   - 仅对简单情况使用内联配置

3. **文档**: 包含 README 文件
   - 插件根目录: 总体目的和用法
   - 组件目录: 特定指导
   - 脚本目录: 用法和要求

### 命名

1. **一致性**: 在组件间使用一致的命名
   - 如果命令是 `test-runner`, 命名相关 agent 为 `test-runner-agent`
   - 将技能目录名称与其目的匹配

2. **清晰度**: 使用指示目的的描述性名称
   - 好: `api-integration-testing/`, `code-quality-checker.md`
   - 避免: `utils/`, `misc.md`, `temp.sh`

3. **长度**: 平衡简洁性和清晰度
   - 命令: 2-3 个单词 (`review-pr`, `run-ci`)
   - Agents: 清楚地描述角色 (`code-reviewer`, `test-generator`)
   - 技能: 主题聚焦 (`error-handling`, `api-design`)

### 可移植性

1. **始终使用 ${CLAUDE_PLUGIN_ROOT}**: 永远不要硬编码路径
2. **在多个系统上测试**: 在 macOS, Linux, Windows 上验证
3. **记录依赖**: 列出所需的工具和版本
4. **避免系统特定功能**: 使用可移植的 bash/Python 结构

### 维护

1. **一致版本控制**: 为发布更新 plugin.json 中的版本
2. **优雅弃用**: 在删除前清楚地标记旧组件
3. **记录破坏性更改**: 注意影响现有用户的更改
4. **彻底测试**: 更改后验证所有组件工作

## 常见模式

### 最小插件

单个命令无依赖:
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json    # 仅名称字段
└── commands/
    └── hello.md       # 单个命令
```

### 全功能插件

包含所有组件类型的完整插件:
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/          # 面向用户的命令
├── agents/            # 专门的子 agents
├── skills/            # 自动激活的技能
├── hooks/             # 事件处理器
│   ├── hooks.json
│   └── scripts/
├── .mcp.json          # 外部集成
└── scripts/           # 共享工具
```

### 技能聚焦插件

仅提供技能的插件:
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    ├── skill-one/
    │   └── SKILL.md
    └── skill-two/
        └── SKILL.md
```

## 故障排除

**组件未加载**:
- 验证文件在正确的目录中且扩展名正确
- 检查 YAML frontmatter 语法 (commands, agents, skills)
- 确保技能有 `SKILL.md` (不是 `README.md` 或其他名称)
- 确认插件在 Claude Code 设置中已启用

**路径解析错误**:
- 用 `${CLAUDE_PLUGIN_ROOT}` 替换所有硬编码路径
- 验证路径是相对的并且在清单中以 `./` 开头
- 检查引用的文件在指定路径是否存在
- 在 hook 脚本中使用 `echo $CLAUDE_PLUGIN_ROOT` 测试

**自动发现不工作**:
- 确认目录在插件根级别 (不在 `.claude-plugin/` 中)
- 检查文件命名遵循约定 (kebab-case, 正确的扩展名)
- 验证清单中的自定义路径正确
- 重启 Claude Code 以重新加载插件配置

**插件间冲突**:
- 使用唯一, 描述性的组件名称
- 如果需要, 使用插件名称为命令添加命名空间
- 在插件 README 中记录潜在冲突
- 考虑为相关功能添加命令前缀

---

有关详细示例和高级模式, 请参阅 `references/` 和 `examples/` 目录中的文件.
