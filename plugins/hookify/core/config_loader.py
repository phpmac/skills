#!/usr/bin/env python3
"""配置加载器

加载和解析 .claude/hookify.*.local.md 文件.
"""

import os
import sys
import glob
import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Condition:
    """单个匹配条件"""
    field: str  # "command", "new_text", "old_text", "file_path" 等
    operator: str  # "regex_match", "contains", "equals" 等
    pattern: str  # 匹配模式

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Condition':
        """从字典创建 Condition"""
        return cls(
            field=data.get('field', ''),
            operator=data.get('operator', 'regex_match'),
            pattern=data.get('pattern', '')
        )


@dataclass
class Rule:
    """hookify 规则"""
    name: str
    enabled: bool
    event: str  # "bash", "file", "stop", "all" 等
    pattern: Optional[str] = None  # 简单模式 (旧版)
    conditions: List[Condition] = field(default_factory=list)
    action: str = "warn"  # "warn" 或 "block"
    tool_matcher: Optional[str] = None  # 覆盖工具匹配
    message: str = ""  # markdown 中的消息体

    @classmethod
    def from_dict(cls, frontmatter: Dict[str, Any], message: str) -> 'Rule':
        """从 frontmatter 字典和消息体创建 Rule"""
        # 处理简单模式和复杂条件
        conditions = []

        # 新风格: 显式 conditions 列表
        if 'conditions' in frontmatter:
            cond_list = frontmatter['conditions']
            if isinstance(cond_list, list):
                conditions = [Condition.from_dict(c) for c in cond_list]

        # 旧风格: 简单 pattern 字段
        simple_pattern = frontmatter.get('pattern')
        if simple_pattern and not conditions:
            # 将简单模式转换为条件
            # 从 event 推断字段
            event = frontmatter.get('event', 'all')
            if event == 'bash':
                field = 'command'
            elif event == 'file':
                field = 'new_text'
            else:
                field = 'content'

            conditions = [Condition(
                field=field,
                operator='regex_match',
                pattern=simple_pattern
            )]

        return cls(
            name=frontmatter.get('name', 'unnamed'),
            enabled=frontmatter.get('enabled', True),
            event=frontmatter.get('event', 'all'),
            pattern=simple_pattern,
            conditions=conditions,
            action=frontmatter.get('action', 'warn'),
            tool_matcher=frontmatter.get('tool_matcher'),
            message=message.strip()
        )


def extract_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """从 markdown 中提取 YAML frontmatter 和消息体

    返回 (frontmatter_dict, message_body)

    通过保留缩进支持列表中的多行字典项.
    """
    if not content.startswith('---'):
        return {}, content

    # 按 --- 标记分割
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    frontmatter_text = parts[1]
    message = parts[2].strip()

    # 处理缩进列表项的简单 YAML 解析器
    frontmatter = {}
    lines = frontmatter_text.split('\n')

    current_key = None
    current_list = []
    current_dict = {}
    in_list = False
    in_dict_item = False

    for line in lines:
        # 跳过空行和注释
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # 检查缩进级别
        indent = len(line) - len(line.lstrip())

        # 顶层键 (无缩进或最小缩进)
        if indent == 0 and ':' in line and not line.strip().startswith('-'):
            # 保存之前的 list/dict
            if in_list and current_key:
                if in_dict_item and current_dict:
                    current_list.append(current_dict)
                    current_dict = {}
                frontmatter[current_key] = current_list
                in_list = False
                in_dict_item = False
                current_list = []

            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if not value:
                # 空值 - 列表或嵌套结构紧随其后
                current_key = key
                in_list = True
                current_list = []
            else:
                # 简单键值对
                value = value.strip('"').strip("'")
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                frontmatter[key] = value

        # 列表项 (以 - 开头)
        elif stripped.startswith('-') and in_list:
            # 保存之前的 dict 项
            if in_dict_item and current_dict:
                current_list.append(current_dict)
                current_dict = {}

            item_text = stripped[1:].strip()

            # 检查是否为内联 dict (同一行有 key: value)
            if ':' in item_text and ',' in item_text:
                # 内联逗号分隔 dict: "- field: command, operator: regex_match"
                item_dict = {}
                for part in item_text.split(','):
                    if ':' in part:
                        k, v = part.split(':', 1)
                        item_dict[k.strip()] = v.strip().strip('"').strip("'")
                current_list.append(item_dict)
                in_dict_item = False
            elif ':' in item_text:
                # 多行 dict 项开始: "- field: command"
                in_dict_item = True
                k, v = item_text.split(':', 1)
                current_dict = {k.strip(): v.strip().strip('"').strip("'")}
            else:
                # 简单列表项
                current_list.append(item_text.strip('"').strip("'"))
                in_dict_item = False

        # dict 项的延续 (在列表项下缩进)
        elif indent > 2 and in_dict_item and ':' in line:
            # 这是当前 dict 项的字段
            k, v = stripped.split(':', 1)
            current_dict[k.strip()] = v.strip().strip('"').strip("'")

    # 保存最后的 list/dict
    if in_list and current_key:
        if in_dict_item and current_dict:
            current_list.append(current_dict)
        frontmatter[current_key] = current_list

    return frontmatter, message


def load_rules(event: Optional[str] = None) -> List[Rule]:
    """从 .claude 目录加载所有 hookify 规则

    Args:
        event: 可选的事件过滤器 ("bash", "file", "stop" 等)

    Returns:
        匹配事件的已启用 Rule 对象列表.
    """
    rules = []

    # 在多个位置查找所有 hookify.*.local.md 文件
    search_paths = [
        os.path.join('.claude', 'hookify.*.local.md'),  # 当前目录
        os.path.join(os.path.expanduser('~'), '.claude', 'hookify.*.local.md'),  # 主目录
    ]

    files = []
    for pattern in search_paths:
        files.extend(glob.glob(pattern))

    for file_path in files:
        try:
            rule = load_rule_file(file_path)
            if not rule:
                continue

            # 如果指定了事件则过滤
            if event:
                if rule.event != 'all' and rule.event != event:
                    continue

            # 只包含已启用的规则
            if rule.enabled:
                rules.append(rule)

        except (IOError, OSError, PermissionError) as e:
            # 文件 I/O 错误 - 记录并继续
            print(f"警告: 无法读取 {file_path}: {e}", file=sys.stderr)
            continue
        except (ValueError, KeyError, AttributeError, TypeError) as e:
            # 解析错误 - 记录并继续
            print(f"警告: 无法解析 {file_path}: {e}", file=sys.stderr)
            continue
        except Exception as e:
            # 意外错误 - 记录类型详情
            print(f"警告: 加载 {file_path} 时发生意外错误 ({type(e).__name__}): {e}", file=sys.stderr)
            continue

    return rules


def load_rule_file(file_path: str) -> Optional[Rule]:
    """加载单个规则文件

    Returns:
        Rule 对象, 如果文件无效则返回 None.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        frontmatter, message = extract_frontmatter(content)

        if not frontmatter:
            print(f"警告: {file_path} 缺少 YAML frontmatter (必须以 --- 开头)", file=sys.stderr)
            return None

        rule = Rule.from_dict(frontmatter, message)
        return rule

    except (IOError, OSError, PermissionError) as e:
        print(f"错误: 无法读取 {file_path}: {e}", file=sys.stderr)
        return None
    except (ValueError, KeyError, AttributeError, TypeError) as e:
        print(f"错误: 规则文件格式错误 {file_path}: {e}", file=sys.stderr)
        return None
    except UnicodeDecodeError as e:
        print(f"错误: {file_path} 编码无效: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"错误: 解析 {file_path} 时发生意外错误 ({type(e).__name__}): {e}", file=sys.stderr)
        return None


# 用于测试
if __name__ == '__main__':
    import sys

    # 测试 frontmatter 解析
    test_content = """---
name: test-rule
enabled: true
event: bash
pattern: "rm -rf"
---

检测到危险命令!
"""

    fm, msg = extract_frontmatter(test_content)
    print("Frontmatter:", fm)
    print("Message:", msg)

    rule = Rule.from_dict(fm, msg)
    print("Rule:", rule)
