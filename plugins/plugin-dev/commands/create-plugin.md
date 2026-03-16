---
description: 引导式端到端插件创建工作流, 包含组件设计, 实现和验证
argument-hint: 可选的插件描述
allowed-tools: ["Read", "Write", "Grep", "Glob", "Bash", "TodoWrite", "AskUserQuestion", "Skill", "Task"]
---

# 插件创建工作流

引导用户从初始概念到测试实现, 创建完整, 高质量的 Claude Code 插件. 遵循系统化方法: 理解需求, 设计组件, 澄清细节, 遵循最佳实践实现, 验证和测试.

## 核心原则

- **提出澄清问题**: 识别关于插件目的, 触发, 范围和组件的所有歧义. 提出具体, 明确的问题而不是做假设. 在继续实现之前等待用户回答.
- **加载相关技能**: 使用 Skill 工具在需要时加载 plugin-dev 技能 (plugin-structure, hook-development, agent-development 等)
- **使用专门的 agents**: 利用 agent-creator, plugin-validator 和 skill-reviewer agents 进行 AI 辅助开发
- **遵循最佳实践**: 应用 plugin-dev 自己实现中的模式
- **渐进式披露**: 创建带有 references/examples 的精简技能
- **使用 TodoWrite**: 在所有阶段跟踪所有进度

**初始请求:** $ARGUMENTS

---

## 阶段 1: 发现

**目标**: 理解需要构建什么插件以及它解决什么问题

**行动**:
1. 创建包含所有 7 个阶段的待办列表
2. 如果从参数中可以清楚插件目的:
   - 总结理解
   - 识别插件类型 (集成, 工作流, 分析, 工具包等)
3. 如果插件目的不清楚, 询问用户:
   - 这个插件解决什么问题?
   - 谁会使用它, 何时使用?
   - 它应该做什么?
   - 有没有类似的插件可以参考?
4. 总结理解并在继续之前与用户确认

**输出**: 清晰的插件目的和目标用户陈述

---

## 阶段 2: 组件规划

**目标**: 确定需要什么插件组件

**必须在此阶段前使用 Skill 工具加载 plugin-structure 技能**.

**行动**:
1. 加载 plugin-structure 技能以理解组件类型
2. 分析插件需求并确定所需组件:
   - **Skills**: 是否需要专业知识? (hooks API, MCP 模式等)
   - **Commands**: 用户发起的操作? (部署, 配置, 分析)
   - **Agents**: 自主任务? (验证, 生成, 分析)
   - **Hooks**: 事件驱动自动化? (验证, 通知)
   - **MCP**: 外部服务集成? (数据库, API)
   - **Settings**: 用户配置? (.local.md 文件)
3. 对于每种需要的组件类型, 识别:
   - 每种类型需要多少个
   - 每个做什么
   - 大致的触发/使用模式
4. 以表格形式向用户展示组件计划:
   ```
   | 组件类型 | 数量 | 用途 |
   |----------|------|------|
   | Skills   | 2    | Hook 模式, MCP 用法 |
   | Commands | 3    | 部署, 配置, 验证 |
   | Agents   | 1    | 自主验证 |
   | Hooks    | 0    | 不需要 |
   | MCP      | 1    | 数据库集成 |
   ```
5. 获得用户确认或调整

**输出**: 确认的要创建组件列表

---

## 阶段 3: 详细设计和澄清问题

**目标**: 详细指定每个组件并解决所有歧义

**关键**: 这是最重要的阶段之一. 不要跳过.

**行动**:
1. 对于计划中的每个组件, 识别未充分指定的方面:
   - **Skills**: 什么触发它们? 它们提供什么知识? 多详细?
   - **Commands**: 什么参数? 什么工具? 交互式还是自动化?
   - **Agents**: 何时触发 (主动/被动)? 什么工具? 输出格式?
   - **Hooks**: 哪些事件? 基于 prompt 还是命令? 验证标准?
   - **MCP**: 什么服务器类型? 认证? 哪些工具?
   - **Settings**: 什么字段? 必需还是可选? 默认值?

2. **以有组织的章节向用户展示所有问题** (每种组件类型一个章节)

3. **在继续实现之前等待回答**

4. 如果用户说 "你觉得最好的就行", 提供具体建议并获得明确确认

**技能的示例问题**:
- 什么特定的用户查询应该触发此技能?
- 它应该包含实用脚本吗? 什么功能?
- 核心 SKILL.md 应该多详细 vs references/?
- 有没有要包含的真实示例?

**Agent 的示例问题**:
- 此 agent 应该在某些操作后主动触发, 还是仅在明确请求时触发?
- 它需要什么工具 (Read, Write, Bash 等)?
- 输出格式应该是什么?
- 有没有要执行的特定质量标准?

**输出**: 每个组件的详细规范

---

## 阶段 4: 插件结构创建

**目标**: 创建插件目录结构和清单

**行动**:
1. 确定插件名称 (kebab-case, 描述性)
2. 选择插件位置:
   - 询问用户: "我应该在哪里创建插件?"
   - 提供选项: 当前目录, ../new-plugin-name, 自定义路径
3. 使用 bash 创建目录结构:
   ```bash
   mkdir -p plugin-name/.claude-plugin
   mkdir -p plugin-name/skills     # 如果需要
   mkdir -p plugin-name/commands   # 如果需要
   mkdir -p plugin-name/agents     # 如果需要
   mkdir -p plugin-name/hooks      # 如果需要
   ```
4. 使用 Write 工具创建 plugin.json 清单:
   ```json
   {
     "name": "plugin-name",
     "version": "0.1.0",
     "description": "[简要描述]",
     "author": {
       "name": "[来自用户或默认的作者]",
       "email": "[邮箱或默认]"
     }
   }
   ```
5. 创建 README.md 模板
6. 如果需要创建 .gitignore (用于 .claude/*.local.md 等)
7. 如果创建新目录则初始化 git 仓库

**输出**: 插件目录结构已创建并准备好组件

---

## 阶段 5: 组件实现

**目标**: 遵循最佳实践创建每个组件

**在实现每种组件类型前加载相关技能**:
- Skills: 加载 skill-development 技能
- Commands: 加载 command-development 技能
- Agents: 加载 agent-development 技能
- Hooks: 加载 hook-development 技能
- MCP: 加载 mcp-integration 技能
- Settings: 加载 plugin-settings 技能

**每种组件的行动**:

### 对于 Skills:
1. 使用 Skill 工具加载 skill-development 技能
2. 对于每个技能:
   - 向用户询问具体使用示例 (或使用阶段 3 中的)
   - 规划资源 (scripts/, references/, examples/)
   - 创建技能目录结构
   - 编写 SKILL.md, 包含:
     - 带有特定触发短语的第三人称描述
     - 命令式形式的精简正文 (1,500-2,000 字)
     - 对支持文件的引用
   - 为详细内容创建参考文件
   - 为工作代码创建示例文件
   - 如果需要创建实用脚本
3. 使用 skill-reviewer agent 验证每个技能

### 对于 Commands:
1. 使用 Skill 工具加载 command-development 技能
2. 对于每个命令:
   - 编写带有 frontmatter 的命令 markdown
   - 包含清晰的描述和 argument-hint
   - 指定 allowed-tools (最小必要)
   - 为 Claude 编写指令 (不是给用户的)
   - 提供使用示例和技巧
   - 如果适用引用相关技能

### 对于 Agents:
1. 使用 Skill 工具加载 agent-development 技能
2. 对于每个 agent, 使用 agent-creator agent:
   - 提供 agent 应该做什么的描述
   - Agent-creator 生成: identifier, whenToUse 带示例, systemPrompt
   - 创建带有 frontmatter 和 system prompt 的 agent markdown 文件
   - 添加适当的 model, color 和 tools
   - 使用 validate-agent.sh 脚本验证

### 对于 Hooks:
1. 使用 Skill 工具加载 hook-development 技能
2. 对于每个 hook:
   - 创建带有 hook 配置的 hooks/hooks.json
   - 对于复杂逻辑优先使用基于 prompt 的 hooks
   - 使用 ${CLAUDE_PLUGIN_ROOT} 以实现可移植性
   - 如果需要创建 hook 脚本 (在 examples/ 而不是 scripts/)
   - 使用 validate-hook-schema.sh 和 test-hook.sh 工具测试

### 对于 MCP:
1. 使用 Skill 工具加载 mcp-integration 技能
2. 创建 .mcp.json 配置, 包含:
   - 服务器类型 (本地用 stdio, 托管用 SSE)
   - 命令和参数 (带 ${CLAUDE_PLUGIN_ROOT})
   - 如果是 LSP 则需要 extensionToLanguage 映射
   - 按需的环境变量
3. 在 README 中记录必需的环境变量
4. 提供设置说明

### 对于 Settings:
1. 使用 Skill 工具加载 plugin-settings 技能
2. 在 README 中创建设置模板
3. 创建示例 .claude/plugin-name.local.md 文件 (作为文档)
4. 按需在 hooks/commands 中实现设置读取
5. 添加到 .gitignore: `.claude/*.local.md`

**进度跟踪**: 每完成一个组件更新待办事项

**输出**: 所有插件组件已实现

---

## 阶段 6: 验证和质量检查

**目标**: 确保插件符合质量标准并正常工作

**行动**:
1. **运行 plugin-validator agent**:
   - 使用 plugin-validator agent 全面验证插件
   - 检查: 清单, 结构, 命名, 组件, 安全
   - 审查验证报告

2. **修复严重问题**:
   - 解决验证中的任何严重错误
   - 修复任何表明实际问题的警告

3. **使用 skill-reviewer 审查** (如果插件有技能):
   - 对于每个技能, 使用 skill-reviewer agent
   - 检查描述质量, 渐进式披露, 写作风格
   - 应用建议

4. **测试 agent 触发** (如果插件有 agents):
   - 对于每个 agent, 验证 <example> 块是否清晰
   - 检查触发条件是否具体
   - 在 agent 文件上运行 validate-agent.sh

5. **测试 hook 配置** (如果插件有 hooks):
   - 在 hooks/hooks.json 上运行 validate-hook-schema.sh
   - 使用 test-hook.sh 测试 hook 脚本
   - 验证 ${CLAUDE_PLUGIN_ROOT} 的使用

6. **展示发现**:
   - 验证结果摘要
   - 任何剩余问题
   - 总体质量评估

7. **询问用户**: "验证完成. 发现的问题: [严重数量], [警告数量]. 你想让我现在修复它们, 还是继续测试?"

**输出**: 插件已验证并准备好测试

---

## 阶段 7: 测试和验证

**目标**: 测试插件在 Claude Code 中正常工作

**行动**:
1. **安装说明**:
   - 向用户展示如何本地测试:
     ```bash
     cc --plugin-dir /path/to/plugin-name
     ```
   - 或复制到 `.claude-plugin/` 进行项目测试

2. **用户执行的验证清单**:
   - [ ] 技能在触发时加载 (使用触发短语提问)
   - [ ] 命令出现在 `/help` 中并正确执行
   - [ ] Agents 在适当场景下触发
   - [ ] Hooks 在事件上激活 (如果适用)
   - [ ] MCP 服务器连接 (如果适用)
   - [ ] 设置文件工作 (如果适用)

3. **测试建议**:
   - 对于技能: 使用描述中的触发短语提问
   - 对于命令: 使用各种参数运行 `/plugin-name:command-name`
   - 对于 agents: 创建匹配 agent 示例的场景
   - 对于 hooks: 使用 `claude --debug` 查看 hook 执行
   - 对于 MCP: 使用 `/mcp` 验证服务器和工具

4. **询问用户**: "我已经准备好插件进行测试. 你想让我引导你测试每个组件, 还是想自己测试?"

5. **如果用户想要引导**, 使用具体测试用例逐步测试每个组件

**输出**: 插件已测试并验证工作

---

## 阶段 8: 文档和后续步骤

**目标**: 确保插件有良好的文档并准备好分发

**行动**:
1. **验证 README 完整性**:
   - 检查 README 有: 概述, 功能, 安装, 先决条件, 使用
   - 对于 MCP 插件: 记录必需的环境变量
   - 对于 hook 插件: 解释 hook 激活
   - 对于设置: 提供配置模板

2. **添加市场条目** (如果发布):
   - 向用户展示如何添加到 marketplace.json
   - 帮助起草市场描述
   - 建议类别和标签

3. **创建摘要**:
   - 标记所有待办事项完成
   - 列出创建的内容:
     - 插件名称和目的
     - 创建的组件 (X skills, Y commands, Z agents 等)
     - 关键文件及其用途
     - 总文件数和结构
   - 后续步骤:
     - 测试建议
     - 发布到市场 (如果需要)
     - 基于使用的迭代

4. **建议改进** (可选):
   - 可以增强插件的其他组件
   - 集成机会
   - 测试策略

**输出**: 完整, 有文档的插件准备好使用或发布

---

## 重要说明

### 在所有阶段中

- **使用 TodoWrite** 在每个阶段跟踪进度
- **使用 Skill 工具加载技能** 在处理特定组件类型时
- **使用专门的 agents** (agent-creator, plugin-validator, skill-reviewer)
- **在关键决策点请求用户确认**
- **遵循 plugin-dev 自己的模式** 作为参考示例
- **应用最佳实践**:
  - 技能使用第三人称描述
  - 技能正文使用命令式
  - 为 Claude 编写命令
  - 强触发短语
  - ${CLAUDE_PLUGIN_ROOT} 用于可移植性
  - 渐进式披露
  - 安全优先 (HTTPS, 无硬编码凭证)

### 关键决策点 (等待用户)

1. 阶段 1 后: 确认插件目的
2. 阶段 2 后: 批准组件计划
3. 阶段 3 后: 继续实现
4. 阶段 6 后: 修复问题或继续
5. 阶段 7 后: 继续文档

### 按阶段加载的技能

- **阶段 2**: plugin-structure
- **阶段 5**: skill-development, command-development, agent-development, hook-development, mcp-integration, plugin-settings (按需)
- **阶段 6**: (agents 将自动使用技能)

### 质量标准

每个组件必须符合这些标准:
- 遵循 plugin-dev 的成熟模式
- 使用正确的命名约定
- 有强触发条件 (skills/agents)
- 包含工作示例
- 有适当的文档
- 使用工具验证
- 在 Claude Code 中测试

---

## 示例工作流

### 用户请求
"创建一个管理数据库迁移的插件"

### 阶段 1: 发现
- 理解: 迁移管理, 数据库模式版本控制
- 确认: 用户想创建, 运行, 回滚迁移

### 阶段 2: 组件规划
- Skills: 1 (迁移最佳实践)
- Commands: 3 (create-migration, run-migrations, rollback)
- Agents: 1 (migration-validator)
- MCP: 1 (数据库连接)

### 阶段 3: 澄清问题
- 哪些数据库? (PostgreSQL, MySQL 等)
- 迁移文件格式? (SQL, 基于代码?)
- Agent 应该在应用前验证吗?
- 需要什么 MCP 工具? (query, execute, schema)

### 阶段 4-8: 实现, 验证, 测试, 文档

---

**从阶段 1 开始: 发现**
