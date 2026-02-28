#!/usr/bin/env python3
"""UserPromptSubmit hook 执行器

此脚本在用户提交提示时被 Claude Code 调用.
读取 .claude/hookify.*.local.md 文件并评估规则.
"""

import os
import sys
import json

# 关键: 将插件根目录添加到 Python 路径以便导入
PLUGIN_ROOT = os.environ.get('CLAUDE_PLUGIN_ROOT')
if PLUGIN_ROOT:
    parent_dir = os.path.dirname(PLUGIN_ROOT)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    if PLUGIN_ROOT not in sys.path:
        sys.path.insert(0, PLUGIN_ROOT)

try:
    from core.config_loader import load_rules
    from core.rule_engine import RuleEngine
except ImportError as e:
    error_msg = {"systemMessage": f"Hookify 导入错误: {e}"}
    print(json.dumps(error_msg), file=sys.stdout)
    sys.exit(0)


def main():
    """UserPromptSubmit hook 主入口"""
    try:
        # 从 stdin 读取输入
        input_data = json.load(sys.stdin)

        # 加载用户提示规则
        rules = load_rules(event='prompt')

        # 评估规则
        engine = RuleEngine()
        result = engine.evaluate_rules(rules, input_data)

        # 始终输出 JSON (即使为空)
        print(json.dumps(result), file=sys.stdout)

    except Exception as e:
        error_output = {
            "systemMessage": f"Hookify 错误: {str(e)}"
        }
        print(json.dumps(error_output), file=sys.stdout)

    finally:
        # 始终退出 0
        sys.exit(0)


if __name__ == '__main__':
    main()
