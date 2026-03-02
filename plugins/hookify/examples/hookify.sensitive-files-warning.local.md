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
- 确保没有硬编码凭据
- 使用环境变量存储机密
- 验证此文件已加入 .gitignore
- 考虑使用密钥管理器
