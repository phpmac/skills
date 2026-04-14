---
name: git-commit-confirm
enabled: true
event: tool
action: block
conditions:
  - field: tool_name
    operator: equals
    value: Bash
  - field: command
    operator: regex_match
    pattern: git (add|commit|push|checkout|restore)
---

**Git 操作需确认**

检测到自动 Git 操作, 在用户明确要求前禁止执行.
等待用户确认后再执行.
