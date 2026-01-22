# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库概述

这是一个 Claude Skills 收集仓库，用于存储和分享可重用的技能定义。Skills 是 Claude 动态加载的指令集，用于在特定任务中提高性能。

## Claude Skills 系统

### 什么是 Skill

一个 **Skill** 是一个包含 `SKILL.md` 文件的文件夹，该文件使用 YAML frontmatter 和 Markdown 内容来定义：

- **name**: 技能的唯一标识符（仅使用字母、数字和连字符）
- **description**: 描述何时使用此技能（第三人称，以 "Use when..." 开头）
- **内容**: Claude 在激活此技能时遵循的指令、示例和指南

### 目录结构

```
skills/
  .claude-plugin/
    plugin.json         # 插件元数据（必需）
    marketplace.json    # 市场配置（可选，用于发布）
  skills/
    skill-name/
      SKILL.md          # 技能定义（必需）
      README.md         # 附加文档（可选）
      supporting-file.* # 参考资料或可重用工具（可选）
  commands/             # 斜杠命令（可选）
  hooks/                # 钩子脚本（可选）
  agents/               # 代理定义（可选）
```

### SKILL.md 格式

```markdown
---
name: skill-name-with-hyphens
description: Use when [具体的触发条件和症状]
---

# 技能标题

## 概述
简要说明这个技能是什么，核心原则是什么（1-2句话）

## 使用时机
- 列出症状和用例的要点
- 何时不使用

## 核心模式
针对技术/模式的具体内容

## 快速参考
表格或要点以方便扫描常见操作

## 实现
简单模式的内联代码
链接到重型参考或可重用工具的文件

## 常见错误
会出现什么问题 + 如何修复
```

### Frontmatter 字段要求

**必需字段:**
- `name`: 技能标识符（最大 64 字符，仅字母、数字、连字符）
- `description`: 触发条件描述（最大 1024 字符，第三人称，以 "Use when..." 开头）

**可选字段:**
- `version`: 语义版本号
- `license`: 许可信息

### plugin.json 格式

```json
{
  "name": "plugin-name",
  "description": "插件描述",
  "author": {
    "name": "作者名称",
    "email": "email@example.com"
  },
  "version": "1.0.0",
  "homepage": "https://...",
  "repository": "https://...",
  "license": "MIT",
  "keywords": ["tags"]
}
```

### marketplace.json 格式

```json
{
  "name": "marketplace-name",
  "description": "市场描述",
  "owner": {
    "name": "所有者名称",
    "email": "email@example.com"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "description": "插件描述",
      "version": "1.0.0",
      "source": "./",
      "author": {
        "name": "作者名称",
        "email": "email@example.com"
      }
    }
  ]
}
```

## 安装和使用

### 在 Claude Code 中安装

```bash
# 添加市场
/plugin marketplace add <username>/skills

# 安装插件
/plugin install <plugin-name>@<marketplace-name>
```

### 技能的调用

在 Claude Code 中，通过 `Skill` 工具调用技能。当技能适用于当前任务时，Claude 会自动加载并遵循其指令。

## 技能创建最佳实践

### 铁律

**NO SKILL WITHOUT A FAILING TEST FIRST**

创建技能必须遵循 TDD 原则：
1. **RED**: 在没有技能的情况下运行基线测试，记录失败行为
2. **GREEN**: 编写最小技能来解决这些具体问题
3. **REFACTOR**: 识别新的漏洞并添加明确的应对措施

### 技能类型

1. **技术类**: 具有步骤的具体方法（如 `condition-based-waiting`, `root-cause-tracing`）
2. **模式类**: 思考问题的方式（如 `flatten-with-flags`, `test-invariants`）
3. **参考类**: API 文档、语法指南、工具文档
4. **规则强制类**: 强制执行规则/要求（如 `test-driven-development`, `verification-before-completion`）

### Claude 搜索优化 (CSO)

为便于 Claude 发现和使用技能：

1. **丰富的描述字段**: 使用具体触发器、症状和情况，**不要**总结技能的工作流程
2. **关键词覆盖**: 错误消息、症状、同义词、工具名称
3. **描述性命名**: 使用主动语态，动词优先（如 `creating-skills` 而非 `skill-creation`）
4. **令牌效率**: 频繁加载的技能应简洁（<200 词），详细信息移至辅助文件

### 跨技能引用

使用技能名称配合显式要求标记：
- **REQUIRED SUB-SKILL**: `Use superpowers:test-driven-development`
- **REQUIRED BACKGROUND**: `You MUST understand superpowers:systematic-debugging`

避免使用 `@` 语法强制加载文件，这会消耗大量上下文。

## 参考资源

- [官方技能仓库](https://github.com/anthropics/skills)
- [Agent Skills 规范](https://agentskills.io)
- [Superpowers 技能库](https://github.com/obra/superpowers)
