---
name: warn-chinese-punctuation
enabled: true
event: file
action: warn
conditions:
  - field: content
    operator: regex_match
    pattern: [，。！？；：“‘【】《》、]
---

**检测到中文标点符号**

代码中存在中文标点符号, 这不符合规范:
- 检查是否误用了中文逗号应为英文 `,`
- 检查是否误用了中文冒号应为英文 `:`
- 检查是否误用了中文括号等

请确保代码中的标点符号使用英文半角符号
