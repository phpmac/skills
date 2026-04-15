---
allowed-tools: Bash(git checkout --branch:*), Bash(git add:*), Bash(git status:*), Bash(git push:*), Bash(git commit:*), Bash(gh pr create:*)
description: 提交, 推送并创建 PR
---

## 规范

- 提交前检查暂存文件是否包含敏感文件(.env, auth.json, *.key, *.pem 等), 发现时主动警告用户并停止提交
- 内容使用中文, 标点符号必须使用英文标点

## 提交前逻辑检查

创建 commit 前, 必须按以下优先级顺序检查代码改动的逻辑正确性:

1. **对话内容** - 检查对话上下文中的需求/意图是否与代码改动一致
2. **注释** - 检查新增/修改的注释是否准确描述实际行为
3. **代码改动** - 检查 git diff 中的逻辑是否符合预期, 有无遗漏/误改/副作用

存在以下任一情况时, 必须使用 AskUserQuestion 与用户确认后再提交:
- 代码改动与对话需求存在偏差或遗漏
- 注释与实际代码行为不一致
- 发现了未在对话中提及的额外修改(如格式化/无关文件变动)
- 对改动的影响范围或正确性存疑

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
