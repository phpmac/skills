---
name: command-development
description: 当用户要求 "create a slash command", "add a command", "write a custom command", "define command arguments", "use command frontmatter", "organize commands", "create command with file references", "interactive command", "use AskUserQuestion in command", 或需要关于斜杠命令结构, YAML frontmatter 字段, 动态参数, 命令中的 bash 执行, 用户交互模式或 Claude Code 命令开发最佳实践的指导时应使用此技能.
version: 0.2.0
---

# Claude Code 命令开发

## 概述

斜杠命令是定义为 Markdown 文件的常用提示, Claude 在交互会话期间执行它们. 理解命令结构, frontmatter 选项和动态功能可以创建强大的, 可重用的工作流.

**关键概念:**
- 命令的 Markdown 文件格式
- 用于配置的 YAML frontmatter
- 动态参数和文件引用
- 用于获取上下文的 Bash 执行
- 命令组织和命名空间

## 命令基础

### 什么是斜杠命令?

斜杠命令是一个 Markdown 文件, 包含 Claude 在调用时执行的提示. 命令提供:
- **可重用性**: 一次定义, 反复使用
- **一致性**: 标准化常用工作流
- **共享**: 在团队或项目间分发
- **效率**: 快速访问复杂提示

### 关键: 命令是给 Claude 的指令

**命令是为 agent 消费编写的, 不是为人类消费编写的.**

当用户调用 `/command-name` 时, 命令内容成为 Claude 的指令. 将命令作为关于做什么的指令写 给 Claude, 而不是作为给用户的消息.

**正确方法 (给 Claude 的指令):**
```markdown
审查此代码的安全漏洞, 包括:
- SQL 注入
- XSS 攻击
- 认证问题

提供具体的行号和严重程度评级.
```

**错误方法 (给用户的消息):**
```markdown
此命令将审查您的代码安全问题.
您将收到包含漏洞详细信息的报告.
```

第一个示例告诉 Claude 做什么. 第二个告诉用户将发生什么但没有指示 Claude. 始终使用第一种方法.

### 命令位置

**项目命令** (与团队共享):
- 位置: `.claude/commands/`
- 范围: 在特定项目中可用
- 标签: 在 `/help` 中显示为 "(project)"
- 用于: 团队工作流, 项目特定任务

**个人命令** (随处可用):
- 位置: `~/.claude/commands/`
- 范围: 在所有项目中可用
- 标签: 在 `/help` 中显示为 "(user)"
- 用于: 个人工作流, 跨项目工具

**插件命令** (与插件捆绑):
- 位置: `plugin-name/commands/`
- 范围: 插件安装时可用
- 标签: 在 `/help` 中显示为 "(plugin-name)"
- 用于: 插件特定功能

## 文件格式

### 基本结构

命令是带有 `.md` 扩展名的 Markdown 文件:

```
.claude/commands/
├── review.md           # /review 命令
├── test.md             # /test 命令
└── deploy.md           # /deploy 命令
```

**简单命令:**
```markdown
审查此代码的安全漏洞, 包括:
- SQL 注入
- XSS 攻击
- 认证绕过
- 不安全的数据处理
```

基本命令不需要 frontmatter.

### 带 YAML Frontmatter

使用 YAML frontmatter 添加配置:

```markdown
---
description: 审查代码安全问题
allowed-tools: Read, Grep, Bash(git:*)
model: sonnet
---

审查此代码的安全漏洞...
```

## YAML Frontmatter 字段

### description

**目的:** 在 `/help` 中显示的简要描述
**类型:** 字符串
**默认:** 命令提示的第一行

```yaml
---
description: 审查 PR 的代码质量
---
```

**最佳实践:** 清晰, 可操作的描述 (60 字符以内)

### allowed-tools

**目的:** 指定命令可以使用的工具
**类型:** 字符串或数组
**默认:** 从对话继承

```yaml
---
allowed-tools: Read, Write, Edit, Bash(git:*)
---
```

**模式:**
- `Read, Write, Edit` - 特定工具
- `Bash(git:*)` - 仅限 git 命令的 Bash
- `*` - 所有工具 (很少需要)

**使用场景:** 命令需要特定工具访问时

### model

**目的:** 指定命令执行的模型
**类型:** 字符串 (sonnet, opus, haiku)
**默认:** 从对话继承

```yaml
---
model: haiku
---
```

**用例:**
- `haiku` - 快速, 简单命令
- `sonnet` - 标准工作流
- `opus` - 复杂分析

### argument-hint

**目的:** 为自动完成记录预期参数
**类型:** 字符串
**默认:** 无

```yaml
---
argument-hint: [pr-number] [priority] [assignee]
---
```

**优点:**
- 帮助用户理解命令参数
- 改进命令发现
- 记录命令接口

## 动态参数

### 使用 $ARGUMENTS

将所有参数捕获为单个字符串:

```markdown
---
description: 按编号修复问题
argument-hint: [issue-number]
---

按照我们的编码标准和最佳实践修复问题 #$ARGUMENTS.
```

**用法:**
```
> /fix-issue 123
> /fix-issue 456
```

**展开为:**
```
按照我们的编码标准和最佳实践修复问题 #123...
按照我们的编码标准和最佳实践修复问题 #456...
```

### 使用位置参数

使用 `$1`, `$2`, `$3` 等捕获单个参数:

```markdown
---
description: 用优先级和负责人审查 PR
argument-hint: [pr-number] [priority] [assignee]
---

审查拉取请求 #$1, 优先级为 $2.
审查后, 分配给 $3 进行跟进.
```

**用法:**
```
> /review-pr 123 high alice
```

**展开为:**
```
审查拉取请求 #123, 优先级为 high.
审查后, 分配给 alice 进行跟进.
```

## 文件引用

### 使用 @ 语法

在命令中包含文件内容:

```markdown
---
description: 审查特定文件
argument-hint: [file-path]
---

审查 @$1 的:
- 代码质量
- 最佳实践
- 潜在 bug
```

**用法:**
```
> /review-file src/api/users.ts
```

**效果:** Claude 在处理命令前读取 `src/api/users.ts`

### 多文件引用

引用多个文件:

```markdown
比较 @src/old-version.js 与 @src/new-version.js

识别:
- 破坏性更改
- 新功能
- Bug 修复
```

## 命令中的 Bash 执行

命令可以内联执行 bash 命令, 在 Claude 处理命令前动态收集上下文. 这对于包含仓库状态, 环境信息或项目特定上下文很有用.

**何时使用:**
- 包含动态上下文 (git 状态, 环境变量等)
- 收集项目/仓库状态
- 构建上下文感知工作流

**语法:**
```markdown
当前分支: !`git branch --show-current`
待处理更改: !`git status --short`
```

## 命令组织

### 扁平结构

小命令集的简单组织:

```
.claude/commands/
├── build.md
├── test.md
├── deploy.md
├── review.md
└── docs.md
```

**使用场景:** 5-15 个命令, 无明确类别

### 命名空间结构

在子目录中组织命令:

```
.claude/commands/
├── ci/
│   ├── build.md        # /build (project:ci)
│   ├── test.md         # /test (project:ci)
│   └── lint.md         # /lint (project:ci)
├── git/
│   ├── commit.md       # /commit (project:git)
│   └── pr.md           # /pr (project:git)
└── docs/
    ├── generate.md     # /generate (project:docs)
    └── publish.md      # /publish (project:docs)
```

**优点:**
- 按类别逻辑分组
- 命名空间在 `/help` 中显示
- 更容易找到相关命令

**使用场景:** 15+ 个命令, 明确类别

## 最佳实践

### 命令设计

1. **单一职责:** 一个命令, 一个任务
2. **清晰描述:** 在 `/help` 中自解释
3. **显式依赖:** 需要时使用 `allowed-tools`
4. **记录参数:** 始终提供 `argument-hint`
5. **一致命名:** 使用动词-名词模式 (review-pr, fix-issue)

### 参数处理

1. **验证参数:** 在提示中检查必需参数
2. **提供默认值:** 参数缺失时建议默认值
3. **记录格式:** 解释预期的参数格式
4. **处理边缘情况:** 考虑缺失或无效参数

### Bash 命令

1. **限制范围:** 使用 `Bash(git:*)` 而不是 `Bash(*)`
2. **安全命令:** 避免破坏性操作
3. **处理错误:** 考虑命令失败
4. **保持快速:** 长时间运行的命令会减慢调用

## 常见模式

### 审查模式

```markdown
---
description: 审查代码更改
allowed-tools: Read, Bash(git:*)
---

更改的文件: !`git diff --name-only`

审查每个文件的:
1. 代码质量和风格
2. 潜在 bug 或问题
3. 测试覆盖率
4. 文档需求

为每个文件提供具体反馈.
```

### 测试模式

```markdown
---
description: 为特定文件运行测试
argument-hint: [test-file]
allowed-tools: Bash(npm:*)
---

运行测试: !`npm test $1`

分析结果并为失败建议修复.
```

### 文档模式

```markdown
---
description: 为文件生成文档
argument-hint: [source-file]
---

为 @$1 生成全面文档, 包括:
- 函数/类描述
- 参数文档
- 返回值描述
- 使用示例
- 边缘情况和错误
```

## 故障排除

**命令未出现:**
- 检查文件是否在正确目录中
- 验证 `.md` 扩展名存在
- 确保有效的 Markdown 格式
- 重启 Claude Code

**参数不工作:**
- 验证 `$1`, `$2` 语法正确
- 检查 `argument-hint` 与用法匹配
- 确保没有多余空格

**Bash 执行失败:**
- 检查 `allowed-tools` 包含 Bash
- 验证反引号中的命令语法
- 首先在终端中测试命令
- 检查所需权限

**文件引用不工作:**
- 验证 `@` 语法正确
- 检查文件路径有效
- 确保 Read 工具允许
- 使用绝对或项目相对路径

## 插件特定功能

### CLAUDE_PLUGIN_ROOT 变量

插件命令可以访问 `${CLAUDE_PLUGIN_ROOT}`, 一个解析为插件绝对路径的环境变量.

**目的:**
- 可移植地引用插件文件
- 执行插件脚本
- 加载插件配置
- 访问插件模板

**基本用法:**

```markdown
---
description: 使用插件脚本分析
allowed-tools: Bash(node:*)
---

运行分析: !`node ${CLAUDE_PLUGIN_ROOT}/scripts/analyze.js $1`

审查结果并报告发现.
```

**常见模式:**

```markdown
# 执行插件脚本
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/script.sh`

# 加载插件配置
@${CLAUDE_PLUGIN_ROOT}/config/settings.json

# 使用插件模板
@${CLAUDE_PLUGIN_ROOT}/templates/report.md

# 访问插件资源
@${CLAUDE_PLUGIN_ROOT}/docs/reference.md
```

### 插件命令组织

插件命令从 `commands/` 目录自动发现:

```
plugin-name/
├── commands/
│   ├── foo.md              # /foo (plugin:plugin-name)
│   ├── bar.md              # /bar (plugin:plugin-name)
│   └── utils/
│       └── helper.md       # /helper (plugin:plugin-name:utils)
└── plugin.json
```

**命名空间优点:**
- 命令逻辑分组
- 在 `/help` 输出中显示
- 避免名称冲突
- 组织相关命令

---

有关详细的 frontmatter 字段规范, 请参阅 `references/frontmatter-reference.md`.
有关插件特定功能和模式, 请参阅 `references/plugin-features-reference.md`.
有关命令模式示例, 请参阅 `examples/` 目录.
