---
name: warn-sensitive-files
enabled: true
event: file
action: block
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.env$|\.env\.|credentials|secrets
---

**检测到敏感文件**

你正在编辑可能包含敏感数据的文件:
- 建议人工手动添加
