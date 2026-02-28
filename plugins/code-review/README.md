# Code Review 插件

使用多个专业 Agent 并行审计 PR 变更, 通过置信度评分过滤误报, 实现自动化代码审查.

## 概述

Code Review 插件通过启动多个并行的 Agent 从不同角度独立审计变更, 实现自动化 PR 审查. 使用置信度评分过滤误报, 确保只输出高质量, 可操作的反馈.

## 命令

### `/code-review`

使用多个专业 Agent 对 PR 执行自动化代码审查.

**功能:**
1. 检查是否需要审查 (跳过已关闭, 草稿, 琐碎或已审查的 PR)
2. 收集仓库中相关的 CLAUDE.md 规则文件
3. 汇总 PR 变更内容
4. 启动 4 个并行 Agent 独立审查:
   - **Agent #1 & #2**: 审计 CLAUDE.md 合规性
   - **Agent #3**: 扫描变更中的明显 bug
   - **Agent #4**: 分析 git blame/历史以发现上下文相关问题
5. 对每个问题进行 0-100 置信度评分
6. 过滤置信度低于 80 的问题
7. 输出审查结果 (默认输出到终端, 使用 `--comment` 参数可发布为 PR 评论)

**用法:**
```bash
/code-review [--comment]
```

**参数:**
- `--comment`: 将审查结果作为评论发布到 PR (默认: 仅输出到终端)

**示例工作流:**
```bash
# 在 PR 分支上本地运行 (输出到终端):
/code-review

# 将审查结果发布为 PR 评论:
/code-review --comment

# Claude 将会:
# - 并行启动 4 个审查 Agent
# - 对每个问题进行置信度评分
# - 输出置信度 >=80 的问题 (根据参数输出到终端或 PR)
# - 如果没有高置信度问题则跳过
```

**特性:**
- 多个独立 Agent 实现全面审查
- 基于置信度的评分减少误报 (阈值: 80)
- CLAUDE.md 合规性检查, 显式验证规则
- 专注于变更的 bug 检测 (非预先存在的问题)
- 通过 git blame 分析历史上下文
- 自动跳过已关闭, 草稿或已审查的 PR
- 使用完整 SHA 和行范围直接链接到代码

**审查评论格式:**
```markdown
## Code review

Found 3 issues:

1. Missing error handling for OAuth callback (CLAUDE.md says "Always handle OAuth errors")

https://github.com/owner/repo/blob/abc123.../src/auth.ts#L67-L72

2. Memory leak: OAuth state not cleaned up (bug due to missing cleanup in finally block)

https://github.com/owner/repo/blob/abc123.../src/auth.ts#L88-L95

3. Inconsistent naming pattern (src/conventions/CLAUDE.md says "Use camelCase for functions")

https://github.com/owner/repo/blob/abc123.../src/utils.ts#L23-L28
```

**置信度评分:**
- **0**: 不确定, 误报
- **25**: 有点确定, 可能是真的
- **50**: 中等确定, 真实但次要
- **75**: 高度确定, 真实且重要
- **100**: 绝对确定, 肯定是真的

**过滤的误报类型:**
- 非 PR 引入的预先存在问题
- 看起来像 bug 但实际不是的代码
- 挑剔的吹毛求疵
- Linter 会捕获的问题
- 一般质量问题 (除非在 CLAUDE.md 中规定)
- 带有 lint ignore 注释的问题

## 安装

此插件包含在 Claude Code 仓库中. 使用 Claude Code 时命令自动可用.

## 最佳实践

### 使用 `/code-review`
- 维护清晰的 CLAUDE.md 文件以获得更好的合规性检查
- 信任 80+ 的置信度阈值 - 误报已被过滤
- 对所有非琐碎的 PR 运行
- 将 Agent 发现作为人工审查的起点
- 根据反复出现的审查模式更新 CLAUDE.md

### 何时使用
- 所有有意义变更的 PR
- 涉及关键代码路径的 PR
- 多个贡献者的 PR
- 规则合规性重要的 PR

### 何时不使用
- 已关闭或草稿 PR (会自动跳过)
- 琐碎的自动化 PR (会自动跳过)
- 需要立即合并的紧急热修复
- 已审查的 PR (会自动跳过)

## 工作流集成

### 标准 PR 审查工作流:
```bash
# 创建带变更的 PR
# 运行本地审查 (输出到终端)
/code-review

# 查看自动化反馈
# 进行必要的修复

# 可选: 发布为 PR 评论
/code-review --comment

# 准备好后合并
```

### 作为 CI/CD 的一部分:
```bash
# 在 PR 创建或更新时触发
# 使用 --comment 参数发布审查评论
/code-review --comment
# 如果审查已存在则跳过
```

## 要求

- 具有 GitHub 集成的 Git 仓库
- GitHub CLI (`gh`) 已安装并认证
- CLAUDE.md 文件 (可选但推荐用于规则检查)

## 故障排除

### 审查耗时过长

**问题**: Agent 在大型 PR 上运行缓慢

**解决方案**:
- 大量变更时正常现象 - Agent 并行运行
- 4 个独立 Agent 确保彻底性
- 考虑将大型 PR 拆分为较小的 PR

### 误报过多

**问题**: 审查标记了不真实的问题

**解决方案**:
- 默认阈值为 80 (已过滤大多数误报)
- 让 CLAUDE.md 更具体地说明什么重要
- 考虑标记的问题是否实际有效

### 未发布审查评论

**问题**: `/code-review` 运行了但没有评论出现

**解决方案**:
检查以下情况:
- PR 已关闭 (审查被跳过)
- PR 是草稿 (审查被跳过)
- PR 是琐碎/自动化的 (审查被跳过)
- PR 已有审查 (审查被跳过)
- 没有问题得分 >=80 (无需评论)

### 链接格式错误

**问题**: 代码链接在 GitHub 中无法正确渲染

**解决方案**:
链接必须遵循以下精确格式:
```
https://github.com/owner/repo/blob/[full-sha]/path/file.ext#L[start]-L[end]
```
- 必须使用完整 SHA (非缩写)
- 必须使用 `#L` 表示法
- 必须包含至少 1 行上下文的行范围

### GitHub CLI 不工作

**问题**: `gh` 命令失败

**解决方案**:
- 安装 GitHub CLI: `brew install gh` (macOS) 或参见 [GitHub CLI installation](https://cli.github.com/)
- 认证: `gh auth login`
- 验证仓库具有 GitHub 远程

## 技巧

- **编写具体的 CLAUDE.md 文件**: 清晰的规则 = 更好的审查
- **在 PR 中包含上下文**: 帮助 Agent 理解意图
- **使用置信度评分**: >=80 的问题通常是正确的
- **迭代规则**: 根据模式更新 CLAUDE.md
- **自动审查**: 设置为 PR 工作流的一部分
- **信任过滤**: 阈值防止噪音

## 配置

### 调整置信度阈值

默认阈值为 80. 要调整, 修改命令文件 `commands/code-review.md`:
```markdown
Filter out any issues with a score less than 80.
```

将 `80` 更改为您首选的阈值 (0-100).

### 自定义审查重点

编辑 `commands/code-review.md` 添加或修改 Agent 任务:
- 添加安全专注的 Agent
- 添加性能分析 Agent
- 添加可访问性检查 Agent
- 添加文档质量检查

## 技术细节

### Agent 架构
- **2x CLAUDE.md 合规 Agent**: 规则检查冗余
- **1x bug 检测器**: 专注于变更中的明显 bug
- **1x 历史分析器**: 来自 git blame 和历史的上下文
- **Nx 置信度评分器**: 每个问题一个, 独立评分

### 评分系统
- 每个问题独立评分 0-100
- 评分考虑证据强度和验证
- 阈值 (默认 80) 过滤低置信度问题
- 对于 CLAUDE.md 问题: 验证规则明确提到它

### GitHub 集成
使用 `gh` CLI 用于:
- 查看 PR 详情和差异
- 获取仓库数据
- 读取 git blame 和历史
- 发布审查评论

## 作者

Boris Cherny (boris@anthropic.com)

## 版本

1.0.0
