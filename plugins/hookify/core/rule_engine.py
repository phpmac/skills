#!/usr/bin/env python3
"""规则评估引擎"""

import re
import sys
from functools import lru_cache
from typing import List, Dict, Any, Optional

# 从本地模块导入
from core.config_loader import Rule, Condition


# 缓存编译的正则表达式 (最多 128 个模式)
@lru_cache(maxsize=128)
def compile_regex(pattern: str) -> re.Pattern:
    """编译正则表达式模式并缓存

    Args:
        pattern: 正则表达式字符串

    Returns:
        编译后的正则表达式模式
    """
    return re.compile(pattern, re.IGNORECASE)


class RuleEngine:
    """根据 hook 输入数据评估规则"""

    def __init__(self):
        """初始化规则引擎"""
        # 不再需要实例缓存 - 使用全局 lru_cache
        pass

    def evaluate_rules(self, rules: List[Rule], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估所有规则并返回合并结果

        检查所有规则并累积匹配.阻止规则优先于警告规则.
        所有匹配的规则消息会被合并.

        Args:
            rules: 要评估的 Rule 对象列表
            input_data: Hook 输入 JSON (tool_name, tool_input 等)

        Returns:
            包含 systemMessage, hookSpecificOutput 等的响应字典
            如果没有规则匹配则返回空字典 {}.
        """
        hook_event = input_data.get('hook_event_name', '')
        blocking_rules = []
        warning_rules = []

        for rule in rules:
            if self._rule_matches(rule, input_data):
                if rule.action == 'block':
                    blocking_rules.append(rule)
                else:
                    warning_rules.append(rule)

        # 如果有阻止规则匹配, 阻止操作
        if blocking_rules:
            messages = [f"**[{r.name}]**\n{r.message}" for r in blocking_rules]
            combined_message = "\n\n".join(messages)

            # 根据事件类型使用适当的阻止格式
            if hook_event == 'Stop':
                return {
                    "decision": "block",
                    "reason": combined_message,
                    "systemMessage": combined_message
                }
            elif hook_event in ['PreToolUse', 'PostToolUse']:
                return {
                    "hookSpecificOutput": {
                        "hookEventName": hook_event,
                        "permissionDecision": "deny"
                    },
                    "systemMessage": combined_message
                }
            else:
                # 对于其他事件, 只显示消息
                return {
                    "systemMessage": combined_message
                }

        # 如果只有警告, 显示但允许操作
        if warning_rules:
            messages = [f"**[{r.name}]**\n{r.message}" for r in warning_rules]
            return {
                "systemMessage": "\n\n".join(messages)
            }

        # 没有匹配 - 允许操作
        return {}

    def _rule_matches(self, rule: Rule, input_data: Dict[str, Any]) -> bool:
        """检查规则是否匹配输入数据

        Args:
            rule: 要评估的规则
            input_data: Hook 输入数据

        Returns:
            如果规则匹配返回 True, 否则返回 False
        """
        # 提取工具信息
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})

        # 如果指定了工具匹配器则检查
        if rule.tool_matcher:
            if not self._matches_tool(rule.tool_matcher, tool_name):
                return False

        # 如果没有条件, 不匹配
        # (规则必须至少有一个条件才有效)
        if not rule.conditions:
            return False

        # 所有条件都必须匹配
        for condition in rule.conditions:
            if not self._check_condition(condition, tool_name, tool_input, input_data):
                return False

        return True

    def _matches_tool(self, matcher: str, tool_name: str) -> bool:
        """检查 tool_name 是否匹配匹配器模式

        Args:
            matcher: 模式如 "Bash", "Edit|Write", "*"
            tool_name: 实际工具名称

        Returns:
            如果匹配返回 True
        """
        if matcher == '*':
            return True

        # 按 | 分割进行 OR 匹配
        patterns = matcher.split('|')
        return tool_name in patterns

    def _check_condition(self, condition: Condition, tool_name: str,
                        tool_input: Dict[str, Any], input_data: Dict[str, Any] = None) -> bool:
        """检查单个条件是否匹配

        Args:
            condition: 要检查的条件
            tool_name: 正在使用的工具
            tool_input: 工具输入字典
            input_data: 完整的 hook 输入数据 (用于 Stop 事件等)

        Returns:
            如果条件匹配返回 True
        """
        # 提取要检查的字段值
        field_value = self._extract_field(condition.field, tool_name, tool_input, input_data)
        if field_value is None:
            return False

        # 应用操作符
        operator = condition.operator
        pattern = condition.pattern

        if operator == 'regex_match':
            return self._regex_match(pattern, field_value)
        elif operator == 'contains':
            return pattern in field_value
        elif operator == 'equals':
            return pattern == field_value
        elif operator == 'not_contains':
            return pattern not in field_value
        elif operator == 'starts_with':
            return field_value.startswith(pattern)
        elif operator == 'ends_with':
            return field_value.endswith(pattern)
        else:
            # 未知操作符
            return False

    def _extract_field(self, field: str, tool_name: str,
                      tool_input: Dict[str, Any], input_data: Dict[str, Any] = None) -> Optional[str]:
        """从工具输入或 hook 输入数据中提取字段值

        Args:
            field: 字段名如 "command", "new_text", "file_path", "reason", "transcript"
            tool_name: 正在使用的工具 (Stop 事件可能为空)
            tool_input: 工具输入字典
            input_data: 完整的 hook 输入 (用于访问 transcript_path, reason 等)

        Returns:
            字段值作为字符串, 如果未找到则返回 None
        """
        # 直接 tool_input 字段
        if field in tool_input:
            value = tool_input[field]
            if isinstance(value, str):
                return value
            return str(value)

        # 对于 Stop 事件和其他非工具事件, 检查 input_data
        if input_data:
            # Stop 事件特定字段
            if field == 'reason':
                return input_data.get('reason', '')
            elif field == 'transcript':
                # 如果提供了路径则读取对话记录文件
                transcript_path = input_data.get('transcript_path')
                if transcript_path:
                    try:
                        with open(transcript_path, 'r') as f:
                            return f.read()
                    except FileNotFoundError:
                        print(f"警告: 未找到对话记录文件: {transcript_path}", file=sys.stderr)
                        return ''
                    except PermissionError:
                        print(f"警告: 无权限读取对话记录: {transcript_path}", file=sys.stderr)
                        return ''
                    except (IOError, OSError) as e:
                        print(f"警告: 读取对话记录错误 {transcript_path}: {e}", file=sys.stderr)
                        return ''
                    except UnicodeDecodeError as e:
                        print(f"警告: 对话记录编码错误 {transcript_path}: {e}", file=sys.stderr)
                        return ''
            elif field == 'user_prompt':
                # 用于 UserPromptSubmit 事件
                return input_data.get('user_prompt', '')

        # 按工具类型处理特殊情况
        if tool_name == 'Bash':
            if field == 'command':
                return tool_input.get('command', '')

        elif tool_name in ['Write', 'Edit']:
            if field == 'content':
                # Write 使用 'content', Edit 有 'new_string'
                return tool_input.get('content') or tool_input.get('new_string', '')
            elif field == 'new_text' or field == 'new_string':
                return tool_input.get('new_string', '')
            elif field == 'old_text' or field == 'old_string':
                return tool_input.get('old_string', '')
            elif field == 'file_path':
                return tool_input.get('file_path', '')

        elif tool_name == 'MultiEdit':
            if field == 'file_path':
                return tool_input.get('file_path', '')
            elif field in ['new_text', 'content']:
                # 连接所有编辑
                edits = tool_input.get('edits', [])
                return ' '.join(e.get('new_string', '') for e in edits)

        return None

    def _regex_match(self, pattern: str, text: str) -> bool:
        """使用正则表达式检查模式是否匹配文本

        Args:
            pattern: 正则表达式模式
            text: 要匹配的文本

        Returns:
            如果模式匹配返回 True
        """
        try:
            # 使用缓存的编译正则 (LRU 缓存最多 128 个模式)
            regex = compile_regex(pattern)
            return bool(regex.search(text))

        except re.error as e:
            print(f"无效的正则模式 '{pattern}': {e}", file=sys.stderr)
            return False


# 用于测试
if __name__ == '__main__':
    from core.config_loader import Condition, Rule

    # 测试规则评估
    rule = Rule(
        name="test-rm",
        enabled=True,
        event="bash",
        conditions=[
            Condition(field="command", operator="regex_match", pattern=r"rm\s+-rf")
        ],
        message="危险的 rm 命令!"
    )

    engine = RuleEngine()

    # 测试匹配输入
    test_input = {
        "tool_name": "Bash",
        "tool_input": {
            "command": "rm -rf /tmp/test"
        }
    }

    result = engine.evaluate_rules([rule], test_input)
    print("匹配结果:", result)

    # 测试不匹配输入
    test_input2 = {
        "tool_name": "Bash",
        "tool_input": {
            "command": "ls -la"
        }
    }

    result2 = engine.evaluate_rules([rule], test_input2)
    print("不匹配结果:", result2)
