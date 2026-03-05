---
name: block-git-checkout-discard
enabled: true
event: bash
pattern: ^git\s+checkout\s+--\s+\.
action: block
---

**禁止 AI 执行 git checkout -- . 撤销所有更改**

此命令会撤销当前目录下所有未提交的代码更改, 风险极高:
- 所有未提交的工作将丢失
- 无法恢复已撤销的更改
- 可能导致大量工作成果丢失

**重要规则:**
- **AI 禁止执行此命令, 无例外**
- **如确需执行, 必须由用户自己在终端手动操作**
- Claude 不应代为执行此类危险操作

**安全替代方案:**
- 使用 `git stash` 暂存更改
- 使用 `git restore <file>` 撤销特定文件
- 使用 `git checkout -- <file>` 撤销指定文件
