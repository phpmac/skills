---
description: 清理所有标记为 [gone] 的 git 分支 (已从远程删除但仍存在于本地的分支), 包括删除关联的 worktree.
---

## 规范

- 内容使用中文, 标点符号必须使用英文标点

## 任务

您需要执行以下 bash 命令来清理已从远程仓库删除的过时本地分支.

## 要执行的命令

1. **首先, 列出分支以识别任何 [gone] 状态**
   执行此命令:
   ```bash
   git branch -v
   ```

   注意: 带有 '+' 前缀的分支有关联的 worktree, 必须在删除前删除其 worktree.

2. **接下来, 识别需要为 [gone] 分支删除的 worktree**
   执行此命令:
   ```bash
   git worktree list
   ```

3. **最后, 删除 worktree 并删除 [gone] 分支 (同时处理普通分支和 worktree 分支)**
   执行此命令:
   ```bash
   # 处理所有 [gone] 分支, 如有则删除 '+' 前缀
   git branch -v | grep '\[gone\]' | sed 's/^[+* ]//' | awk '{print $1}' | while read branch; do
     echo "处理分支: $branch"
     # 查找并删除 worktree (如存在)
     worktree=$(git worktree list | grep "\\[$branch\\]" | awk '{print $1}')
     if [ ! -z "$worktree" ] && [ "$worktree" != "$(git rev-parse --show-toplevel)" ]; then
       echo "  删除 worktree: $worktree"
       git worktree remove --force "$worktree"
     fi
     # 删除分支
     echo "  删除分支: $branch"
     git branch -D "$branch"
   done
   ```

## 预期行为

执行这些命令后, 您将:

- 查看所有本地分支及其状态列表
- 识别并删除与 [gone] 分支关联的任何 worktree
- 删除所有标记为 [gone] 的分支
- 提供关于删除了哪些 worktree 和分支的反馈

如果没有分支标记为 [gone], 报告无需清理.
