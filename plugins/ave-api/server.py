#!/usr/bin/env python3
"""Ave.ai MCP Server - 代币收录数据查询"""

import base64
import json
import os
import subprocess
import urllib.parse
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

# ── 常量 ──────────────────────────────────────────────
BASE_URL = "https://nkdoym.com/v1api"
TIMEOUT_S = 30
STATE_DIR = Path(os.environ.get("AVE_STATE_DIR", Path.home() / ".claude" / "ave"))
ENV_FILE = STATE_DIR / ".env"
CHAINS = ["bsc", "eth", "solana", "base", "arbitrum", "polygon", "optimism", "avalanche", "fantom"]

INSTRUCTIONS = """查询代币数据时, 必须完整展示以下字段, 禁止省略/截断/隐藏:
- 合约地址: 显示完整地址, 禁止缩写
- 官网/Website/X(Twitter)/Telegram: 有则必显
- TVL/价格/涨跌幅/持有人数/风险分: 默认显示
- 项目介绍(intro_cn): 有则必显(不准修饰,确保原样输出)
- 买卖税: 代币详情时显示
表格列顺序: 代币名/合约地址/价格/涨跌幅/TVL/持有人/风险/官网/X/TG/介绍"""

mcp = FastMCP("ave-api", instructions=INSTRUCTIONS)

# ── Token 加载 (从 .env 文件) ──────────────────────────

# 加载 .env
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.strip().partition("=")
            if os.environ.get(k) is None:
                os.environ[k] = v

AVE_TOKEN = os.environ.get("AVE_TOKEN", "")


def _get_headers() -> dict[str, str]:
    headers = {"lang": "cn", "Content-Type": "application/json"}
    if AVE_TOKEN:
        headers["X-Auth"] = AVE_TOKEN
    return headers


# ── 响应解码 (对齐 ave.py) ────────────────────────────


def _decode(data: dict):
    """解码 encode_data 格式, 返回解码后的 data"""
    if data.get("data_type") == 2 and data.get("encode_data"):
        try:
            raw = base64.b64decode(data["encode_data"]).decode()
            decoded = urllib.parse.unquote(raw)
            return json.loads(decoded)
        except Exception:
            pass
    return data.get("data", data)


# ── HTTP 请求 ──────────────────────────────────────────


def _request_raw(path: str, params: dict | None = None) -> dict:
    """发送 GET 请求 (不要求 token)"""
    url = f"{BASE_URL}{path}"
    headers = {"lang": "cn", "Content-Type": "application/json"}
    if AVE_TOKEN:
        headers["X-Auth"] = AVE_TOKEN
    try:
        with httpx.Client(timeout=TIMEOUT_S) as client:
            resp = client.get(url, headers=headers, params=params)
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": f"请求失败: {e}"}


def _request(path: str, params: dict | None = None) -> dict | list:
    """发送 GET 请求到 Ave API"""
    if not AVE_TOKEN:
        return {"status": "error", "message": "未设置 AVE_TOKEN. 请在 ~/.claude/ave/.env 中设置 AVE_TOKEN=xxx"}

    url = f"{BASE_URL}{path}"
    try:
        with httpx.Client(timeout=TIMEOUT_S) as client:
            resp = client.get(url, headers=_get_headers(), params=params)
        result = resp.json()
    except httpx.TimeoutException:
        return {"status": "error", "message": f"请求超时 ({TIMEOUT_S}s)"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "响应 JSON 解析失败"}
    except Exception as e:
        return {"status": "error", "message": f"请求失败: {e}"}

    if isinstance(result, dict) and result.get("status") == 10001:
        return {"status": "error", "message": "Token 已过期, 请更新 ~/.claude/ave/.env 中的 AVE_TOKEN"}

    # 对齐 ave.py: data_type==2 时 decode, 否则取 data
    decoded = _decode(result)
    return decoded


def _parse_appendix(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def _fmt(item: dict) -> dict:
    """格式化单个代币"""
    a = _parse_appendix(item.get("appendix"))
    return {k: v for k, v in {
        "symbol": item.get("symbol_en") or item.get("symbol") or item.get("token0_symbol", ""),
        "name_zh": item.get("name_zh", ""),
        "chain": item.get("chain", ""),
        "contract": item.get("target_token") or item.get("token") or item.get("address", ""),
        "pair": item.get("pair", ""),
        "price_usd": item.get("current_price_usd"),
        "price_change": item.get("price_change_24h") or item.get("price_change"),
        "tvl": item.get("tvl") or item.get("main_pair_tvl") or item.get("pool_size"),
        "holders": item.get("holders"),
        "risk_score": item.get("risk_score"),
        "buy_tax": item.get("buy_tax"),
        "sell_tax": item.get("sell_tax"),
        "intro_cn": item.get("intro_cn", ""),
        "website": a.get("website", ""),
        "twitter": a.get("twitter", ""),
        "telegram": a.get("telegram", ""),
    }.items() if v is not None and v != ""}


def _fetch_intro(contract: str, chain: str) -> str:
    """请求详情接口获取 intro_cn"""
    try:
        data = _request(f"/v3/tokens/{contract}-{chain}")
        if isinstance(data, dict) and not data.get("status") == "error":
            t = data.get("token", data) if isinstance(data, dict) else {}
            return t.get("intro_cn", "")
    except Exception:
        pass
    return ""


# ── MCP 工具 ──────────────────────────────────────────


@mcp.tool()
def ave_new_tokens(chain: str = "bsc", page: int = 1, page_size: int = 10) -> dict:
    """查询最新收录的代币列表.

    参数:
        chain: 链名称 (bsc/eth/solana/base/arbitrum/polygon/optimism/avalanche/fantom)
        page: 页码
        page_size: 每页数量 (1-50)

    返回新收录代币的合约地址/pair/网址/介绍等信息.
    """
    if chain not in CHAINS:
        return {"status": "error", "message": f"不支持的链: {chain}. 支持: {', '.join(CHAINS)}"}

    data = _request("/v4/tokens/treasure/list", params={
        "chain": chain, "category": "inclusion",
        "sort": "target_listing_at", "sort_dir": "desc",
        "pageNO": page, "pageSize": min(page_size, 50),
    })

    if isinstance(data, dict) and data.get("status") == "error":
        return data

    items = data.get("data", []) if isinstance(data, dict) else []
    total = data.get("total", 0) if isinstance(data, dict) else 0

    # 列表接口不含 intro, 逐条请求详情补充
    tokens = []
    for item in items:
        t = _fmt(item)
        contract = t.get("contract", "")
        if contract and not t.get("intro_cn"):
            intro = _fetch_intro(contract, chain)
            if intro:
                t["intro_cn"] = intro
        tokens.append(t)

    return {
        "status": "ok", "chain": chain, "total": total,
        "page": page, "count": len(tokens),
        "tokens": tokens,
    }


@mcp.tool()
def ave_token_info(address: str, chain: str = "bsc") -> dict:
    """查询代币详情 (官网/TG/推特/介绍/税/风险/总量等).

    参数:
        address: 代币合约地址
        chain: 链名称 (bsc/eth/solana/base/arbitrum/polygon/optimism/avalanche/fantom)

    返回完整的代币详情信息.
    """
    if chain not in CHAINS:
        return {"status": "error", "message": f"不支持的链: {chain}. 支持: {', '.join(CHAINS)}"}

    data = _request(f"/v3/tokens/{address}-{chain}")

    if isinstance(data, dict) and data.get("status") == "error":
        return data

    t = data.get("token", data) if isinstance(data, dict) else {}
    if not t:
        return {"status": "error", "message": "未找到代币信息"}

    a = _parse_appendix(t.get("appendix"))
    return {"status": "ok", "token": {k: v for k, v in {
        "symbol": t.get("symbol", ""), "name": t.get("name", ""),
        "chain": chain, "contract": address,
        "price_usd": t.get("current_price_usd"),
        "price_change": t.get("price_change"),
        "tvl": t.get("main_pair_tvl"), "holders": t.get("holders"),
        "risk_score": t.get("risk_score"),
        "buy_tax": t.get("buy_tax"), "sell_tax": t.get("sell_tax"),
        "total_supply": t.get("total"), "burn_amount": t.get("burn_amount_dec"),
        "launchpad": t.get("launchpad", ""),
        "intro_cn": t.get("intro_cn", ""), "intro_en": t.get("intro_en", ""),
        "website": a.get("website", ""), "twitter": a.get("twitter", ""),
        "telegram": a.get("telegram", ""), "discord": a.get("discord", ""),
        "github": a.get("github", ""), "whitepaper": a.get("whitepaper", ""),
        "pairs": t.get("pairs", []),
    }.items() if v is not None and v != ""}}


@mcp.tool()
def ave_hot_tokens() -> dict:
    """查询热门代币列表."""
    data = _request("/v2/tokens/hot")
    if isinstance(data, dict) and data.get("status") == "error":
        return data
    items = data if isinstance(data, list) else []
    return {"status": "ok", "count": len(items), "tokens": [_fmt(t) for t in items]}


@mcp.tool()
def ave_gainers() -> dict:
    """查询涨幅榜."""
    data = _request("/v2/tokens/priceChange")
    if isinstance(data, dict) and data.get("status") == "error":
        return data
    items = data if isinstance(data, list) else []
    return {"status": "ok", "count": len(items), "tokens": [_fmt(t) for t in items]}


@mcp.tool()
def ave_search(keyword: str) -> dict:
    """搜索代币.

    参数:
        keyword: 搜索关键词 (代币名称/符号/合约地址)

    返回匹配的代币列表.
    """
    data = _request("/v2/tokens/query", params={"keyword": keyword})
    if isinstance(data, dict) and data.get("status") == "error":
        return data
    items = data if isinstance(data, list) else []
    return {"status": "ok", "keyword": keyword, "count": len(items), "tokens": [_fmt(t) for t in items]}


@mcp.tool()
def ave_contract_info(token_id: str) -> dict:
    """查询代币合约审计信息.

    参数:
        token_id: 代币 ID (从列表接口获取)

    返回合约安全审计结果.
    """
    data = _request("/v2/tokens/contract", params={"token_id": token_id, "type": "token", "user_address": ""})
    if isinstance(data, dict) and data.get("status") == "error":
        return data
    return {"status": "ok", "data": data}


@mcp.tool()
def ave_get_captcha() -> dict:
    """获取验证码图片. 返回图片路径和 captcha id, 用户识别后调用 ave_verify_captcha 提交答案."""
    raw = _request_raw("/v1/captcha/getCaptcha")
    if isinstance(raw, dict) and raw.get("status") == "error":
        return raw
    result = _decode(raw)
    if not isinstance(result, dict) or "id" not in result:
        return {"status": "error", "message": "获取验证码失败"}
    captcha_id = result["id"]
    img_data = result.get("image", "")
    if img_data.startswith("data:image/png;base64,"):
        img_bytes = base64.b64decode(img_data.split(",")[1])
        img_path = f"/tmp/ave_captcha_{captcha_id[:8]}.png"
        Path(img_path).write_bytes(img_bytes)
        subprocess.run(["open", img_path], check=False)  # 自动打开图片供用户查看
    else:
        return {"status": "error", "message": "验证码图片格式异常"}
    return {"status": "ok", "captcha_id": captcha_id, "image_path": img_path}


@mcp.tool()
def ave_verify_captcha(captcha_id: str, answer: str) -> dict:
    """提交验证码答案, 获取 ave_token.

    参数:
        captcha_id: 从 ave_get_captcha 返回的 captcha_id
        answer: 验证码图片中的数学答案

    返回 ave_token 字符串, 用户需手动更新到 ~/.claude/ave/.env
    """
    with httpx.Client(timeout=TIMEOUT_S) as client:
        resp = client.post(
            f"{BASE_URL}/v1/captcha/verifyCaptcha",
            headers={"lang": "cn", "Content-Type": "application/json"},
            json={"id": captcha_id, "value": answer},
        )
    result = resp.json()
    decoded = _decode(result)
    if not isinstance(decoded, dict) or not decoded.get("is_verified"):
        return {"status": "error", "message": "验证失败", "raw": decoded}
    return {
        "status": "ok",
        "ave_token": decoded["ave_token"],
        "hint": "请手动更新 ~/.claude/ave/.env 中的 AVE_TOKEN",
    }


# ── 入口 ──────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
