---
description: 获取 hookify 插件的帮助信息
allowed-tools: ["Read"]
---

# Hookify 插件帮助

解释 hookify 插件的工作原理和使用方法.

## 概述

hookify 插件让创建自定义 hooks 变得简单, 可以防止不良行为. 你无需编辑 `hooks.json` 文件, 只需创建简单的 markdown 配置文件来定义要监控的模式.

## 工作原理

### 1. Hook 系统

hookify 安装了在以下事件上运行的通用 hooks:
- **PreToolUse**: 任何工具执行之前 (Bash, Edit, Write 等)
- **PostToolUse**: 工具执行之后
- **Stop**: 当 Claude 想要停止工作时
- **UserPromptSubmit**: 当用户提交提示时

这些 hooks 从 `.claude/hookify.*.local.md` 读取配置文件, 并检查是否有规则匹配当前操作.

### 2. 配置文件

用户在 `.claude/hookify.{rule-name}.local.md` 文件中创建规则:

```markdown
---
name: warn-dangerous-rm
enabled: true
event: bash
pattern: rm\s+-rf
---

**检测到危险的 rm 命令!**

此命令可能删除重要文件. 请验证路径.
```

**关键字段:**
- `name`: 规则的唯一标识
- `enabled`: true/false 启用/禁用
- `event`: bash, file, stop, prompt 或 all
- `pattern`: 要匹配的正则表达式

消息正文是规则触发时 Claude 看到的内容.

### 3. 创建规则

**方式 A: 使用 /hookify 命令**
```
/hookify 在生产文件中不要使用调试日志
```

这会分析你的请求并创建相应的规则文件.

**方式 B: 手动创建**
按上述格式创建 `.claude/hookify.my-rule.local.md`.

**方式 C: 分析对话**
```
/hookify
```

不带参数时, hookify 会分析最近的对话, 找出你想要阻止的行为.

## 可用命令

- **`/hookify`** - 从对话分析或明确指令创建 hooks
- **`/hookify:help`** - 显示本帮助 (你正在阅读的内容)
- **`/hookify:list`** - 列出所有已配置的 hooks
- **`/hookify:configure`** - 交互式启用/禁用已有 hooks

## 示例用例

**阻止危险命令:**
```markdown
---
name: block-chmod-777
enabled: true
event: bash
pattern: chmod\s+777
---

不要使用 chmod 777 - 这是安全风险. 请使用具体的权限设置.
```

**警告调试代码:**
```markdown
---
name: warn-debug-code
enabled: true
event: file
pattern: debugger;|print\(
---

检测到调试代码. 提交前请记得移除调试语句.
```

**停止前要求运行测试:**
```markdown
---
name: require-tests
enabled: true
event: stop
pattern: .*
---

你停止前运行测试了吗? 确保执行了 `npm test` 或等效的测试命令.
```

## 模式语法

使用 Python 正则表达式语法:
- `\s` - 空白字符
- `\.` - 字面点号
- `|` - 或
- `+` - 一个或多个
- `*` - 零个或多个
- `\d` - 数字
- `[abc]` - 字符类

**示例:**
- `rm\s+-rf` - 匹配 "rm -rf"
- `(eval|exec)\(` - 匹配 "eval(" 或 "exec("
- `\.env$` - 匹配以 .env 结尾的文件

## 重要说明

**无需重启**: hookify 规则 (`.local.md` 文件) 在下一次工具调用时立即生效. hookify hooks 已经加载, 会动态读取你的规则.

**阻止或警告**: 规则可以 `block` 操作 (阻止执行) 或 `warn` (显示消息但允许). 在规则的 frontmatter 中设置 `action: block` 或 `action: warn`.

**规则文件**: 将规则保存在 `.claude/hookify.*.local.md` - 它们应该被 git 忽略 (如需要可添加到 .gitignore).

**禁用规则**: 在 frontmatter 中设置 `enabled: false` 或删除文件.

## 故障排除

**Hook 未触发:**
- 检查规则文件是否在 `.claude/` 目录中
- 确认 frontmatter 中 `enabled: true`
- 确认模式是有效的正则表达式
- 测试模式: `python3 -c "import re; print(re.search('your_pattern', 'test_text'))"`
- 规则立即生效 - 无需重启

**导入错误:**
- 检查 Python 3 是否可用: `python3 --version`
- 确认 hookify 插件已正确安装

**模式不匹配:**
- 单独测试正则表达式
- 检查转义问题 (在 YAML 中使用未加引号的模式)
- 先尝试简单模式, 再逐步完善

## 入门指南

1. 创建你的第一条规则:
   ```
   /hookify 当我尝试使用 rm -rf 时警告我
   ```

2. 尝试触发它:
   - 让 Claude 运行 `rm -rf /tmp/test`
   - 你应该会看到警告

4. 通过编辑 `.claude/hookify.warn-rm.local.md` 完善规则

5. 随着遇到更多不良行为, 创建更多规则

更多示例请查看 `${CLAUDE_PLUGIN_ROOT}/examples/` 目录.
