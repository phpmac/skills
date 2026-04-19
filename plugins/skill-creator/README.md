# skill-creator

创建/改进/测试/基准测试 Claude Code 技能.

## 功能

- 从零创建新 Skill
- 改进和优化已有 Skill
- 运行测试来测试 Skill 表现
- 基准测试与方差分析
- 描述优化提高触发准确率

## 工作流

1. 捕获意图 -> 访谈研究 -> 编写 SKILL.md
2. 创建测试用例 -> 并行运行(有技能 vs 基线)
3. 评分 -> 基准汇总 -> 可视化审查
4. 用户反馈 -> 改进技能 -> 重复迭代
5. 描述优化 -> 打包发布

## 包含

| 组件 | 说明 |
|------|------|
| SKILL.md | 主技能: 创建/修改/测试/基准测试 |
| agents/grader.md | 评分器: 针对输出评估断言 |
| agents/comparator.md | 盲比较器: A/B 盲评 |
| agents/analyzer.md | 分析器: 为什么赢/输 + 基准模式分析 |
| references/schemas.md | JSON schema 定义 |
| scripts/ | 汇总/基准/打包脚本 |
| eval-viewer/ | 结果可视化查看器 |
| assets/ | HTML 模板等资源 |
