---
name: skill-precheck-hook
enabled: true
event: skill
action: check
---

# Skill 执行前检查

当用户要求执行任何 Skill 时:
1. 读取 Skill 文件中的 `metadata.requires.bins` 或 `## Tools` 段落
2. 对每个工具执行 `which <tool>` 检测
3. 任何工具缺失 → 阻止执行, 提示用户安装
4. **禁止**: 工具缺失时继续读代码/生成方案/启动 Agent
