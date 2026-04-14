# Skill/Agent 执行强制预检

**触发条件**: 当用户要求执行任何 Skill 或启动 Agent 时.

**操作步骤**:
1. 读取目标 Skill/Agent 文件, 找到 `metadata.requires.bins` 或 `## Tools` 段落
2. 对每个依赖工具执行 `which <tool>` 检测
3. 输出结果表格
4. **任何工具缺失 → 立即停止, 明确告知用户**
5. **禁止**: 在工具缺失时继续读代码/生成方案/启动 Agent

**为什么**: coding_development.md 第 10 条已有此规则但 Claude 多次跳过, 需 Hook 强制执行.
