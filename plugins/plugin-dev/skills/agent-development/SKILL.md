---
name: Agent 开发
description: 当用户要求 "create an agent", "add an agent", "write a subagent", "agent frontmatter", "when to use description", "agent examples", "agent tools", "agent colors", "autonomous agent", 或需要关于 agent 结构, system prompts, 触发条件或 Claude Code 插件 agent 开发最佳实践的指导时应使用此技能.
version: 0.1.0
---

# Claude Code 插件的 Agent 开发

## 概述

Agents 是独立处理复杂, 多步任务的自主子进程. 理解 agent 结构, 触发条件和 system prompt 设计可以创建强大的自主能力.

**关键概念:**
- Agents 用于自主工作, 命令用于用户发起的操作
- 带 YAML frontmatter 的 Markdown 文件格式
- 通过带示例的 description 字段触发
- System prompt 定义 agent 行为
- 模型和颜色自定义

## Agent 文件结构

### 完整格式

```markdown
---
name: agent-identifier
description: 当 [触发条件] 时使用此 agent. 示例:

<example>
Context: [情况描述]
user: "[用户请求]"
assistant: "[assistant 应如何响应并使用此 agent]"
<commentary>
[为什么应该触发此 agent]
</commentary>
</example>

<example>
[其他示例...]
</example>

model: inherit
color: blue
tools: ["Read", "Write", "Grep"]
---

你是 [agent 角色描述]...

**你的核心职责:**
1. [职责 1]
2. [职责 2]

**分析流程:**
[分步工作流]

**输出格式:**
[返回什么]
```

## Frontmatter 字段

### name (必需)

用于命名空间和调用的 agent 标识符.

**格式:** 仅小写, 数字, 连字符
**长度:** 3-50 字符
**模式:** 必须以字母数字开头和结尾

**好示例:**
- `code-reviewer`
- `test-generator`
- `api-docs-writer`
- `security-analyzer`

**坏示例:**
- `helper` (太通用)
- `-agent-` (以连字符开头/结尾)
- `my_agent` (不允许下划线)
- `ag` (太短, < 3 字符)

### description (必需)

定义 Claude 何时应该触发此 agent. **这是最关键的字段.**

**必须包含:**
1. 触发条件 ("Use this agent when...")
2. 多个展示用法的 `<example>` 块
3. 每个示例中的上下文, 用户请求和 assistant 响应
4. 解释 agent 为何触发的 `<commentary>`

**格式:**
```
当 [条件] 时使用此 agent. 示例:

<example>
Context: [场景描述]
user: "[用户说什么]"
assistant: "[Claude 应如何响应]"
<commentary>
[为什么此 agent 是合适的]
</commentary>
</example>

[更多示例...]
```

**最佳实践:**
- 包含 2-4 个具体示例
- 展示主动和被动触发
- 覆盖相同意图的不同表达方式
- 在评论中解释推理
- 具体说明何时不使用 agent

### model (必需)

agent 应该使用哪个模型.

**选项:**
- `inherit` - 使用与父级相同的模型 (推荐)
- `sonnet` - Claude Sonnet (平衡)
- `opus` - Claude Opus (最强大, 昂贵)
- `haiku` - Claude Haiku (快速, 便宜)

**建议:** 除非 agent 需要特定模型能力, 否则使用 `inherit`.

### color (必需)

UI 中 agent 的视觉标识符.

**选项:** `blue`, `cyan`, `green`, `yellow`, `magenta`, `red`

**指南:**
- 为同一插件中的不同 agent 选择不同的颜色
- 为类似的 agent 类型使用一致的颜色
- Blue/cyan: 分析, 审查
- Green: 成功导向的任务
- Yellow: 警告, 验证
- Red: 关键, 安全
- Magenta: 创意, 生成

### tools (可选)

将 agent 限制为特定工具.

**格式:** 工具名称数组

```yaml
tools: ["Read", "Write", "Grep", "Bash"]
```

**默认:** 如果省略, agent 有权访问所有工具

**最佳实践:** 将工具限制为所需的最小值 (最小权限原则)

**常见工具集:**
- 只读分析: `["Read", "Grep", "Glob"]`
- 代码生成: `["Read", "Write", "Grep"]`
- 测试: `["Read", "Bash", "Grep"]`
- 完全访问: 省略字段或使用 `["*"]`

## System Prompt 设计

markdown 正文成为 agent 的 system prompt. 用第二人称编写, 直接对 agent 说.

### 结构

**标准模板:**
```markdown
你是专门从事 [领域] 的 [角色].

**你的核心职责:**
1. [主要职责]
2. [次要职责]
3. [其他职责...]

**分析流程:**
1. [步骤一]
2. [步骤二]
3. [步骤三]
[...]

**质量标准:**
- [标准 1]
- [标准 2]

**输出格式:**
以此格式提供结果:
- [包含什么]
- [如何构建]

**边缘情况:**
处理这些情况:
- [边缘情况 1]: [如何处理]
- [边缘情况 2]: [如何处理]
```

### 最佳实践

**应该:**
- 用第二人称编写 ("You are...", "You will...")
- 对职责具体
- 提供分步流程
- 定义输出格式
- 包含质量标准
- 处理边缘情况
- 保持在 10,000 字符以内

**不应该:**
- 用第一人称编写 ("I am...", "I will...")
- 模糊或通用
- 省略流程步骤
- 输出格式未定义
- 跳过质量指导
- 忽略错误情况

## 创建 Agents

### 方法 1: AI 辅助生成

使用此提示模式 (从 Claude Code 提取):

```
基于此请求创建 agent 配置: "[你的描述]"

要求:
1. 提取核心意图和职责
2. 为领域设计专家角色
3. 创建全面的 system prompt, 包含:
   - 清晰的行为边界
   - 具体的方法论
   - 边缘情况处理
   - 输出格式
4. 创建标识符 (小写, 连字符, 3-50 字符)
5. 编写带触发条件的描述
6. 包含 2-3 个展示何时使用的 <example> 块

返回 JSON:
{
  "identifier": "agent-name",
  "whenToUse": "当...时使用此 agent. 示例: <example>...</example>",
  "systemPrompt": "你是..."
}
```

然后转换为带 frontmatter 的 agent 文件格式.

参见 `examples/agent-creation-prompt.md` 获取完整模板.

### 方法 2: 手动创建

1. 选择 agent 标识符 (3-50 字符, 小写, 连字符)
2. 编写带示例的描述
3. 选择模型 (通常 `inherit`)
4. 选择颜色以进行视觉识别
5. 定义工具 (如果限制访问)
6. 使用上述结构编写 system prompt
7. 保存为 `agents/agent-name.md`

## 验证规则

### 标识符验证

```
有效: code-reviewer, test-gen, api-analyzer-v2
无效: ag (太短), -start (以连字符开头), my_agent (下划线)
```

**规则:**
- 3-50 字符
- 仅小写字母, 数字, 连字符
- 必须以字母数字开头和结尾
- 无下划线, 空格或特殊字符

### 描述验证

**长度:** 10-5,000 字符
**必须包含:** 触发条件和示例
**最佳:** 200-1,000 字符, 带有 2-4 个示例

### System Prompt 验证

**长度:** 20-10,000 字符
**最佳:** 500-3,000 字符
**结构:** 清晰的职责, 流程, 输出格式

## Agent 组织

### 插件 Agents 目录

```
plugin-name/
└── agents/
    ├── analyzer.md
    ├── reviewer.md
    └── generator.md
```

`agents/` 中的所有 `.md` 文件自动发现.

### 命名空间

Agents 自动添加命名空间:
- 单个插件: `agent-name`
- 带子目录: `plugin:subdir:agent-name`

## 测试 Agents

### 测试触发

创建测试场景以验证 agent 正确触发:

1. 编写带特定触发示例的 agent
2. 在测试中使用与示例类似的措辞
3. 检查 Claude 是否加载 agent
4. 验证 agent 提供预期功能

### 测试 System Prompt

确保 system prompt 完整:

1. 给 agent 典型任务
2. 检查它是否遵循流程步骤
3. 验证输出格式正确
4. 测试 prompt 中提到的边缘情况
5. 确认达到质量标准

## 快速参考

### 最小 Agent

```markdown
---
name: simple-agent
description: 当...时使用此 agent. 示例: <example>...</example>
model: inherit
color: blue
---

你是 [做 X] 的 agent.

流程:
1. [步骤 1]
2. [步骤 2]

输出: [提供什么]
```

### Frontmatter 字段摘要

| 字段 | 必需 | 格式 | 示例 |
|------|------|------|------|
| name | 是 | lowercase-hyphens | code-reviewer |
| description | 是 | 文本 + 示例 | 当... <example>... |
| model | 是 | inherit/sonnet/opus/haiku | inherit |
| color | 是 | 颜色名称 | blue |
| tools | 否 | 工具名称数组 | ["Read", "Grep"] |

### 最佳实践

**应该:**
- 在描述中包含 2-4 个具体示例
- 编写特定的触发条件
- 除非有特定需求, 否则对模型使用 `inherit`
- 选择适当的工具 (最小权限)
- 编写清晰, 结构化的 system prompts
- 彻底测试 agent 触发

**不应该:**
- 使用没有示例的通用描述
- 省略触发条件
- 给所有 agent 相同的颜色
- 授予不必要的工具访问权限
- 编写模糊的 system prompts
- 跳过测试

## 附加资源

### 参考文件

有关详细指导, 请参阅:

- **`references/system-prompt-design.md`** - 完整的 system prompt 模式
- **`references/triggering-examples.md`** - 示例格式和最佳实践
- **`references/agent-creation-system-prompt.md`** - 来自 Claude Code 的确切提示

### 示例文件

`examples/` 中的工作示例:

- **`agent-creation-prompt.md`** - AI 辅助 agent 生成模板
- **`complete-agent-examples.md`** - 不同用例的完整 agent 示例

### 实用脚本

`scripts/` 中的开发工具:

- **`validate-agent.sh`** - 验证 agent 文件结构
- **`test-agent-trigger.sh`** - 测试 agent 是否正确触发

## 实现工作流

为插件创建 agent:

1. 定义 agent 目的和触发条件
2. 选择创建方法 (AI 辅助或手动)
3. 创建 `agents/agent-name.md` 文件
4. 使用所有必需字段编写 frontmatter
5. 按照最佳实践编写 system prompt
6. 在描述中包含 2-4 个触发示例
7. 使用 `scripts/validate-agent.sh` 验证
8. 用真实场景测试触发
9. 在插件 README 中记录 agent

专注于清晰的触发条件和全面的 system prompts 以实现自主操作.
