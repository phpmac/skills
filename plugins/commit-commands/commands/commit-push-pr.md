---
allowed-tools: Bash(git checkout --branch:*), Bash(git add:*), Bash(git status:*), Bash(git push:*), Bash(git commit:*), Bash(gh pr create:*)
description: 提交, 推送并创建 PR
---

## 上下文

- 当前 git 状态: !`git status`
- 当前 git diff (暂存和未暂存变更): !`git diff HEAD`
- 当前分支: !`git branch --show-current`

## 任务

根据上述变更:

1. 如果在 main 上则创建新分支
2. 使用合适的信息创建单个提交
3. 推送分支到 origin
4. 使用 `gh pr create` 创建 PR
5. 您可以在单个响应中调用多个工具. 必须在单条消息中完成以上所有操作. 不要使用任何其他工具或执行其他操作. 除了工具调用外不要发送任何其他文本或消息.
