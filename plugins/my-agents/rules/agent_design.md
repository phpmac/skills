---
paths: ["plugins/*/agents/**"]
---

# Agent 设计规范

## 专家化原则

- 每个 agent 只负责一个领域, 不做通用 agent
- agent 设计时定义明确的 domain boundary, 防止跨域能力退化
- 多 agent 协作通过 orchestrator 分发, 不做端到端全能 agent

## Agent 编写规范

- 禁止写操作手册式流程(按步骤执行...), 应写决策指南(什么情况做什么判断)
- 必须定义: 触发条件 / 能力范围 / 边界外行为 / 输出格式
- 引用父级规则而非重复内容, 防止规则多源不一致

## 反模式

- 禁止: agent prompt 中硬编码具体命令/路径
- 禁止: 一个 agent 覆盖 3 个以上领域
- 禁止: 跳过工具预检直接启动 agent
