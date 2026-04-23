---
description: 通过分析对话模式或从明确指令创建 hooks 以防止不良行为
argument-hint: 可选, 指定要处理的具体行为
allowed-tools: ["Read", "Write", "AskUserQuestion", "Task", "Grep", "TodoWrite", "Skill"]
---

# Hookify - 从不良行为创建 Hooks

**首先: 使用 Skill 工具加载 hookify:writing-rules 技能** 以了解规则文件格式和语法.

通过分析对话或根据用户明确指令, 创建 hook 规则以阻止问题行为.

## 你的任务

你将帮助用户创建 hookify 规则以防止不良行为. 按以下步骤执行:

### 步骤 1: 收集行为信息

**如果提供了 $ARGUMENTS:**
- 用户已给出明确指令: `$ARGUMENTS`
- 仍需分析最近的对话 (最近 10-15 条用户消息) 以获取额外上下文
- 查找该行为发生的示例

**如果 $ARGUMENTS 为空:**
- 启动 conversation-analyzer Agent 以发现问题行为
- Agent 将扫描用户提示中的不满信号
- Agent 将返回结构化的分析结果

**分析对话时:**
使用 Task 工具启动 conversation-analyzer Agent:
```
{
  "subagent_type": "general-purpose",
  "description": "分析对话中的不良行为",
  "prompt": "你正在分析一个 Claude Code 对话, 以找出用户想要阻止的行为.

阅读当前对话中的用户消息, 识别:
1. 明确要求避免某事 (\"不要做 X\", \"停止做 Y\")
2. 纠正或回退 (用户修复 Claude 的操作)
3. 不满的反应 (\"你为什么要做 X?\", \"我没要求那个\")
4. 重复出现的问题 (同一问题多次出现)

对每个发现的问题, 提取:
- 使用了什么工具 (Bash, Edit, Write 等)
- 具体的模式或命令
- 为什么有问题
- 用户说明的原因

以结构化列表返回分析结果:
- category: 问题类型
- tool: 涉及的工具
- pattern: 要匹配的正则或字面模式
- context: 发生了什么
- severity: high/medium/low

重点关注最近的问题 (最近 20-30 条消息). 除非用户明确要求, 否则不要追溯更早的记录."
}
```

### 步骤 2: 向用户展示分析结果

收集到行为信息后 (来自参数或 Agent), 使用 AskUserQuestion 向用户展示:

**问题 1: 要 hookify 哪些行为?**
- 标题: "创建规则"
- multiSelect: true
- 选项: 列出每个检测到的行为 (最多 4 个)
  - 标签: 简短描述 (如 "阻止 rm -rf")
  - 描述: 为什么有问题

**问题 2: 对每个选中的行为, 询问操作方式:**
- "应该阻止操作还是仅警告?"
- 选项:
  - "仅警告" (action: warn - 显示消息但允许)
  - "阻止操作" (action: block - 阻止执行)

**问题 3: 询问示例模式:**
- "什么模式应该触发此规则?"
- 显示检测到的模式
- 允许用户完善或添加更多

### 步骤 3: 生成规则文件

对每个确认的行为, 创建 `.claude/hookify.{rule-name}.local.md` 文件:

**规则命名规范:**
- 使用 kebab-case
- 要有描述性: `block-dangerous-rm`, `warn-console-log`, `require-tests-before-stop`
- 以动作动词开头: block, warn, prevent, require

**文件格式:**
```markdown
---
name: {rule-name}
enabled: true
event: {bash|file|stop|prompt|all}
pattern: {regex pattern}
action: {warn|block}
---

{规则触发时显示给 Claude 的消息}
```

**action 值:**
- `warn`: 显示消息但允许操作 (默认)
- `block`: 阻止操作或停止会话

**更复杂的规则 (多条件):**
```markdown
---
name: {rule-name}
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.env$
  - field: new_text
    operator: contains
    pattern: API_KEY
---

{警告消息}
```

### 步骤 4: 创建文件并确认

**重要**: 规则文件必须创建在当前工作目录的 `.claude/` 文件夹中, 而不是插件目录中.

使用当前工作目录 (Claude Code 启动位置) 作为基础路径.

1. 检查当前工作目录中是否存在 `.claude/` 目录
   - 如果不存在, 先创建: `mkdir -p .claude`

2. 使用 Write 工具创建每个 `.claude/hookify.{name}.local.md` 文件
   - 使用相对于当前工作目录的路径: `.claude/hookify.{name}.local.md`
   - 路径应解析到项目的 .claude 目录, 而不是插件的

3. 向用户展示创建的内容:
   ```
   已创建 3 条 hookify 规则:
   - .claude/hookify.dangerous-rm.local.md
   - .claude/hookify.console-log.local.md
   - .claude/hookify.sensitive-files.local.md

   这些规则将在以下情况触发:
   - dangerous-rm: 匹配 "rm -rf" 的 Bash 命令
   - console-log: 添加 console.log 语句的编辑操作
   - sensitive-files: 对 .env 或凭据文件的编辑
   ```

4. 通过列出文件来确认它们创建在正确位置

5. 告知用户: **"规则立即生效 - 无需重启!"**

   hookify hooks 已经加载, 会在下一次工具调用时读取你的新规则.

## 事件类型参考

- **bash**: 匹配 Bash 工具命令
- **file**: 匹配 Edit, Write, MultiEdit 工具
- **stop**: 匹配 Agent 想要停止时 (用于完成检查)
- **prompt**: 匹配用户提交提示时
- **all**: 匹配所有事件

## 模式编写技巧

**Bash 模式:**
- 匹配危险命令: `rm\s+-rf|chmod\s+777|dd\s+if=`
- 匹配特定工具: `npm\s+install\s+|pip\s+install`

**文件模式:**
- 匹配代码模式: `console\.log\(|eval\(|innerHTML\s*=`
- 匹配文件路径: `\.env$|\.git/|node_modules/`

**Stop 模式:**
- 检查缺失步骤: (检查会话记录或完成标准)

## 示例工作流

**用户说**: "/hookify 使用 rm -rf 前先问我"

**你的响应**:
1. 分析: 用户想要阻止 rm -rf 命令
2. 询问: "我应该阻止这个命令还是仅警告你?"
3. 用户选择: "仅警告"
4. 创建 `.claude/hookify.dangerous-rm.local.md`:
   ```markdown
   ---
   name: warn-dangerous-rm
   enabled: true
   event: bash
   pattern: rm\s+-rf
   ---

   **检测到危险的 rm 命令**

   你要求在使用 rm -rf 时收到警告.
   请确认路径是否正确.
   ```
5. 确认: "已创建 hookify 规则. 立即生效 - 试试触发它!"

## 重要说明

- **无需重启**: 规则在下一次工具调用时立即生效
- **文件位置**: 在项目的 `.claude/` 目录中创建文件 (当前工作目录), 而不是插件的 .claude/
- **正则语法**: 使用 Python 正则表达式语法 (YAML 中使用原始字符串, 无需转义)
- **操作类型**: 规则可以 `warn` (默认) 或 `block` 操作
- **测试**: 创建规则后立即测试

## 故障排除

**如果规则文件创建失败:**
1. 使用 pwd 检查当前工作目录
2. 确保 `.claude/` 目录存在 (如需要则用 mkdir 创建)
3. 必要时使用绝对路径: `{cwd}/.claude/hookify.{name}.local.md`
4. 用 Glob 或 ls 验证文件是否已创建

**如果规则创建后不触发:**
1. 确认文件在项目 `.claude/` 中而不是插件 `.claude/` 中
2. 用 Read 工具检查文件确保模式正确
3. 测试模式: `python3 -c "import re; print(re.search(r'pattern', 'test text'))"`
4. 确认 frontmatter 中 `enabled: true`
5. 注意: 规则立即生效, 无需重启

**如果阻止过于严格:**
1. 在规则文件中将 `action: block` 改为 `action: warn`
2. 或调整模式使其更具体
3. 更改在下一次工具调用时生效

使用 TodoWrite 跟踪你的步骤进度.
