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
- 所有回复必须使用英文标点符号,逗号/句号/分号/引号等禁止使用中文标点符号
- 代码注释必须使用中文,禁止使用英文注释,注释禁止使用中文标点符号包括，。！？；：“‘【】《》、等

请确保代码中的标点符号使用英文半角符号
