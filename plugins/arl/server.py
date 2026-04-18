#!/usr/bin/env python3
"""ARL资产侦察灯塔 MCP Server - 从 ~/.claude/arl/.env 读取配置"""

import os
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

# ── 配置加载 ──────────────────────────────────────────
STATE_DIR = Path(os.environ.get("ARL_STATE_DIR", Path.home() / ".claude" / "arl"))
ENV_FILE = STATE_DIR / ".env"

if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.strip().partition("=")
            if os.environ.get(k) is None:
                os.environ[k] = v

ARL_URL = os.environ.get("ARL_URL", "").rstrip("/")
ARL_TOKEN = os.environ.get("ARL_TOKEN", "")
TIMEOUT_S = 30

# ── MCP Server ────────────────────────────────────────
INSTRUCTIONS = """ARL资产侦察灯塔操作专家. 核心规则:
1. [强制] 必须使用策略提交任务, 禁止直接配置参数
2. [强制] 提交后记录task_id并告知用户稍后查询
3. [强制] size参数不超过100, 防止系统崩溃
4. 遇到 Too many requests 立即停止"""

mcp = FastMCP("arl", instructions=INSTRUCTIONS)


def _headers() -> dict:
    return {"Token": ARL_TOKEN, "Content-Type": "application/json"}


def _check():
    if not ARL_URL or not ARL_TOKEN:
        return "错误: ARL未配置, 请在 ~/.claude/arl/.env 中设置 ARL_URL 和 ARL_TOKEN"
    return None


# ── 查询工具 ──────────────────────────────────────────

@mcp.tool()
async def get_tasks(
    name: str | None = None, target: str | None = None,
    status: str | None = None, task_id: str | None = None,
    task_tag: str | None = None,
    page: int = 1, size: int = 10, order: str = "-_id",
) -> str:
    """查询ARL任务列表"""
    if e := _check(): return e
    params = {k: v for k, v in locals().items() if v is not None and k not in ("e",)}
    # MCP参数名映射到ARL API参数名
    if "task_id" in params:
        params["_id"] = params.pop("task_id")
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as c:
        r = await c.get(f"{ARL_URL}/api/task/", headers=_headers(), params=params)
        return r.text


@mcp.tool()
async def get_policies(
    name: str | None = None, policy_id: str | None = None,
    page: int = 1, size: int = 10, order: str = "-_id",
) -> str:
    """查询ARL策略列表"""
    if e := _check(): return e
    params = {k: v for k, v in locals().items() if v is not None and k not in ("e",)}
    if "policy_id" in params:
        params["_id"] = params.pop("policy_id")
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as c:
        r = await c.get(f"{ARL_URL}/api/policy/", headers=_headers(), params=params)
        return r.text


@mcp.tool()
async def get_sites(
    site: str | None = None, hostname: str | None = None,
    ip: str | None = None, title: str | None = None,
    http_server: str | None = None, headers: str | None = None,
    finger_name: str | None = None, status: int | None = None,
    favicon_hash: int | None = None, task_id: str | None = None,
    tag: str | None = None,
    page: int = 1, size: int = 10, order: str = "-_id",
) -> str:
    """查询ARL站点信息"""
    if e := _check(): return e
    params = {k: v for k, v in locals().items() if v is not None and k not in ("e",)}
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as c:
        r = await c.get(f"{ARL_URL}/api/site/", headers=_headers(), params=params)
        return r.text


@mcp.tool()
async def get_domains(
    domain: str | None = None, record: str | None = None,
    type: str | None = None, ips: str | None = None,
    source: str | None = None, task_id: str | None = None,
    page: int = 1, size: int = 10, order: str = "-_id",
) -> str:
    """查询ARL域名信息"""
    if e := _check(): return e
    params = {k: v for k, v in locals().items() if v is not None and k not in ("e",)}
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as c:
        r = await c.get(f"{ARL_URL}/api/domain/", headers=_headers(), params=params)
        return r.text


@mcp.tool()
async def get_ips(
    ip: str | None = None, domain: str | None = None,
    port_id: int | None = None, service_name: str | None = None,
    version: str | None = None, product: str | None = None,
    os_name: str | None = None, task_id: str | None = None,
    ip_type: str | None = None, cdn_name: str | None = None,
    asn_number: int | None = None, asn_org: str | None = None,
    region_name: str | None = None,
    page: int = 1, size: int = 10, order: str = "-_id",
) -> str:
    """查询ARL IP信息"""
    if e := _check(): return e
    params = {k: v for k, v in locals().items() if v is not None and k not in ("e",)}
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as c:
        r = await c.get(f"{ARL_URL}/api/ip/", headers=_headers(), params=params)
        return r.text


@mcp.tool()
async def get_wihs(
    task_id: str | None = None, content: str | None = None,
    record_type: str | None = None,
    page: int = 1, size: int = 10, order: str = "-_id",
) -> str:
    """查询ARL WIH敏感信息"""
    if e := _check(): return e
    params = {k: v for k, v in locals().items() if v is not None and k not in ("e",)}
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as c:
        r = await c.get(f"{ARL_URL}/api/wih/", headers=_headers(), params=params)
        return r.text


# ── 任务操作 ──────────────────────────────────────────

@mcp.tool()
async def add_task(
    name: str, target: str,
    domain_brute: bool = True, port_scan: bool = True,
    port_scan_type: str = "test", domain_brute_type: str = "test",
    service_detection: bool = False, service_brute: bool = False,
    os_detection: bool = False, site_identify: bool = False,
    site_capture: bool = False, file_leak: bool = False,
    search_engines: bool = False, site_spider: bool = False,
    arl_search: bool = False, alt_dns: bool = False,
    ssl_cert: bool = False, dns_query_plugin: bool = False,
    skip_scan_cdn_ip: bool = False, nuclei_scan: bool = False,
    findvhost: bool = False, web_info_hunter: bool = False,
) -> str:
    """添加ARL扫描任务(直接参数模式)"""
    if e := _check(): return e
    body = {k: v for k, v in locals().items() if v is not None and k != "e"}
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as c:
        r = await c.post(f"{ARL_URL}/api/task/", headers=_headers(), json=body)
        return r.text


@mcp.tool()
async def task_by_policy(
    name: str, task_tag: str, policy_id: str,
    target: str | None = None, result_set_id: str | None = None,
) -> str:
    """通过策略添加ARL扫描任务"""
    if e := _check(): return e
    body = {k: v for k, v in locals().items() if v is not None and k != "e"}
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as c:
        r = await c.post(f"{ARL_URL}/api/task/policy/", headers=_headers(), json=body)
        return r.text


@mcp.tool()
async def restart_tasks(
    task_id: list[str], del_old_task: bool | None = None,
    del_task_data: bool = False,
) -> str:
    """按任务ID重启ARL任务"""
    if e := _check(): return e
    body: dict = {"task_id": task_id, "del_task_data": del_task_data}
    if del_old_task is not None:
        body["del_old_task"] = del_old_task
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as c:
        r = await c.post(f"{ARL_URL}/api/task/restart/", headers=_headers(), json=body)
        return r.text


@mcp.tool()
async def restart_tasks_by_status(
    status: str, limit: int = 100,
    del_old_task: bool = True, del_task_data: bool = False,
) -> str:
    """按状态批量重启ARL任务"""
    if e := _check(): return e
    body = {"status": status, "limit": limit, "del_old_task": del_old_task, "del_task_data": del_task_data}
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as c:
        r = await c.post(f"{ARL_URL}/api/task/restart/by_status/", headers=_headers(), json=body)
        return r.text


if __name__ == "__main__":
    mcp.run()
