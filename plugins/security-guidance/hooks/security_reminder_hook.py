#!/usr/bin/env python3
"""
Claude Code 安全提醒钩子
检查文件编辑中的安全模式并警告潜在漏洞.
"""

import json
import os
import random
import sys
from datetime import datetime

# 调试日志文件
DEBUG_LOG_FILE = "/tmp/security-warnings-log.txt"


def debug_log(message):
    """将调试消息追加到日志文件."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        # 静默忽略日志错误以避免中断钩子
        pass


# 用于跟踪已显示警告的状态文件 (使用会话ID限定作用域)

# 安全模式配置
SECURITY_PATTERNS = [
    {
        "ruleName": "github_actions_workflow",
        "path_check": lambda path: ".github/workflows/" in path
        and (path.endswith(".yml") or path.endswith(".yaml")),
        "reminder": """你正在编辑 GitHub Actions 工作流文件, 请注意以下安全风险:

1. **命令注入**: 绝不要在 run: 命令中直接使用不受信任的输入 (如 issue 标题, PR 描述, 提交消息), 必须正确转义
2. **使用环境变量**: 不要使用 ${{ github.event.issue.title }}, 改用 env: 并正确引用
3. **参考指南**: https://github.blog/security/vulnerability-research/how-to-catch-github-actions-workflow-injections-before-attackers-do/

不安全模式示例 (避免):
run: echo "${{ github.event.issue.title }}"

安全模式示例:
env:
  TITLE: ${{ github.event.issue.title }}
run: echo "$TITLE"

其他需要注意的风险输入:
- github.event.issue.body
- github.event.pull_request.title
- github.event.pull_request.body
- github.event.comment.body
- github.event.review.body
- github.event.review_comment.body
- github.event.pages.*.page_name
- github.event.commits.*.message
- github.event.head_commit.message
- github.event.head_commit.author.email
- github.event.head_commit.author.name
- github.event.commits.*.author.email
- github.event.commits.*.author.name
- github.event.pull_request.head.ref
- github.event.pull_request.head.label
- github.event.pull_request.head.repo.default_branch
- github.head_ref""",
    },
    {
        "ruleName": "child_process_exec",
        "substrings": ["child_process.exec", "exec(", "execSync("],
        "reminder": """安全警告: 使用 child_process.exec() 可能导致命令注入漏洞.

此代码库提供了更安全的替代方案: src/utils/execFileNoThrow.ts

不要这样写:
  exec(`command ${userInput}`)

应该这样写:
  import { execFileNoThrow } from '../utils/execFileNoThrow.js'
  await execFileNoThrow('command', [userInput])

execFileNoThrow 工具函数:
- 使用 execFile 而非 exec (防止 shell 注入)
- 自动处理 Windows 兼容性
- 提供正确的错误处理
- 返回结构化输出 (stdout, stderr, status)

只有在你确实需要 shell 特性且输入保证安全时才使用 exec().""",
    },
    {
        "ruleName": "new_function_injection",
        "substrings": ["new Function"],
        "reminder": "安全警告: 使用 new Function() 处理动态字符串可能导致代码注入漏洞. 请考虑不需要执行任意代码的替代方案. 只有在你确实需要执行任意动态代码时才使用 new Function().",
    },
    {
        "ruleName": "eval_injection",
        "substrings": ["eval("],
        "reminder": "安全警告: eval() 会执行任意代码, 是重大安全风险. 数据解析请考虑使用 JSON.parse() 或不需要代码执行的其他设计模式. 只有在你确实需要执行任意代码时才使用 eval().",
    },
    {
        "ruleName": "react_dangerously_set_html",
        "substrings": ["dangerouslySetInnerHTML"],
        "reminder": "安全警告: 对不受信任的内容使用 dangerouslySetInnerHTML 可能导致 XSS 漏洞. 确保所有内容都使用 HTML 消毒库 (如 DOMPurify) 正确消毒, 或使用安全的替代方案.",
    },
    {
        "ruleName": "document_write_xss",
        "substrings": ["document.write"],
        "reminder": "安全警告: document.write() 可被利用进行 XSS 攻击, 且有性能问题. 请改用 createElement() 和 appendChild() 等 DOM 操作方法.",
    },
    {
        "ruleName": "innerHTML_xss",
        "substrings": [".innerHTML =", ".innerHTML="],
        "reminder": "安全警告: 对不受信任的内容设置 innerHTML 可能导致 XSS 漏洞. 纯文本请使用 textContent, HTML 内容请使用安全的 DOM 方法. 如需支持 HTML, 请考虑使用 DOMPurify 等 HTML 消毒库.",
    },
    {
        "ruleName": "pickle_deserialization",
        "substrings": ["pickle"],
        "reminder": "安全警告: 对不受信任的内容使用 pickle 可能导致任意代码执行. 请考虑使用 JSON 或其他安全的序列化格式. 只有在明确需要或用户要求时才使用 pickle.",
    },
    {
        "ruleName": "os_system_injection",
        "substrings": ["os.system", "from os import system"],
        "reminder": "安全警告: 此代码似乎使用了 os.system. 此函数只应与静态参数一起使用, 绝不要与可能受用户控制的参数一起使用.",
    },
]


def get_state_file(session_id):
    """获取会话特定的状态文件路径."""
    return os.path.expanduser(f"~/.claude/security_warnings_state_{session_id}.json")


def cleanup_old_state_files():
    """删除 30 天前的状态文件."""
    try:
        state_dir = os.path.expanduser("~/.claude")
        if not os.path.exists(state_dir):
            return

        current_time = datetime.now().timestamp()
        thirty_days_ago = current_time - (30 * 24 * 60 * 60)

        for filename in os.listdir(state_dir):
            if filename.startswith("security_warnings_state_") and filename.endswith(
                ".json"
            ):
                file_path = os.path.join(state_dir, filename)
                try:
                    file_mtime = os.path.getmtime(file_path)
                    if file_mtime < thirty_days_ago:
                        os.remove(file_path)
                except (OSError, IOError):
                    pass  # 忽略单个文件清理的错误
    except Exception:
        pass  # 静默忽略清理错误


def load_state(session_id):
    """从文件加载已显示警告的状态."""
    state_file = get_state_file(session_id)
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError):
            return set()
    return set()


def save_state(session_id, shown_warnings):
    """将已显示警告的状态保存到文件."""
    state_file = get_state_file(session_id)
    try:
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        with open(state_file, "w") as f:
            json.dump(list(shown_warnings), f)
    except IOError as e:
        debug_log(f"保存状态文件失败: {e}")
        pass  # 如果无法保存状态则静默失败


def check_patterns(file_path, content):
    """检查文件路径或内容是否匹配任何安全模式."""
    # 通过移除前导斜杠规范化路径
    normalized_path = file_path.lstrip("/")

    for pattern in SECURITY_PATTERNS:
        # 检查基于路径的模式
        if "path_check" in pattern and pattern["path_check"](normalized_path):
            return pattern["ruleName"], pattern["reminder"]

        # 检查基于内容的模式
        if "substrings" in pattern and content:
            for substring in pattern["substrings"]:
                if substring in content:
                    return pattern["ruleName"], pattern["reminder"]

    return None, None


def extract_content_from_input(tool_name, tool_input):
    """根据工具类型从工具输入中提取要检查的内容."""
    if tool_name == "Write":
        return tool_input.get("content", "")
    elif tool_name == "Edit":
        return tool_input.get("new_string", "")
    elif tool_name == "MultiEdit":
        edits = tool_input.get("edits", [])
        if edits:
            return " ".join(edit.get("new_string", "") for edit in edits)
        return ""

    return ""


def main():
    """主钩子函数."""
    # 检查是否启用了安全提醒
    security_reminder_enabled = os.environ.get("ENABLE_SECURITY_REMINDER", "1")

    # 仅在启用安全提醒时运行
    if security_reminder_enabled == "0":
        sys.exit(0)

    # 定期清理旧状态文件 (每次运行 10% 概率)
    if random.random() < 0.1:
        cleanup_old_state_files()

    # 从 stdin 读取输入
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except json.JSONDecodeError as e:
        debug_log(f"JSON 解码错误: {e}")
        sys.exit(0)  # 如果无法解析输入则允许工具继续

    # 从钩子输入中提取会话 ID 和工具信息
    session_id = input_data.get("session_id", "default")
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # 检查是否为相关工具
    if tool_name not in ["Edit", "Write", "MultiEdit"]:
        sys.exit(0)  # 允许非文件工具继续

    # 从 tool_input 中提取文件路径
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)  # 如果没有文件路径则允许

    # 提取要检查的内容
    content = extract_content_from_input(tool_name, tool_input)

    # 检查安全模式
    rule_name, reminder = check_patterns(file_path, content)

    if rule_name and reminder:
        # 创建唯一警告键
        warning_key = f"{file_path}-{rule_name}"

        # 加载此会话的现有警告
        shown_warnings = load_state(session_id)

        # 检查是否已在此会话中显示过此警告
        if warning_key not in shown_warnings:
            # 添加到已显示警告并保存
            shown_warnings.add(warning_key)
            save_state(session_id, shown_warnings)

            # 将警告输出到 stderr 并阻止执行
            print(reminder, file=sys.stderr)
            sys.exit(2)  # 阻止工具执行 (PreToolUse 钩子使用退出码 2)

    # 允许工具继续
    sys.exit(0)


if __name__ == "__main__":
    main()
