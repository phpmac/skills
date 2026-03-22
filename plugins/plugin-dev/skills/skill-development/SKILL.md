---
name: skill-development
description: 当用户想 "create a skill", "add a skill to plugin", "write a new skill", "improve skill description", "organize skill content", 或需要关于技能结构, 渐进式披露或 Claude Code 插件技能开发最佳实践的指导时应使用此技能.
version: 0.1.0
---

# Claude Code 插件的技能开发

此技能提供创建有效的 Claude Code 插件技能的指导.

## 关于技能

技能是模块化, 自包含的包, 通过提供专业知识, 工作流和工具来扩展 Claude 的能力. 将它们视为特定领域或任务的"入职指南"——它们将 Claude 从通用 agent 转变为配备任何模型都无法完全拥有的程序性知识的专门 agent.

### 技能提供什么

1. 专门的工作流 - 特定领域的多步流程
2. 工具集成 - 使用特定文件格式或 API 的指令
3. 领域专业知识 - 公司特定知识, 模式, 业务逻辑
4. 捆绑资源 - 复杂和重复任务的脚本, 参考和资源

### 技能剖析

每个技能由必需的 SKILL.md 文件和可选的捆绑资源组成:

```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter 元数据 (必需)
│   │   ├── name: (必需)
│   │   └── description: (必需)
│   └── Markdown 指令 (必需)
└── 捆绑资源 (可选)
    ├── scripts/          - 可执行代码 (Python/Bash 等)
    ├── references/       - 按需加载到上下文中的文档
    └── assets/           - 输出中使用的文件 (模板, 图标, 字体等)
```

#### SKILL.md (必需)

**元数据质量:** YAML frontmatter 中的 `name` 和 `description` 决定 Claude 何时使用技能. 对技能做什么和何时使用要具体. 使用第三人称 (例如 "This skill should be used when..." 而不是 "Use this skill when...").

#### 捆绑资源 (可选)

##### Scripts (`scripts/`)

需要确定性可靠性或被重复重写的任务的可执行代码 (Python/Bash 等).

- **何时包含**: 当相同代码被重复重写或需要确定性可靠性时
- **示例**: 用于 PDF 旋转任务的 `scripts/rotate_pdf.py`
- **优点**: 节省 token, 确定性, 可以在不加载到上下文的情况下执行

##### References (`references/`)

按需加载到上下文中以指导 Claude 的流程和思考的文档和参考材料.

- **何时包含**: 用于 Claude 在工作时应该参考的文档
- **示例**: `references/finance.md` 用于财务模式, `references/mnda.md` 用于公司 NDA 模板
- **用例**: 数据库模式, API 文档, 领域知识, 公司政策, 详细工作流指南
- **优点**: 保持 SKILL.md 精简, 仅在 Claude 确定需要时加载

##### Assets (`assets/`)

不打算加载到上下文中, 而是在 Claude 生成的输出中使用的文件.

- **何时包含**: 当技能需要将在最终输出中使用的文件时
- **示例**: `assets/logo.png` 用于品牌资源, `assets/slides.pptx` 用于 PowerPoint 模板
- **用例**: 模板, 图像, 图标, 样板代码, 字体, 被复制或修改的示例文档

### 渐进式披露设计原则

技能使用三级加载系统来有效管理上下文:

1. **元数据 (name + description)** - 始终在上下文中 (~100 字)
2. **SKILL.md 正文** - 技能触发时 (<5k 字)
3. **捆绑资源** - Claude 按需 (无限制*)

*无限制是因为脚本可以在不读取到上下文窗口的情况下执行.

## 技能创建流程

要创建技能, 按顺序遵循"技能创建流程", 仅在有明确理由不适用时才跳过步骤.

### 步骤 1: 用具体示例理解技能

仅当技能的使用模式已经清楚理解时才跳过此步骤.

要创建有效的技能, 清楚理解技能将如何使用的具体示例. 这种理解可以来自直接的用户示例或经用户反馈验证的生成示例.

例如, 在构建图像编辑器技能时, 相关问题包括:

- "图像编辑器技能应该支持什么功能? 编辑, 旋转, 还有其他吗?"
- "你能给一些这个技能如何使用的示例吗?"
- "我可以想象用户会要求 '从此图像中去除红眼' 或 '旋转此图像'. 你还能想象其他使用此技能的方式吗?"
- "用户会说什么来触发此技能?"

为了避免让用户不知所措, 避免在一条消息中问太多问题. 从最重要的问题开始, 根据需要进行跟进以提高效果.

当清楚了解技能应支持的功能时, 结束此步骤.

### 步骤 2: 规划可重用的技能内容

要将具体示例转化为有效的技能, 分析每个示例:

1. 考虑如何从头开始执行示例
2. 识别在重复执行这些工作流时什么脚本, 参考和资源会有帮助

**对于 Claude Code 插件:** 在构建 hooks 技能时, 分析显示:
1. 开发人员反复需要验证 hooks.json 和测试 hook 脚本
2. `scripts/validate-hook-schema.sh` 和 `scripts/test-hook.sh` 工具会有帮助
3. 用于详细 hook 模式的 `references/patterns.md` 以避免膨胀 SKILL.md

要建立技能的内容, 分析每个具体示例以创建要包含的可重用资源列表: 脚本, 参考和资源.

### 步骤 3: 创建技能结构

对于 Claude Code 插件, 创建技能目录结构:

```bash
mkdir -p plugin-name/skills/skill-name/{references,examples,scripts}
touch plugin-name/skills/skill-name/SKILL.md
```

### 步骤 4: 编辑技能

编辑技能时, 记住技能是为另一个 Claude 实例使用而创建的. 专注于包含对 Claude 有益且非显而易见的信息. 考虑什么程序性知识, 领域特定细节或可重用资源会帮助另一个 Claude 实例更有效地执行这些任务.

#### 从可重用技能内容开始

要开始实现, 从上面识别的可重用资源开始: `scripts/`, `references/` 和 `assets/` 文件. 注意此步骤可能需要用户输入.

同时, 删除技能不需要的任何示例文件和目录. 仅创建实际需要的目录 (references/, examples/, scripts/).

#### 更新 SKILL.md

**写作风格:** 使用**命令式/不定式形式** (动词优先的指令) 编写整个技能, 而不是第二人称. 使用客观的, 指令性的语言 (例如, "To accomplish X, do Y" 而不是 "You should do X").

**描述 (Frontmatter):** 使用带特定触发短语的第三人称格式:

```yaml
---
name: 技能名称
description: 当用户要求 "specific phrase 1", "specific phrase 2", "specific phrase 3" 时应使用此技能. 包含用户会说的应该触发此技能的确切短语. 要具体和明确.
version: 0.1.0
---
```

**保持 SKILL.md 精简:** 正文目标 1,500-2,000 字. 将详细内容移到 references/:
- 详细模式 -> `references/patterns.md`
- 高级技术 -> `references/advanced.md`
- 迁移指南 -> `references/migration.md`

**在 SKILL.md 中引用资源:**
```markdown
## 附加资源

### 参考文件

有关详细模式和技术, 请参阅:
- **`references/patterns.md`** - 常见模式
- **`references/advanced.md`** - 高级用例

### 示例文件

`examples/` 中的工作示例:
- **`example-script.sh`** - 工作示例
```

### 步骤 5: 验证和测试

**对于插件技能, 验证与通用技能不同:**

1. **检查结构**: 技能目录在 `plugin-name/skills/skill-name/`
2. **验证 SKILL.md**: 有带 name 和 description 的 frontmatter
3. **检查触发短语**: 描述包含特定用户查询
4. **验证写作风格**: 正文使用命令式/不定式形式, 不是第二人称
5. **测试渐进式披露**: SKILL.md 精简 (~1,500-2,000 字), 详细内容在 references/
6. **检查引用**: 所有引用的文件存在
7. **验证示例**: 示例完整且正确
8. **测试脚本**: 脚本可执行且工作正常

**使用 skill-reviewer agent:**
```
询问: "审查我的技能并检查它是否遵循最佳实践"
```

skill-reviewer agent 将检查描述质量, 内容组织和渐进式披露.

### 步骤 6: 迭代

测试技能后, 用户可能会请求改进. 这通常发生在使用技能后立即, 伴随着技能如何表现的新鲜上下文.

**迭代工作流:**
1. 在真实任务上使用技能
2. 注意困难或低效
3. 识别如何更新 SKILL.md 或捆绑资源
4. 实施更改并再次测试

## 渐进式披露实践

### SKILL.md 中放什么

**包含 (技能触发时始终加载):**
- 核心概念和概述
- 基本流程和工作流
- 快速参考表
- 指向 references/examples/scripts 的指针
- 最常见的用例

**保持在 3,000 字以下, 理想为 1,500-2,000 字**

### references/ 中放什么

**移到 references/ (按需加载):**
- 详细模式和高级技术
- 全面的 API 文档
- 迁移指南
- 边缘情况和故障排除
- 详细的示例和演练

**每个参考文件可以很大 (2,000-5,000+ 字)**

### examples/ 中放什么

**工作代码示例:**
- 完整, 可运行的脚本
- 配置文件
- 模板文件
- 真实世界的使用示例

**用户可以直接复制和改编这些**

### scripts/ 中放什么

**实用脚本:**
- 验证工具
- 测试助手
- 解析工具
- 自动化脚本

**应该是可执行且有文档的**

## 写作风格要求

### 命令式/不定式形式

使用动词优先的指令编写, 而不是第二人称:

**正确 (命令式):**
```
要创建 hook, 定义事件类型.
配置 MCP 服务器的认证.
使用前验证设置.
```

**错误 (第二人称):**
```
你应该通过定义事件类型来创建 hook.
你需要配置 MCP 服务器.
使用前你必须验证设置.
```

### 描述中使用第三人称

frontmatter 描述必须使用第三人称:

**正确:**
```yaml
description: 当用户要求 "create X", "configure Y"... 时应使用此技能
```

**错误:**
```yaml
description: 当你想创建 X 时使用此技能...
description: 当用户询问时加载此技能...
```

## 验证清单

在完成技能前:

**结构:**
- [ ] SKILL.md 文件存在且具有有效的 YAML frontmatter
- [ ] Frontmatter 有 `name` 和 `description` 字段
- [ ] Markdown 正文存在且充实
- [ ] 引用的文件实际存在

**描述质量:**
- [ ] 使用第三人称 ("This skill should be used when...")
- [ ] 包含用户会说的特定触发短语
- [ ] 列出具体场景 ("create X", "configure Y")
- [ ] 不模糊或通用

**内容质量:**
- [ ] SKILL.md 正文使用命令式/不定式形式
- [ ] 正文专注且精简 (理想 1,500-2,000 字, 最大 <5k)
- [ ] 详细内容移到 references/
- [ ] 示例完整且可工作
- [ ] 脚本可执行且有文档

## 要避免的常见错误

### 错误 1: 弱触发描述

**坏:**
```yaml
description: 提供使用 hooks 的指导.
```

**好:**
```yaml
description: 当用户要求 "create a hook", "add a PreToolUse hook", "validate tool use", 或提到 hook 事件时应使用此技能. 提供全面的 hooks API 指导.
```

### 错误 2: SKILL.md 中太多内容

**坏:**
```
skill-name/
└── SKILL.md  (8,000 字 - 所有内容在一个文件中)
```

**好:**
```
skill-name/
├── SKILL.md  (1,800 字 - 核心要点)
└── references/
    ├── patterns.md (2,500 字)
    └── advanced.md (3,700 字)
```

### 错误 3: 第二人称写作

**坏:**
```markdown
你应该从读取配置文件开始.
你需要验证输入.
你可以使用 grep 工具搜索.
```

**好:**
```markdown
从读取配置文件开始.
处理前验证输入.
使用 grep 工具搜索模式.
```

## 实现工作流

为插件创建技能:

1. **理解用例**: 识别技能使用的具体示例
2. **规划资源**: 确定需要什么脚本/参考/示例
3. **创建结构**: `mkdir -p skills/skill-name/{references,examples,scripts}`
4. **编写 SKILL.md**:
   - 带第三人称描述和触发短语的 Frontmatter
   - 命令式形式的精简正文 (1,500-2,000 字)
   - 引用支持文件
5. **添加资源**: 按需创建 references/, examples/, scripts/
6. **验证**: 检查描述, 写作风格, 组织
7. **测试**: 验证技能在预期触发时加载
8. **迭代**: 基于使用进行改进

专注于强触发描述, 渐进式披露和命令式写作风格, 以创建在需要时加载并提供针对性指导的有效技能.
