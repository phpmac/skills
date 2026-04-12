---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
description: 创建 git commit
---

## 规范

- 提交前检查暂存文件是否包含敏感文件(.env, auth.json, *.key, *.pem 等), 发现时主动警告用户并停止提交
- 内容使用中文, 标点符号必须使用英文标点

## 上下文

- 当前 git 状态: !`git status`
- 当前 git diff (暂存和未暂存变更): !`git diff HEAD`
- 当前分支: !`git branch --show-current`
- 最近提交: !`git log --oneline -10`

## 任务

根据上述变更, 创建单个 git commit.

**提交信息规范:**
- 遵循约定式提交实践, 优先使用中文前缀: 更新(修改)/修复(bug)/添加(新功能)/文档(变更)/重构(代码)/优化(性能)/测试(用例)

您可以在单个响应中调用多个工具. 使用单条消息暂存并创建提交. 不要使用任何其他工具或执行其他操作. 除了工具调用外不要发送任何其他文本或消息.
