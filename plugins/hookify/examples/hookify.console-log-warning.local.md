---
name: warn-console-log
enabled: true
event: file
pattern: console\.log\(
action: warn
---

**检测到 console.log**

你正在添加 console.log 语句, 请考虑:
- 这是用于调试还是应该使用正式的日志记录?
- 这会被发布到生产环境吗?
- 是否应该使用日志库替代?
