#!/usr/bin/env bash
# 读取 ~/.claude/CLAUDE.md 内容注入到 SessionStart context

CLAUDE_MD="$HOME/.claude/CLAUDE.md"

if [[ ! -f "$CLAUDE_MD" ]]; then
  exit 0
fi

python3 - "$CLAUDE_MD" << 'PYEOF'
import sys, json

with open(sys.argv[1], "r", encoding="utf-8") as f:
    rules = f.read()

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": rules
    }
}, ensure_ascii=False))
PYEOF
