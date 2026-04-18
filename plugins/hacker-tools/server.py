#!/usr/bin/env python3
"""
黑客工具 MCP 服务器
封装了资产侦查和渗透相关的工具
"""

import os
import base64
from pathlib import Path
from typing import Any, Optional
import httpx
from fastmcp import FastMCP

# ── 配置加载 (从 ~/.claude/hacker-tools/.env) ──────────
STATE_DIR = Path(os.environ.get("HACKER_TOOLS_STATE_DIR", Path.home() / ".claude" / "hacker-tools"))
ENV_FILE = STATE_DIR / ".env"

if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.strip().partition("=")
            if os.environ.get(k) is None:
                os.environ[k] = v

mcp = FastMCP(name="hacker-tools")


def _parse_error(response: httpx.Response) -> str:
    """解析HTTP错误响应, 提取JSON中的具体错误信息"""
    raw = response.text[:500] if response.text else "(empty)"
    try:
        err = response.json()
        # Censys风格: {"errors": [{"message": "..."}]}
        msgs = [e.get("message", "") for e in err.get("errors", []) if e.get("message")]
        if msgs:
            return ", ".join(msgs)
        # 通用: {"detail": "..."} 或 {"error": "..."} 或 {"errmsg": "..."}
        for key in ("detail", "error", "errmsg", "message"):
            if err.get(key):
                return str(err[key])
    except Exception:
        pass
    return raw


# 创建一个自定义的 httpx 客户端,忽略 SSL 证书验证
def get_http_client(timeout: int = 10) -> httpx.AsyncClient:
    """创建忽略SSL证书验证的HTTP客户端"""
    return httpx.AsyncClient(
        timeout=timeout,
        verify=False,  # 忽略SSL证书验证
        follow_redirects=True,
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
    )


@mcp.tool()
async def fofa_search(
    domain: Optional[list[str]] = None, query: Optional[str] = None
) -> dict[str, Any]:
    """
    FOFA 网络空间测绘搜索引擎

    参数:
        domain: 主域名/顶级域名列表,例如: ["vc.sb"]
        query: 直接输入搜索语句,例如: 'domain="vc.sb"'

    返回:
        查询结果字典
    """
    try:
        key = os.getenv("FOFA_KEY")
        if not key:
            return {"error": True, "errmsg": "FOFA_KEY 环境变量未设置", "data": None}

        search_query = ""
        if query:
            search_query = query
        elif domain:
            search_query = " || ".join(domain)
        else:
            return {
                "error": True,
                "errmsg": "必须提供 domain 或 query 参数",
                "data": None,
            }

        qbase64 = base64.b64encode(search_query.encode()).decode()
        url = f"https://fofa.info/api/v1/search/all?key={key}&qbase64={qbase64}&page=1&full=true&r_type=json&size=100"

        async with get_http_client() as client:
            response = await client.get(url)

            if response.status_code != 200:
                return {"error": True, "errmsg": f"FOFA API {response.status_code}: {_parse_error(response)}", "data": None}

            return {"error": False, "data": response.json()}

    except httpx.TimeoutException:
        return {"error": True, "errmsg": "FOFA API 请求超时", "data": None}
    except Exception as e:
        return {"error": True, "errmsg": f"未知错误: {type(e).__name__}: {str(e) or repr(e)}", "data": None}


@mcp.tool()
async def hunter_search(
    query: str, page: int = 1, page_size: int = 100
) -> dict[str, Any]:
    """
    Hunter.how 网络空间测绘搜索引擎

    参数:
        query: 搜索语句,例如: 'ip="1.1.1.1"' 或 'domain="example.com"' 或 'web.body=""'
        page: 页码,默认 1
        page_size: 每页数量,默认 100

    返回:
        查询结果字典
    """
    try:
        api_key = os.getenv("HUNTER_HOW_API_KEY")
        if not api_key:
            return {
                "error": True,
                "errmsg": "HUNTER_HOW_API_KEY 环境变量未设置",
                "data": None,
            }

        # Hunter API只接受 10/20/50/100/1000
        valid_sizes = {10, 20, 50, 100, 1000}
        if page_size not in valid_sizes:
            page_size = min(valid_sizes, key=lambda x: abs(x - page_size))

        # query需要base64编码
        encoded_query = base64.urlsafe_b64encode(query.encode("utf-8")).decode("ascii")
        # 时间范围: 最近一年
        from datetime import datetime, timedelta

        end_time = datetime.now().strftime("%Y-%m-%d")
        start_time = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        # 返回字段
        fields = "ip,port,domain,protocol,web_title,country,province,city,url,as_org,status_code,product,updated_at"

        url = (
            f"https://api.hunter.how/search?"
            f"api-key={api_key}&query={encoded_query}&page={page}&page_size={page_size}"
            f"&start_time={start_time}&end_time={end_time}&fields={fields}"
        )

        async with get_http_client() as client:
            response = await client.get(url)

            if response.status_code != 200:
                return {"error": True, "errmsg": f"Hunter API {response.status_code}: {_parse_error(response)}", "data": None}

            return {"error": False, "data": response.json()}

    except httpx.TimeoutException:
        return {"error": True, "errmsg": "Hunter API 请求超时", "data": None}
    except Exception as e:
        return {"error": True, "errmsg": f"未知错误: {type(e).__name__}: {str(e) or repr(e)}", "data": None}


@mcp.tool()
async def censys_search(query: str) -> dict[str, Any]:
    """
    Censys 网络空间测绘搜索引擎 (Platform API v3)

    参数:
        query: CenQL 搜索语句, 例如: "host.name: example.com" 或 "host.services.port: 443"

    两种搜索方式:
        1. 全文本搜索: 直接用引号包裹关键词, 如 "example.com" 搜索所有记录
        2. 字段查询: 使用 host./web./cert. 前缀精确匹配

    常用字段:
        Host: host.ip, host.services.port, host.services.protocol, host.location.country,
              host.services.software.product, host.services.banner, host.autonomous_system.asn
        Web:  web.hostname, web.endpoints.http.body, web.endpoints.http.html_title
        Cert: cert.names, cert.parsed.subject.common_name

    语法示例:
        - "example.com"                                    (全文本搜索)
        - host.ip="1.1.1.1"                               (精确匹配)
        - host.services.port=443                          (端口过滤)
        - host.services:(port="22" and protocol="SSH")   (嵌套字段)
        - web.hostname: "example.com"                     (web属性)
        - host.services.scan_time > "now-1d"              (相对时间)

    返回:
        查询结果字典
    """
    try:
        token = os.getenv("CENSYS_TOKEN")
        org_id = os.getenv("CENSYS_ORGANIZATION_ID")

        if not token:
            return {"error": True, "errmsg": "CENSYS_TOKEN 环境变量未设置", "data": None}

        url = "https://api.platform.censys.io/v3/global/search/query"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if org_id:
            headers["X-Organization-ID"] = org_id

        data = {
            "page_size": 100,
            "query": query,
        }

        async with get_http_client() as client:
            response = await client.post(url, json=data, headers=headers)

            if response.status_code != 200:
                return {"error": True, "errmsg": f"Censys API {response.status_code}: {_parse_error(response)}", "data": None}

            return {"error": False, "data": response.json()}

    except httpx.TimeoutException:
        return {"error": True, "errmsg": "Censys API 请求超时", "data": None}
    except Exception as e:
        return {"error": True, "errmsg": f"未知错误: {type(e).__name__}: {str(e) or repr(e)}", "data": None}


@mcp.tool()
async def http_request(
    url: list[str],
    method: str = "GET",
    headers: Optional[dict[str, str]] = None,
    body: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    模拟真实浏览器访问网址的工具,如果 chrome-devtools 可用则优先使用

    参数:
        url: 要并发访问的网址数组,必须是 http(s):// 开头
        method: HTTP方法,可选 GET/POST/PUT/DELETE
        headers: 自定义请求头
        body: 请求体内容

    返回:
        响应结果列表
    """

    async def fetch_single_url(target_url: str) -> dict[str, Any]:
        try:
            default_headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Cache-Control": "max-age=0",
            }

            if headers:
                default_headers.update(headers)

            async with get_http_client() as client:
                if method.upper() == "GET":
                    response = await client.get(target_url, headers=default_headers)
                elif method.upper() == "POST":
                    response = await client.post(
                        target_url, headers=default_headers, content=body
                    )
                elif method.upper() == "PUT":
                    response = await client.put(
                        target_url, headers=default_headers, content=body
                    )
                elif method.upper() == "DELETE":
                    response = await client.delete(target_url, headers=default_headers)
                else:
                    return {
                        "status": 0,
                        "headers": {},
                        "body": f"不支持的HTTP方法: {method}",
                        "url": target_url,
                        "originalUrl": target_url,
                    }

                response_body = response.text
                response_headers = dict(response.headers)

                return {
                    "status": response.status_code,
                    "headers": response_headers,
                    "body": response_body,
                    "url": str(response.url),
                    "originalUrl": target_url,
                }

        except httpx.TimeoutException:
            return {
                "status": 0,
                "headers": {},
                "body": f"错误: 请求超时 - {target_url}",
                "url": target_url,
                "originalUrl": target_url,
            }
        except Exception as e:
            return {
                "status": 0,
                "headers": {},
                "body": f"错误: {str(e)}",
                "url": target_url,
                "originalUrl": target_url,
            }

    # 并发访问多个URL
    import asyncio

    tasks = [fetch_single_url(single_url) for single_url in url]
    results = await asyncio.gather(*tasks)
    return results


@mcp.tool()
async def nvd_search(
    keyword: Optional[str] = None,
    cpe_name: Optional[str] = None,
    severity: Optional[str] = None,
    results_per_page: int = 20,
) -> dict[str, Any]:
    """
    NVD (National Vulnerability Database) CVE 漏洞搜索工具

    默认返回最新的漏洞(按发布日期降序)

    参数:
        keyword: 搜索关键字(搜索描述文本),例如 "rce", "xss", "sql injection"
        cpe_name: CPE名称(搜索产品配置),例如 "vercel:next.js" 或 "cpe:2.3:a:vercel:next.js"
        severity: 可选,按严重程度过滤: LOW/MEDIUM/HIGH/CRITICAL
        results_per_page: 每页结果数,默认 20,最大 100

    推荐: 只使用 cpe_name 搜索产品漏洞
        - cpe_name 搜索 CPE 配置,结果最精确
        - keyword 只搜索描述文本,可能遗漏重要 CVE
        - 示例: nvd_search(cpe_name="vercel:next.js", severity="CRITICAL")

    如何找到正确的 cpe_name:
        1. 访问 https://nvd.nist.gov/products/cpe/search 搜索产品
        2. 或查询 CPE API: https://services.nvd.nist.gov/rest/json/cpes/2.0?keywordSearch=next.js
        3. 从返回的 cpeName 中提取 vendor:product,例如 "vercel:next.js"
        4. 注意: 同一产品可能有多个 vendor (如 next.js 有 vercel 和 zeit)

    返回:
        {
            "error": false,
            "data": {
                "totalResults": 总数,
                "uniqueResults": 去重后数量,
                "vulnerabilities": [...]
            }
        }
    """
    try:
        if not keyword and not cpe_name:
            return {"error": True, "errmsg": "必须提供 keyword 或 cpe_name 参数", "data": None}

        api_key = os.getenv("CVE_API_KEY")
        results_per_page = min(results_per_page, 100)

        base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        params = []

        if keyword:
            params.append(f"keywordSearch={keyword}")

        if cpe_name:
            # 支持简写: "vercel:next.js" -> "cpe:2.3:a:vercel:next.js"
            if not cpe_name.startswith("cpe:"):
                cpe_name = f"cpe:2.3:a:{cpe_name}"
            params.append(f"virtualMatchString={cpe_name}")

        if severity and severity.upper() in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            params.append(f"cvssV3Severity={severity.upper()}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        if api_key:
            headers["apiKey"] = api_key

        async with get_http_client(timeout=30) as client:
            # 第一次请求获取总数
            url = f"{base_url}?{'&'.join(params)}&resultsPerPage=1"
            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                return {"error": True, "errmsg": f"NVD API {response.status_code}: {_parse_error(response)}", "data": None}

            total_results = response.json().get("totalResults", 0)
            if total_results == 0:
                return {"error": False, "data": {"totalResults": 0, "uniqueResults": 0, "vulnerabilities": []}}

            # 计算最后一页的 startIndex (获取最新漏洞)
            start_index = max(0, total_results - results_per_page)

            # 第二次请求获取最新数据
            url = f"{base_url}?{'&'.join(params)}&resultsPerPage={results_per_page}&startIndex={start_index}"
            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                return {"error": True, "errmsg": f"NVD API {response.status_code}: {_parse_error(response)}", "data": None}

            raw_data = response.json()

            # 精简返回数据,并反转为降序
            vulnerabilities = []
            for item in raw_data.get("vulnerabilities", []):
                cve = item.get("cve", {})

                # 提取 CVSS 分数
                cvss_score = None
                cvss_severity = None
                metrics = cve.get("metrics", {})
                if "cvssMetricV31" in metrics and metrics["cvssMetricV31"]:
                    cvss_data = metrics["cvssMetricV31"][0].get("cvssData", {})
                    cvss_score = cvss_data.get("baseScore")
                    cvss_severity = cvss_data.get("baseSeverity")
                elif "cvssMetricV30" in metrics and metrics["cvssMetricV30"]:
                    cvss_data = metrics["cvssMetricV30"][0].get("cvssData", {})
                    cvss_score = cvss_data.get("baseScore")
                    cvss_severity = cvss_data.get("baseSeverity")

                # 提取描述
                descriptions = cve.get("descriptions", [])
                description = ""
                for desc in descriptions:
                    if desc.get("lang") == "en":
                        description = desc.get("value", "")
                        break

                vulnerabilities.append(
                    {
                        "cveId": cve.get("id"),
                        "description": description,
                        "cvssScore": cvss_score,
                        "severity": cvss_severity,
                        "published": cve.get("published"),
                        "lastModified": cve.get("lastModified"),
                        "url": f"https://nvd.nist.gov/vuln/detail/{cve.get('id')}",
                    }
                )

            # 反转列表,让最新漏洞排在最前面
            vulnerabilities.reverse()

            return {
                "error": False,
                "data": {
                    "totalResults": raw_data.get("totalResults", 0),
                    "uniqueResults": len(vulnerabilities),
                    "resultsPerPage": len(vulnerabilities),
                    "vulnerabilities": vulnerabilities,
                },
            }

    except httpx.TimeoutException:
        return {"error": True, "errmsg": "NVD API 请求超时", "data": None}
    except Exception as e:
        return {"error": True, "errmsg": f"未知错误: {type(e).__name__}: {str(e) or repr(e)}", "data": None}


@mcp.tool()
async def nvd_get_cve(cve_id: str) -> dict[str, Any]:
    """
    NVD 获取单个 CVE 详情

    参数:
        cve_id: CVE ID,例如 "CVE-2024-1234"

    返回:
        CVE 详细信息
    """
    try:
        api_key = os.getenv("CVE_API_KEY")

        base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        url = f"{base_url}?cveId={cve_id}"

        # API Key 通过请求头传递
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        if api_key:
            headers["apiKey"] = api_key

        async with get_http_client(timeout=30) as client:
            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                return {"error": True, "errmsg": f"NVD API {response.status_code}: {_parse_error(response)}", "data": None}

            return {"error": False, "data": response.json()}

    except Exception as e:
        return {"error": True, "errmsg": f"未知错误: {type(e).__name__}: {str(e) or repr(e)}", "data": None}


@mcp.tool()
async def dnsdumpster_query(domain: str) -> dict[str, Any]:
    """
    DNSDumpster.com 域名信息查询工具

    参数:
        domain: 域名,例如 "a.com"

    返回:
        域名信息查询结果
    """
    try:
        api_key = os.getenv("DNSDUMPSTER_API_KEY")
        if not api_key:
            return {
                "error": True,
                "errmsg": "DNSDUMPSTER_API_KEY 环境变量未设置",
                "data": None,
            }

        url = f"https://api.dnsdumpster.com/domain/{domain}"
        headers = {"X-API-Key": api_key}

        async with get_http_client() as client:
            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                return {
                    "error": True,
                    "errmsg": f"DNSDumpster API {response.status_code}: {_parse_error(response)}",
                    "data": None,
                }

            return {"error": False, "data": response.json()}

    except httpx.TimeoutException:
        return {"error": True, "errmsg": "DNSDumpster API 请求超时", "data": None}
    except Exception as e:
        return {"error": True, "errmsg": f"未知错误: {type(e).__name__}: {str(e) or repr(e)}", "data": None}


@mcp.tool()
async def virustotal_query(domain: str) -> dict[str, Any]:
    """
    VirusTotal 域名信息查询工具

    参数:
        domain: 域名,例如 "a.com"

    返回:
        域名安全信息查询结果
    """
    try:
        api_key = os.getenv("VIRUSTOTAL_API_KEY")
        if not api_key:
            return {
                "error": True,
                "errmsg": "VIRUSTOTAL_API_KEY 环境变量未设置",
                "data": None,
            }

        url = f"https://www.virustotal.com/api/v3/domains/{domain}"
        headers = {"accept": "application/json", "x-apikey": api_key}

        async with get_http_client() as client:
            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                return {
                    "error": True,
                    "errmsg": f"VirusTotal API {response.status_code}: {_parse_error(response)}",
                    "data": None,
                }

            return {"error": False, "data": response.json()}

    except httpx.TimeoutException:
        return {"error": True, "errmsg": "VirusTotal API 请求超时", "data": None}
    except Exception as e:
        return {"error": True, "errmsg": f"未知错误: {type(e).__name__}: {str(e) or repr(e)}", "data": None}


# TODO 得更换其他的ip查询工具
@mcp.tool()
async def ip_query(
    ip: Optional[str] = None, query: Optional[str] = None
) -> dict[str, Any]:
    """
    IP地理位置查询工具

    参数:
        ip: IP地址,例如 "185.222.222.222"
        query: 兼容性参数,同 ip

    返回:
        IP地理位置信息
    """
    try:
        target_ip = ip or query
        if not target_ip:
            return {"error": True, "errmsg": "必须提供 ip 或 query 参数", "data": None}

        url = f"http://ip-api.com/json/{target_ip}"
        headers = {
            "accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        }

        async with get_http_client() as client:
            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                return {
                    "error": True,
                    "errmsg": f"IP API {response.status_code}: {_parse_error(response)}",
                    "data": None,
                }

            return {"error": False, "data": response.json()}

    except httpx.TimeoutException:
        return {"error": True, "errmsg": "IP API 请求超时", "data": None}
    except Exception as e:
        return {"error": True, "errmsg": f"未知错误: {type(e).__name__}: {str(e) or repr(e)}", "data": None}


if __name__ == "__main__":
    # 运行 MCP 服务器
    mcp.run()
