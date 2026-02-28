---
allowed-tools: Bash(gh issue view:*), Bash(gh search:*), Bash(gh issue list:*), Bash(gh pr comment:*), Bash(gh pr diff:*), Bash(gh pr view:*), Bash(gh pr list:*), mcp__github_inline_comment__create_inline_comment
description: Code review a pull request
---

为给定的 PR 提供代码审查.

**Agent 假设 (适用于所有 Agent 和子 Agent):**
- 所有工具都正常工作, 不会出错. 不要测试工具或进行探索性调用. 确保每个启动的子 Agent 都清楚这一点.
- 只在完成任务需要时才调用工具. 每个工具调用都应有明确目的.

按以下步骤精确执行:

1. 启动一个 haiku agent 检查是否存在以下情况:
   - PR 已关闭
   - PR 是草稿
   - PR 不需要代码审查 (例如自动化 PR, 明显正确的琐碎变更)
   - Claude 已经在此 PR 上评论过 (检查 `gh pr view <PR> --comments` 中 claude 留下的评论)

   如果任一条件为真, 停止并不继续.

注意: 仍然审查 Claude 生成的 PR.

2. 启动一个 haiku agent 返回所有相关 CLAUDE.md 文件的路径列表 (不是内容), 包括:
   - 根 CLAUDE.md 文件 (如果存在)
   - PR 修改的文件所在目录中的任何 CLAUDE.md 文件

3. 启动一个 sonnet agent 查看 PR 并返回变更摘要

4. 并行启动 4 个 agent 独立审查变更. 每个 agent 应返回问题列表, 每个问题包括描述和标记原因 (例如 "CLAUDE.md adherence", "bug"). Agent 应执行以下操作:

   Agent 1 + 2: CLAUDE.md 合规性 sonnet agent
   并行审计 CLAUDE.md 合规性. 注意: 评估文件的 CLAUDE.md 合规性时, 只应考虑与该文件共享路径或父路径的 CLAUDE.md 文件.

   Agent 3: Opus bug agent (与 agent 4 并行子 agent)
   扫描明显的 bug. 只关注 diff 本身, 不阅读额外上下文. 只标记重要的 bug; 忽略挑剔和可能的误报. 不要标记无法在 git diff 上下文之外验证的问题.

   Agent 4: Opus bug agent (与 agent 3 并行子 agent)
   寻找引入代码中存在的问题. 这可能是安全问题, 逻辑错误等. 只查找变更代码范围内的问题.

   **关键: 我们只需要高信号问题.** 标记以下问题:
   - 代码无法编译或解析 (语法错误, 类型错误, 缺少导入, 未解析的引用)
   - 无论输入如何代码都会产生错误结果 (明显的逻辑错误)
   - 明确, 无歧义的 CLAUDE.md 违规, 可以引用被违反的确切规则

   不要标记:
   - 代码风格或质量问题
   - 依赖特定输入或状态的潜在问题
   - 主观建议或改进

   如果不确定问题是否真实, 不要标记. 误报会削弱信任并浪费审查者时间.

   此外, 应告知每个子 Agent PR 标题和描述. 这将帮助提供关于作者意图的上下文.

5. 对于步骤 4 中 agent 3 和 4 发现的每个问题, 启动并行子 agent 验证问题. 这些子 agent 应获取 PR 标题和描述以及问题描述. agent 的工作是审查问题以高置信度验证所述问题确实是问题. 例如, 如果标记了 "变量未定义" 这样的问题, 子 agent 的工作是验证这在代码中确实是真的. 另一个例子是 CLAUDE.md 问题. agent 应验证被违反的 CLAUDE.md 规则适用于此文件并且确实被违反. 对 bug 和逻辑问题使用 Opus 子 agent, 对 CLAUDE.md 违规使用 sonnet agent.

6. 过滤掉步骤 5 中未验证的任何问题. 此步骤将给出我们审查的高信号问题列表.

7. 将审查发现摘要输出到终端:
   - 如果发现问题, 列出每个问题及简要描述.
   - 如果未发现问题, 说明: "No issues found. Checked for bugs and CLAUDE.md compliance."

   如果未提供 `--comment` 参数, 在此停止. 不要发布任何 GitHub 评论.

   如果提供了 `--comment` 参数且未发现问题, 使用 `gh pr comment` 发布摘要评论并停止.

   如果提供了 `--comment` 参数且发现问题, 继续步骤 8.

8. 创建计划发布的所有评论列表. 这只是为了让您确保对评论感到满意. 不要在任何地方发布此列表.

9. 使用 `mcp__github_inline_comment__create_inline_comment` 为每个问题发布内联评论. 对于每条评论:
   - 提供问题的简要描述
   - 对于小型, 自包含的修复, 包含可提交的建议块
   - 对于较大的修复 (6+ 行, 结构性变更, 或跨多个位置的变更), 描述问题和建议的修复, 不使用建议块
   - 除非提交建议能完全修复问题, 否则永远不要发布可提交的建议. 如果需要后续步骤, 不要留下可提交的建议.

   **重要: 每个唯一问题只发布一条评论. 不要发布重复评论.**

在步骤 4 和 5 中评估问题时使用此列表 (这些是误报, 不要标记):

- 预先存在的问题
- 看起来是 bug 但实际上是正确的
- 高级工程师不会标记的学究式挑剔
- Linter 会捕获的问题 (不要运行 linter 验证)
- 一般代码质量问题 (例如, 缺乏测试覆盖, 一般安全问题), 除非 CLAUDE.md 中明确要求
- CLAUDE.md 中提到但在代码中明确静默的问题 (例如, 通过 lint ignore 注释)

注意:

- 使用 gh CLI 与 GitHub 交互 (例如, 获取 PR, 创建评论). 不要使用 web fetch.
- 开始前创建 todo 列表.
- 必须在内联评论中引用并链接每个问题 (例如, 如果引用 CLAUDE.md, 包含指向它的链接).
- 如果未发现问题且提供了 `--comment` 参数, 使用以下格式发布评论:

---

## Code review

No issues found. Checked for bugs and CLAUDE.md compliance.

---

- 在内联评论中链接代码时, 严格遵循以下格式, 否则 Markdown 预览无法正确渲染.
  - 需要完整 git sha
  - 必须提供完整 sha. 诸如 `https://github.com/owner/repo/blob/$(git rev-parse HEAD)/foo/bar` 的命令将不起作用, 因为您的评论将直接在 Markdown 中渲染.
  - 仓库名必须与您正在代码审查的仓库匹配
  - 文件名后的 # 符号
  - 行范围格式为 L[start]-L[end]
  - 在您要评论的行前后至少提供 1 行上下文 (例如, 如果您评论第 5-6 行, 应链接到 `L4-7`)
