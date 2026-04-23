---
name: writing-rules
description: 当用户要求 "创建 hookify 规则", "编写 hook 规则", "配置 hookify", "添加 hookify 规则", 或需要 hookify 规则语法和模式指导时使用此技能.
version: 0.1.0
---

# 编写 Hookify 规则

## 概述

hookify 规则是带有 YAML frontmatter 的 markdown 文件, 定义要监控的模式以及匹配时显示的消息. 规则存储在 `.claude/hookify.{rule-name}.local.md` 文件中.

## 规则文件格式

### 基本结构

```markdown
---
name: rule-identifier
enabled: true
event: bash|file|stop|prompt|all
pattern: regex-pattern-here
---

规则触发时显示给 Claude 的消息.
可以包含 markdown 格式, 警告, 建议等.
```

### Frontmatter 字段

**name** (必填): 规则的唯一标识
- 使用 kebab-case: `warn-dangerous-rm`, `block-console-log`
- 要有描述性和动作导向
- 以动词开头: warn, prevent, block, require, check

**enabled** (必填): 布尔值, 启用/禁用
- `true`: 规则活跃
- `false`: 规则禁用 (不会触发)
- 可以切换而无需删除规则

**event** (必填): 触发的 hook 事件
- `bash`: Bash 工具命令
- `file`: Edit, Write, MultiEdit 工具
- `stop`: 当 Agent 想要停止时
- `prompt`: 当用户提交提示时
- `all`: 所有事件

**action** (可选): 规则匹配时的操作
- `warn`: 显示消息但允许操作 (默认)
- `block`: 阻止操作 (PreToolUse) 或停止会话 (Stop 事件)
- 如果省略, 默认为 `warn`

**pattern** (简单格式): 要匹配的正则表达式
- 用于简单的单条件规则
- 匹配命令 (bash) 或 new_text (file)
- Python 正则表达式语法

**示例:**
```yaml
event: bash
pattern: rm\s+-rf
```

### 高级格式 (多条件)

用于需要多个条件的复杂规则:

```markdown
---
name: warn-env-file-edits
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

你正在向 .env 文件添加 API 密钥. 确保此文件已加入 .gitignore!
```

**条件字段:**
- `field`: 要检查的字段
  - bash: `command`
  - file: `file_path`, `new_text`, `old_text`, `content`
- `operator`: 匹配方式
  - `regex_match`: 正则表达式匹配
  - `contains`: 子字符串检查
  - `equals`: 精确匹配
  - `not_contains`: 子字符串不得存在
  - `starts_with`: 前缀检查
  - `ends_with`: 后缀检查
- `pattern`: 要匹配的模式或字符串

**所有条件必须同时匹配, 规则才会触发.**

## 消息正文

frontmatter 之后的 markdown 内容是规则触发时显示给 Claude 的消息.

**好的消息:**
- 解释检测到了什么
- 解释为什么有问题
- 建议替代方案或最佳实践
- 使用格式化提高可读性 (粗体, 列表等)

**示例:**
```markdown
**检测到调试代码!**

你正在向生产代码添加调试语句.

**为什么这很重要:**
- 调试日志不应发布到生产环境
- 可能暴露敏感数据
- 影响浏览器性能

**替代方案:**
- 使用合适的日志库
- 提交前移除
- 使用条件调试构建
```

## 事件类型指南

### bash 事件

匹配 Bash 命令模式:

```markdown
---
event: bash
pattern: sudo\s+|rm\s+-rf|chmod\s+777
---

检测到危险命令!
```

**常用模式:**
- 危险命令: `rm\s+-rf`, `dd\s+if=`, `mkfs`
- 提权操作: `sudo\s+`, `su\s+`
- 权限问题: `chmod\s+777`, `chown\s+root`

### file 事件

匹配 Edit/Write/MultiEdit 操作:

```markdown
---
event: file
pattern: debugger;|print\(
---

检测到可能有问题的代码模式!
```

**匹配不同字段:**
```markdown
---
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.tsx?$
  - field: new_text
    operator: regex_match
    pattern: debugger;
---

TypeScript 文件中检测到调试器语句!
```

**常用模式:**
- 调试代码: `debugger`, `print\(`
- 安全风险: `innerHTML\s*=`, `dangerouslySetInnerHTML`
- 敏感文件: `\.env$`, `credentials`, `\.pem$`
- 生成文件: `node_modules/`, `dist/`, `build/`

### stop 事件

当 Agent 想要停止时匹配 (完成检查):

```markdown
---
event: stop
pattern: .*
---

停止前, 请验证:
- [ ] 已运行测试
- [ ] 构建成功
- [ ] 文档已更新
```

**用途:**
- 必要步骤的提醒
- 完成清单
- 流程强制执行

### prompt 事件

匹配用户提示内容 (高级):

```markdown
---
event: prompt
conditions:
  - field: user_prompt
    operator: contains
    pattern: deploy to production
---

生产部署清单:
- [ ] 测试是否通过?
- [ ] 是否已由团队审查?
- [ ] 监控是否就绪?
```

## 模式编写技巧

### 正则基础

**字面字符:** 大多数字符匹配自身
- `rm` 匹配 "rm"
- `debugger` 匹配 "debugger"

**特殊字符需要转义:**
- `.` (任意字符) -> `\.` (字面点号)
- `(` `)` -> `\(` `\)` (字面括号)
- `[` `]` -> `\[` `\]` (字面方括号)

**常用元字符:**
- `\s` - 空白字符 (空格, 制表符, 换行)
- `\d` - 数字 (0-9)
- `\w` - 单词字符 (a-z, A-Z, 0-9, _)
- `.` - 任意字符
- `+` - 一个或多个
- `*` - 零个或多个
- `?` - 零个或一个
- `|` - 或

**示例:**
```
rm\s+-rf         匹配: rm -rf, rm  -rf
debugger;        匹配: debugger;
chmod\s+777      匹配: chmod 777, chmod  777
API_KEY\s*=      匹配: API_KEY=, API_KEY =
```

### 测试模式

使用前先测试正则表达式:

```bash
python3 -c "import re; print(re.search(r'your_pattern', 'test text'))"
```

或使用在线正则测试工具 (regex101.com, 选择 Python 模式).

### 常见陷阱

**过于宽泛:**
```yaml
pattern: log    # 匹配 "log", "login", "dialog", "catalog"
```
更好: `debugger;|print\(`

**过于具体:**
```yaml
pattern: rm -rf /tmp  # 仅匹配精确路径
```
更好: `rm\s+-rf`

**转义问题:**
- YAML 加引号字符串: `"pattern"` 需要双反斜杠 `\\s`
- YAML 不加引号: `pattern: \s` 直接使用
- **建议**: 在 YAML 中使用不加引号的模式

## 文件组织

**位置:** 所有规则在 `.claude/` 目录
**命名:** `.claude/hookify.{描述性名称}.local.md`
**Gitignore:** 将 `.claude/*.local.md` 添加到 `.gitignore`

**好的命名:**
- `hookify.dangerous-rm.local.md`
- `hookify.console-log.local.md`
- `hookify.require-tests.local.md`
- `hookify.sensitive-files.local.md`

**不好的命名:**
- `hookify.rule1.local.md` (不够描述性)
- `hookify.md` (缺少 .local)
- `danger.local.md` (缺少 hookify 前缀)

## 工作流

### 创建规则

1. 识别不良行为
2. 确定涉及的工具 (Bash, Edit 等)
3. 选择事件类型 (bash, file, stop 等)
4. 编写正则表达式模式
5. 在项目根目录创建 `.claude/hookify.{name}.local.md` 文件
6. 立即测试 - 规则会在下一次工具调用时动态读取

### 完善规则

1. 编辑 `.local.md` 文件
2. 调整模式或消息
3. 立即测试 - 更改在下一次工具调用时生效

### 禁用规则

**临时:** 在 frontmatter 中设置 `enabled: false`
**永久:** 删除 `.local.md` 文件

## 示例

查看 `${CLAUDE_PLUGIN_ROOT}/examples/` 中的完整示例:
- `dangerous-rm.local.md` - 阻止危险的 rm 命令
- `console-log-warning.local.md` - 警告调试语句
- `sensitive-files-warning.local.md` - 警告编辑 .env 文件

## 快速参考

**最简规则:**
```markdown
---
name: my-rule
enabled: true
event: bash
pattern: dangerous_command
---

警告消息写在这里
```

**带条件的规则:**
```markdown
---
name: my-rule
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.ts$
  - field: new_text
    operator: contains
    pattern: any
---

警告消息
```

**事件类型:**
- `bash` - Bash 命令
- `file` - 文件编辑
- `stop` - 完成检查
- `prompt` - 用户输入
- `all` - 所有事件

**字段选项:**
- Bash: `command`
- File: `file_path`, `new_text`, `old_text`, `content`
- Prompt: `user_prompt`

**操作符:**
- `regex_match`, `contains`, `equals`, `not_contains`, `starts_with`, `ends_with`
