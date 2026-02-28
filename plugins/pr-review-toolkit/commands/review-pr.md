---
description: "使用专业 Agent 进行全面 PR 审查"
argument-hint: "[审查方面]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task"]
---

# 全面 PR 审查

使用多个专业 Agent 运行全面的 PR 审查, 每个 Agent 专注于代码质量的不同方面.

**审查方面 (可选):** "$ARGUMENTS"

## 审查工作流:

1. **确定审查范围**
   - 检查 git status 识别变更文件
   - 解析参数查看用户是否请求特定审查方面
   - 默认: 运行所有适用的审查

2. **可用的审查方面:**

   - **comments** - 分析代码注释准确性和可维护性
   - **tests** - 审查测试覆盖质量和完整性
   - **errors** - 检查错误处理的静默失败
   - **types** - 分析类型设计和不变量 (如果添加了新类型)
   - **code** - 项目规则通用代码审查
   - **simplify** - 简化代码以提高清晰度和可维护性
   - **all** - 运行所有适用的审查 (默认)

3. **识别变更文件**
   - 运行 `git diff --name-only` 查看修改的文件
   - 检查 PR 是否已存在: `gh pr view`
   - 识别文件类型和适用的审查

4. **确定适用的审查**

   基于变更:
   - **始终适用**: code-reviewer (通用质量)
   - **如果测试文件变更**: pr-test-analyzer
   - **如果添加注释/文档**: comment-analyzer
   - **如果错误处理变更**: silent-failure-hunter
   - **如果类型添加/修改**: type-design-analyzer
   - **通过审查后**: code-simplifier (优化和改进)

5. **启动审查 Agent**

   **顺序方式** (一次一个):
   - 更容易理解和执行
   - 每个报告在下一个之前完成
   - 适合交互式审查

   **并行方式** (用户可请求):
   - 同时启动所有 Agent
   - 更快的全面审查
   - 结果一起返回

6. **汇总结果**

   Agent 完成后, 总结:
   - **关键问题** (合并前必须修复)
   - **重要问题** (应该修复)
   - **建议** (最好有)
   - **正面观察** (什么是好的)

7. **提供行动计划**

   整理发现:
   ```markdown
   # PR 审查摘要

   ## 关键问题 (发现 X 个)
   - [agent-name]: 问题描述 [file:line]

   ## 重要问题 (发现 X 个)
   - [agent-name]: 问题描述 [file:line]

   ## 建议 (发现 X 个)
   - [agent-name]: 建议 [file:line]

   ## 优势
   - 此 PR 做得好的地方

   ## 推荐行动
   1. 首先修复关键问题
   2. 处理重要问题
   3. 考虑建议
   4. 修复后重新运行审查
   ```

## 用法示例:

**完整审查 (默认):**
```
/pr-review-toolkit:review-pr
```

**特定方面:**
```
/pr-review-toolkit:review-pr tests errors
# 只审查测试覆盖和错误处理

/pr-review-toolkit:review-pr comments
# 只审查代码注释

/pr-review-toolkit:review-pr simplify
# 通过审查后简化代码
```

**并行审查:**
```
/pr-review-toolkit:review-pr all parallel
# 并行启动所有 Agent
```

## Agent 描述:

**comment-analyzer**:
- 验证注释与代码的准确性
- 识别注释腐烂
- 检查文档完整性

**pr-test-analyzer**:
- 审查行为测试覆盖
- 识别关键缺口
- 评估测试质量

**silent-failure-hunter**:
- 查找静默失败
- 审查 catch 块
- 检查错误日志

**type-design-analyzer**:
- 分析类型封装
- 审查不变量表达
- 评分类型设计质量

**code-reviewer**:
- 检查 CLAUDE.md 合规性
- 检测 bug 和问题
- 审查通用代码质量

**code-simplifier**:
- 简化复杂代码
- 改进清晰度和可读性
- 应用项目标准
- 保留功能

## 技巧:

- **早期运行**: 在创建 PR 之前, 不是之后
- **关注变更**: Agent 默认分析 git diff
- **先解决关键问题**: 在低优先级之前修复高优先级问题
- **修复后重新运行**: 验证问题是否解决
- **使用特定审查**: 当您知道关注点时针对特定方面

## 工作流集成:

**提交前:**
```
1. 编写代码
2. 运行: /pr-review-toolkit:review-pr code errors
3. 修复任何关键问题
4. 提交
```

**创建 PR 前:**
```
1. 暂存所有变更
2. 运行: /pr-review-toolkit:review-pr all
3. 处理所有关键和重要问题
4. 再次运行特定审查以验证
5. 创建 PR
```

**PR 反馈后:**
```
1. 进行请求的变更
2. 根据反馈运行针对性审查
3. 验证问题是否解决
4. 推送更新
```

## 注意:

- Agent 自主运行并返回详细报告
- 每个 Agent 专注于其专业领域进行深入分析
- 结果可操作, 带有具体的 file:line 引用
- Agent 使用适合其复杂性的模型
- 所有 Agent 在 `/agents` 列表中可用
