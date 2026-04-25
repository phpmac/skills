# Ave.ai API 参考

域名: `api.avegac.com` (官方) / `nkdoym.com` (MCP代理)
前缀: `/v1api`
认证: `X-Auth` 请求头, 值为 51 位 hex, 存储在 `~/.claude/ave/.env` 的 `AVE_TOKEN=`
支持链: bsc/eth/solana/base/arbitrum/polygon/optimism/avalanche/fantom

## 响应解码

data_type=2 时: base64 decode -> URL decode -> JSON parse

```python
# 一行解码
decoded = json.loads(urllib.parse.unquote(base64.b64decode(data["encode_data"]).decode()))
```

## 认证 (无需 X-Auth)

```bash
# 1. 获取验证码图片 (返回 data_type=2 编码, 解码后 {id, image})
curl -s 'https://api.avegac.com/v1api/v1/captcha/getCaptcha' \
  -H 'lang: cn' -H 'Content-Type: application/json'

# 2. 人眼识别答案后提交 (id 就是未来的 token, 需激活)
curl -s 'https://api.avegac.com/v1api/v1/captcha/verifyCaptcha' \
  -X POST -H 'lang: cn' -H 'Content-Type: application/json' \
  -d '{"id":"<captcha_id>","value":"<答案>"}'
# 返回 data_type=2: {ave_token: "51位hex", is_verified: true}
```

## API 端点 (均需 X-Auth)

```bash
# 热门代币 (直接返回数组)
curl -s 'https://api.avegac.com/v1api/v2/tokens/hot' \
  -H 'lang: cn' -H 'X-Auth: <token>'

# 涨幅榜 (data_type=2 编码数组)
curl -s 'https://api.avegac.com/v1api/v2/tokens/priceChange' \
  -H 'lang: cn' -H 'X-Auth: <token>'

# 搜索 (返回 {token_list: [...]}, appendix 字段是 JSON 字符串需二次解析)
curl -s 'https://api.avegac.com/v1api/v2/tokens/query?keyword=PEPE' \
  -H 'lang: cn' -H 'X-Auth: <token>'

# 最新收录 (category=inclusion)
curl -s 'https://api.avegac.com/v1api/v4/tokens/treasure/list?chain=bsc&category=inclusion&sort=target_listing_at&sort_dir=desc&pageNO=1&pageSize=10' \
  -H 'lang: cn' -H 'X-Auth: <token>'

# 代币详情 (含 buy_tax/sell_tax/risk_score/intro_cn/appendix)
curl -s 'https://api.avegac.com/v1api/v3/tokens/<address>-<chain>' \
  -H 'lang: cn' -H 'X-Auth: <token>'

# 合约审计
curl -s 'https://api.avegac.com/v1api/v2/tokens/contract?token_id=<id>&type=token&user_address=' \
  -H 'lang: cn' -H 'X-Auth: <token>'
```

## 错误码

| status | 含义 |
|--------|------|
| 1 | 成功 |
| 10001 | Token 过期 |
| 0 | 失败, 看 msg |
