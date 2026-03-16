---
name: cursor-escalator
description: |
  **默认使用**: 当用户要求分析/检查/审查/策划/设计/方案, 或消息中包含 cursor 关键字时, 默认使用此 agent 委托给 Cursor 处理.
  触发场景: (1) 包含 cursor 关键字 (2) 分析/检查/审查代码 (3) 策划/设计/提供方案 (4) 问题反复找不到原因 (5) 多次尝试失败 (6) 需要更强模型.
license: MIT
---

## 上下文打包 (关键)

Cursor 是全新会话, 看不到任何历史. Prompt 必须包含:

```markdown
## 原始需求(背景介绍)
<总结内容>

## 相关文件
- <路径>:<行号> - <改动说明>

## 关键代码片段
<只提供变动位置的关键片段>

## 已尝试方案
1. <方案>: <失败原因>

## 期望结果
<希望达到什么效果>
```

## 调用命令

```bash
# 标准格式
agent --stream-partial-output --output-format stream-json -p "<prompt>"

# 指定模型
agent --stream-partial-output --output-format stream-json -p "<prompt>" --model "opus-4.6"
```

## 注意事项

1. 提供的方案不一定准确, 自己要证实
2. 不要写入到文件,对话可以看到返回内容