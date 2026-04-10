---
paths:
  - "**/*.sol"
  - "**/foundry.toml"
  - "**/remappings.txt"
---

# forge/foundry/solidity 规范

- 禁止使用 `slot` 读取,这个需要和人工沟通
- 默认不要添加 `--private-key $PRIVATE_KEY` 参数

## Solidity 测试输出规范

- 使用中文章节标题包裹主要内容区域 (如 `=== 系统状态 ===`)
- 阶段分隔格式: `  -> 阶段标题`
- 键值对输出需包含中文说明并用括号标注 (如 `key(中文说明): value`)
- 代币数值必须使用 `formatEther()` 格式化并标注单位 (如 `100 USDT`)
- 数值变化输出格式: `前 +变化 = 后`
- 多行输出使用模板字符串配合反引号保持缩进对齐
- 测试输出使用 `[测试] 功能: 验证点` 格式开头, 关键数据单独一行, 结尾标注 `通过`
- Solidity 字符串中使用中文需加 `unicode` 前缀 (如 `console.log(unicode"中文")`)
- 合约编写好要执行 `forge fmt && forge clean && forge build` ,commit之前必须执行,同时要关注命令输出的提示内容

## 常用过滤关键词

测试输出过滤使用: `阶段|结果|通过|失败|JM|BNB|USDT|Revert|Error|assert`
