---
name: warn-dangerous-rm
enabled: true
event: bash
pattern: rm\s+(-rf|-fr|--recursive|--force)
action: warn
---

**检测到危险的 rm 命令!**

此命令可能删除重要文件, 请:
- 确认路径是否正确
- 考虑使用更安全的方式
- 确保已有备份
