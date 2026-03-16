---
name: warn-cat-usage
enabled: true
event: file
action: warn
conditions:
  - field: content
    operator: regex_match
    pattern: cat\s+[\>\|]|cat\s+\<|\`cat\s|cat\s+\`|
---

**检测到 cat 命令不当使用**

代码中存在 cat 命令的错误用法:
- 禁止使用 `cat` 写入文件 (如 `cat > file` 或 `cat |`)
- 禁止使用 `cat` 读取文件内容到变量 (如 `var=$(cat file)`)
- 使用专用工具代替 cat:
  - 写入文件: 使用 `Write` 工具
  - 读取文件: 使用 `Read` 工具
  - 追加内容: 使用 `Edit` 工具
  - 搜索内容: 使用 `Grep` 工具

请使用 Claude Code 提供的专用工具进行文件操作, 不要使用 shell 的 cat 命令
