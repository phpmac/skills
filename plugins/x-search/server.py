#!/usr/bin/env python3
"""X (Twitter) 搜索 MCP Server - 基于 xAI Grok API"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.request import Request, HTTPRedirectHandler, build_opener
from urllib.error import URLError, HTTPError

from mcp.server.fastmcp import FastMCP

# ── 常量 ──────────────────────────────────────────────
API_URL = "https://api.x.ai/v1/responses"
MODEL = "grok-4.20-0309-reasoning"  # 默认值, _init_config() 可覆盖
TIMEOUT_S = 120
MAX_HANDLES = 10
MAX_DOMAINS = 5
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HANDLE_RE = re.compile(r"^[a-zA-Z0-9_]{1,15}$")
TWEET_URL_RE = re.compile(r"(?:x\.com|twitter\.com)/([a-zA-Z0-9_]{1,15})/status/(\d+)")

mcp = FastMCP("x-search")

# ── 错误响应构造 ──────────────────────────────────────


def _error(query: str, text: str) -> dict:
    """构造统一的错误响应"""
    return {
        "status": "error",
        "query": query,
        "text": text,
        "citations": [],
        "searches": 0,
        "tokens": {"input": 0, "output": 0},
    }


# ── 内部工具函数 ──────────────────────────────────────


class _NoRedirect(HTTPRedirectHandler):
    """阻止重定向, 防止 API Key 泄露到其他域名"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(
            newurl, code, f"Redirect to {newurl} blocked (auth safety)", headers, fp
        )


def _validate_handles(
    handles: list[str] | None,
    exclude: list[str] | None,
) -> str | None:
    """校验 handles/exclude 参数, 返回错误信息或 None"""
    if handles is not None and exclude is not None:
        return "handles 和 exclude 不能同时使用."
    if handles is not None and len(handles) == 0:
        return "handles 值为空."
    if exclude is not None and len(exclude) == 0:
        return "exclude 值为空."
    for h in (handles or []) + (exclude or []):
        if not HANDLE_RE.match(h):
            return f'"{h}" 不是有效的 X 用户名 (字母/数字/下划线, 最长15位).'
    if handles and len(handles) > MAX_HANDLES:
        return f"handles 最多 {MAX_HANDLES} 个, 当前 {len(handles)} 个."
    if exclude and len(exclude) > MAX_HANDLES:
        return f"exclude 最多 {MAX_HANDLES} 个, 当前 {len(exclude)} 个."
    return None


def _validate_dates(from_date: str | None, to_date: str | None) -> str | None:
    """校验日期参数, 返回错误信息或 None"""
    if from_date and not DATE_RE.match(from_date):
        return f'from_date 格式错误, 需要 YYYY-MM-DD, 得到 "{from_date}".'
    if to_date and not DATE_RE.match(to_date):
        return f'to_date 格式错误, 需要 YYYY-MM-DD, 得到 "{to_date}".'
    if from_date:
        try:
            datetime.strptime(from_date, "%Y-%m-%d")
        except ValueError:
            return f'from_date "{from_date}" 不是有效日期.'
    if to_date:
        try:
            datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            return f'to_date "{to_date}" 不是有效日期.'
    if from_date and to_date and from_date > to_date:
        return f"from_date ({from_date}) 必须早于 to_date ({to_date})."
    return None


def _validate_domains(
    allowed: list[str] | None,
    excluded: list[str] | None,
) -> str | None:
    """校验域名过滤参数, 返回错误信息或 None"""
    if allowed is not None and excluded is not None:
        return "allowed_domains 和 excluded_domains 不能同时使用."
    if allowed is not None and len(allowed) == 0:
        return "allowed_domains 值为空."
    if excluded is not None and len(excluded) == 0:
        return "excluded_domains 值为空."
    if allowed and len(allowed) > MAX_DOMAINS:
        return f"allowed_domains 最多 {MAX_DOMAINS} 个, 当前 {len(allowed)} 个."
    if excluded and len(excluded) > MAX_DOMAINS:
        return f"excluded_domains 最多 {MAX_DOMAINS} 个, 当前 {len(excluded)} 个."
    return None


def _safe_get(obj: object, key: str, default: object = None) -> object:
    """安全取值"""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _format_response(data: dict, query: str, tool_type: str = "x_search") -> dict:
    """解析 API 响应"""
    outputs = _safe_get(data, "output", [])
    if not isinstance(outputs, list):
        outputs = []
    usage = _safe_get(data, "usage", {})
    if not isinstance(usage, dict):
        usage = {}
    tool_details = _safe_get(usage, "server_side_tool_usage_details", {})
    if not isinstance(tool_details, dict):
        tool_details = {}

    message = next(
        (o for o in outputs if isinstance(o, dict) and o.get("type") == "message"), None
    )
    content_blocks = _safe_get(message, "content", [])
    if not isinstance(content_blocks, list):
        content_blocks = []

    text = "\n\n".join(
        c.get("text", "")
        for c in content_blocks
        if isinstance(c, dict) and c.get("text")
    )
    annotations = [
        a
        for c in content_blocks
        if isinstance(c, dict)
        for a in (c.get("annotations") or [])
        if isinstance(a, dict)
    ]
    citations = [
        {"text": a.get("title", ""), "url": a["url"]}
        for a in annotations
        if a.get("type") == "url_citation" and a.get("url")
    ]

    status = _safe_get(data, "status", "unknown") or "unknown"
    if status not in ("completed", "unknown"):
        error = _safe_get(data, "error", {})
        error_msg = error.get("message", "") if isinstance(error, dict) else str(error)
        text = (
            f"Search {status}"
            + (f": {error_msg}" if error_msg else "")
            + ("\n\n" + text if text else "")
        )

    # 根据 tool_type 提取不同的 usage 统计
    result = {
        "status": status,
        "query": query,
        "text": text,
        "citations": citations,
        "tool_type": tool_type,
        "tokens": {
            "input": usage.get("input_tokens", 0),
            "output": usage.get("output_tokens", 0),
        },
    }
    if tool_type == "x_search":
        result["searches"] = tool_details.get("x_search_calls", 0)
    elif tool_type == "web_search":
        result["searches"] = tool_details.get("web_search_calls", 0)
    else:
        result["searches"] = tool_details.get("x_search_calls", 0)

    return result


def _init_config():
    """从环境变量或 .env 文件初始化配置"""
    global MODEL
    env_path = Path.home() / ".claude" / "channels" / "x-search" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("XAI_MODEL="):
                val = line.split("=", 1)[1].strip().strip("'\"")
                if val:
                    MODEL = val
    # 环境变量优先于 .env 文件
    env_val = os.environ.get("XAI_MODEL", "").strip()
    if env_val:
        MODEL = env_val


_init_config()


def _get_api_key() -> str | None:
    """从环境变量或 .env 文件获取 XAI_API_KEY"""
    key = os.environ.get("XAI_API_KEY", "").strip()
    if key:
        return key
    env_path = Path.home() / ".claude" / "channels" / "x-search" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("XAI_API_KEY="):
                return line.split("=", 1)[1].strip().strip("'\"")
    return None


def _call_api(tools: list[dict], query: str, tool_type: str = "x_search") -> dict:
    """公共 API 调用函数, 所有工具共享"""
    api_key = _get_api_key()
    if not api_key:
        return _error(
            query,
            "XAI_API_KEY 未设置. 请创建 ~/.claude/channels/x-search/.env 并写入 XAI_API_KEY=your-key",
        )

    body = json.dumps(
        {
            "model": MODEL,
            "input": [{"role": "user", "content": query}],
            "tools": tools,
        }
    ).encode()

    req = Request(
        API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "OpenClaw/x-search-mcp",
        },
        method="POST",
    )

    opener = build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=TIMEOUT_S) as resp:
            data = json.loads(resp.read())
    except HTTPError as e:
        try:
            error_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        except Exception:
            error_body = ""
        return _error(query, f"API 错误 ({e.code}): {error_body}")
    except URLError as e:
        return _error(query, f"网络请求失败: {e.reason}")
    except TimeoutError:
        return _error(query, f"请求超时 ({TIMEOUT_S}s).")
    except json.JSONDecodeError:
        return _error(query, "API 响应 JSON 解析失败.")
    except OSError as e:
        return _error(query, f"连接错误: {e}")

    return _format_response(data, query, tool_type)


# ── MCP 工具 ──────────────────────────────────────────


@mcp.tool()
def x_search(
    prompt: str,
    handles: list[str] | None = None,
    exclude: list[str] | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    images: bool = False,
    video: bool = False,
) -> dict:
    """使用 xAI Grok API 搜索 X (Twitter) 帖子.

    参数:
        prompt: 自然语言输入, 支持关键词/语义描述/问题等形式, Grok AI 处理后搜索推特并返回结构化结果
        handles: 筛选指定用户 (最多 10 个)
        exclude: 排除指定用户 (最多 10 个, 与 handles 互斥)
        from_date: 起始日期 YYYY-MM-DD
        to_date: 结束日期 YYYY-MM-DD
        images: 启用图片理解
        video: 启用视频理解

    返回搜索结果, 包含文本, 引用和元数据.
    """
    # 参数校验
    err = _validate_handles(handles, exclude)
    if err:
        return _error(prompt, err)
    err = _validate_dates(from_date, to_date)
    if err:
        return _error(prompt, err)

    # 构建 x_search tool config
    tool: dict = {"type": "x_search"}
    if handles:
        tool["allowed_x_handles"] = handles
    if exclude:
        tool["excluded_x_handles"] = exclude
    if from_date:
        tool["from_date"] = from_date
    if to_date:
        tool["to_date"] = to_date
    if images:
        tool["enable_image_understanding"] = True
    if video:
        tool["enable_video_understanding"] = True

    return _call_api([tool], prompt, "x_search")


@mcp.tool()
def x_read_tweet(url: str) -> dict:
    """读取指定的 X/Twitter 推文或线程.

    参数:
        url: X/Twitter 推文链接 (如 https://x.com/user/status/123456)

    返回推文内容, 回复线程和元数据.
    """
    # 解析 URL 提取用户名和推文 ID
    match = TWEET_URL_RE.search(url)
    if not match:
        return _error(
            url, f"无法解析推文链接: {url}. 格式应为 https://x.com/用户名/status/推文ID"
        )

    handle = match.group(1)
    tweet_id = match.group(2)

    # 构建 query 引导模型读取特定推文
    query = f"Read the full content and thread of this post: https://x.com/{handle}/status/{tweet_id}"

    # 使用 allowed_x_handles 精准定位用户
    tool = {
        "type": "x_search",
        "allowed_x_handles": [handle],
    }

    return _call_api([tool], query, "x_search")


@mcp.tool()
def x_web_search(
    prompt: str,
    allowed_domains: list[str] | None = None,
    excluded_domains: list[str] | None = None,
) -> dict:
    """使用 xAI 网页搜索工具搜索互联网.

    参数:
        prompt: 自然语言输入, 支持关键词/问题/语义描述等形式, Grok AI 处理后搜索网页并返回结构化结果
        allowed_domains: 仅搜索指定域名 (最多 5 个, 与 excluded_domains 互斥)
        excluded_domains: 排除指定域名 (最多 5 个, 与 allowed_domains 互斥)

    返回搜索结果, 包含文本, 引用和元数据.
    """
    # 参数校验
    err = _validate_domains(allowed_domains, excluded_domains)
    if err:
        return _error(prompt, err)

    # 构建 web_search tool config
    tool: dict = {"type": "web_search"}
    if allowed_domains:
        tool["allowed_domains"] = allowed_domains
    if excluded_domains:
        tool["excluded_domains"] = excluded_domains

    return _call_api([tool], prompt, "web_search")


# ── 入口 ──────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
