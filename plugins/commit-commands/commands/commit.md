---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
description: 创建 git commit
---

## 上下文

- 当前 git 状态: !`git status`
- 当前 git diff (暂存和未暂存变更): !`git diff HEAD`
- 当前分支: !`git branch --show-current`
- 最近提交: !`git log --oneline -10`

## 任务

根据上述变更, 创建单个 git commit.

您可以在单个响应中调用多个工具. 使用单条消息暂存并创建提交. 不要使用任何其他工具或执行其他操作. 除了工具调用外不要发送任何其他文本或消息.
