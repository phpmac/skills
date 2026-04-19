---
name: block-cat-file-write
enabled: true
event: bash
pattern: \bcat\b\s+[^|&;]*[>]
action: block
---

禁止使用 cat 写入文件! 请使用 Write 或 Edit 工具代替.
