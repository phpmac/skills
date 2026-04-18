---
name: ave-api
description: Ave.ai 代币收录数据查询与监控. 当需要查询新收录代币/代币详情/热门代币/涨幅榜/监控新币收录, 或用户提到ave/收录/新币/代币信息时使用. 支持合约地址/pair/官网/TG/推特/项目介绍.
allowed-tools: Bash
---

# Ave.ai 代币数据查询

脚本: `ave.py` (项目根目录), 使用 `uv run ave.py` 执行.

## 前置: Token

Token文件: `.ave_token` (自动管理).
过期需重新登录: `uv run ave.py login`

## 操作指令

```
uv run ave.py login                         # 获取token (解验证码)
uv run ave.py new [-n 10] [--chain bsc]     # 最新收录 (合约/pair/网址/介绍)
uv run ave.py hot                           # 热门代币
uv run ave.py gainer                        # 涨幅榜
uv run ave.py info <合约地址> [--chain bsc]  # 代币详情 (官网/TG/推特/介绍/税/风险)
uv run ave.py watch [-i 30] [--chain bsc]   # 持续监控新收录
uv run ave.py token                         # 检查token状态
```

## API 参考

### 域名与认证

- 域名: `nkdoym.com` (ave.ai) / `dryespah.com` (avebusiness.xyz)
- Header: `X-Auth: <50位hex ave_token>`
- 获取流程: getCaptcha → 解题 → verifyCaptcha → token
- 响应编码: `encode_data` = `base64(urlencode(JSON))`, 解码: `JSON.parse(decodeURIComponent(atob(x)))`

### encode_data 解码方法

服务端返回格式:
```json
{"status": 1, "data_type": 2, "encode_data": "eyJhbG...base64..."}
```

解码步骤 (Python):
```python
import base64, json, urllib.parse
raw = base64.b64decode(encode_data).decode()       # URL编码的JSON字符串
decoded = urllib.parse.unquote(raw)                  # 解码URL编码
data = json.loads(decoded)                           # 得到实际JSON
```

解码步骤 (JS):
```javascript
JSON.parse(decodeURIComponent(atob(encode_data)))
```

---

### 收录接口 (HTTP)

#### 1. 获取验证码

```bash
curl -s 'https://nkdoym.com/v1api/v1/captcha/getCaptcha' \
  -H 'lang: cn' \
  -H 'Content-Type: application/json'
```

响应:
```json
{
  "status": 1,
  "data_type": 2,
  "encode_data": "<base64>"
}
```

解码后:
```json
{
  "id": "验证码ID",
  "captcha": "data:image/png;base64,<图片base64>"
}
```

#### 2. 验证验证码获取Token

```bash
curl -s -X POST 'https://nkdoym.com/v1api/v1/captcha/verifyCaptcha' \
  -H 'lang: cn' \
  -H 'Content-Type: application/json' \
  -d '{"id": "<验证码ID>", "value": "<用户输入的答案>"}'
```

响应 (解码后):
```json
{
  "ave_token": "36a6f35d683330259a0ebc017d2b3a791776275805100477730"
}
```

Token 用于后续所有请求的 `X-Auth` header.

#### 3. 收录列表

```bash
curl -s 'https://nkdoym.com/v1api/v4/tokens/treasure/list?chain=bsc&category=inclusion&sort=target_listing_at&sort_dir=desc&pageNO=1&pageSize=10' \
  -H 'lang: cn' \
  -H 'X-Auth: <token>' \
  -H 'Content-Type: application/json'
```

参数:

| 参数 | 值 | 说明 |
|------|-----|------|
| chain | bsc/eth/solana/base/arbitrum/polygon/optimism/avalanche/fantom | 链 |
| category | inclusion | 收录类型 |
| sort | target_listing_at | 按收录时间排序 |
| sort_dir | desc | 降序 |
| pageNO | 1 | 页码 |
| pageSize | 50 | 每页数量 (BSC总量约2501) |

响应:
```json
{
  "status": 1,
  "data": {
    "total": 2501,
    "data": [
      {
        "target_token": "0x1234...合约地址",
        "pair": "0x5678...交易对地址",
        "token0_symbol": "TOKEN",
        "symbol_en": "TOKEN",
        "symbol_zh": "代币中文名",
        "name_zh": "中文名",
        "chain": "bsc",
        "current_price_usd": 0.00012345,
        "price_change_24h": 5.67,
        "tvl": 123456.78,
        "holders": 1500,
        "risk_score": 3,
        "appendix": "{\"website\":\"https://example.com\",\"twitter\":\"https://twitter.com/x\",\"telegram\":\"https://t.me/x\",\"discord\":\"https://discord.gg/x\"}",
        "target_listing_at": 1710000000000
      }
    ]
  }
}
```

**注意**: 列表接口不返回 `intro_cn`, 需要额外请求详情接口补充.

#### 4. 代币详情

```bash
curl -s 'https://nkdoym.com/v1api/v3/tokens/<合约地址>-<链>' \
  -H 'lang: cn' \
  -H 'X-Auth: <token>' \
  -H 'Content-Type: application/json'
```

示例: `/v1api/v3/tokens/0x1234abc...-bsc`

响应:
```json
{
  "status": 1,
  "data": {
    "token": {
      "name": "Token Name",
      "symbol": "TOKEN",
      "current_price_usd": 0.00012345,
      "price_change": 5.67,
      "main_pair_tvl": 123456.78,
      "holders": 1500,
      "risk_score": 3,
      "buy_tax": 0,
      "sell_tax": 0,
      "total": "1000000000",
      "burn_amount_dec": "500000",
      "launchpad": "pumpfun",
      "intro_cn": "这是项目的中文介绍...",
      "intro_en": "English introduction...",
      "appendix": "{\"website\":\"https://...\",\"twitter\":\"https://...\",\"telegram\":\"https://...\",\"discord\":\"https://...\",\"github\":\"https://...\",\"whitepaper\":\"https://...\"}",
      "pairs": [
        {
          "show_name": "PancakeSwap V2",
          "amm": "pcs",
          "tvl": 50000.0,
          "price_change_24h": 3.2
        }
      ]
    }
  }
}
```

`appendix` 是 JSON 字符串, 需二次解析. 字段: website/twitter/telegram/discord/github/whitepaper.

`intro_cn` 实际返回示例:
```
福马 · 税收分红+彩票机制(完整版规则)\n\n一, 税收分配\n\n交易产生税收后, 资金按以下比例分配: \n\n• 50% → 质押TOKEN钻石手LP分红池\n• 50% → 彩票奖池\n\n二, 钻石手质押分红规则\n\n1. 用户需将TOKEN质押...\nQQ1: 1101649973\nQQ2: 1057046154
```

特点: 项目方自己填写的介绍, 可能几百字, `\n` 分行, 常含规则说明/联系方式/QQ群等. 很多币的 `intro_en` 为空字符串.

#### 5. 热门代币

```bash
curl -s 'https://nkdoym.com/v1api/v2/tokens/hot' \
  -H 'lang: cn' \
  -H 'X-Auth: <token>'
```

响应: `{"status":1, "data": [<token对象列表>]}`

Token对象字段: symbol, chain, token(合约地址), current_price_usd, price_change, pool_size, holders.

#### 6. 涨幅榜

```bash
curl -s 'https://nkdoym.com/v1api/v2/tokens/priceChange' \
  -H 'lang: cn' \
  -H 'X-Auth: <token>'
```

响应: `encode_data` 格式, 需要解码.

解码后: `[{symbol, chain, token, current_price_usd, price_change}, ...]`

#### 7. 搜索代币

```bash
curl -s 'https://nkdoym.com/v1api/v2/tokens/query?keyword=<关键词>' \
  -H 'lang: cn' \
  -H 'X-Auth: <token>'
```

#### 8. 代币审计/合约信息

```bash
curl -s 'https://nkdoym.com/v1api/v2/tokens/contract?token_id=<id>&type=token&user_address=' \
  -H 'lang: cn' \
  -H 'X-Auth: <token>'
```

#### 9. 收录提交

```bash
curl -s -X POST 'https://nkdoym.com/v1api/v3/tokens/manager/submit' \
  -H 'X-Auth: <token>' \
  -F 'chain=bsc' \
  -F 'address=0x...' \
  -F '<其他字段>'
```

Content-Type: `multipart/form-data`

#### 10. 支持链列表

```bash
curl -s 'https://nkdoym.com/v1api/v3/tokens/manager/chains' \
  -H 'X-Auth: <token>'
```

#### 11. 查询收录提交状态

```bash
curl -s 'https://nkdoym.com/v1api/v3/tokens/manager/submition?id=<提交ID>' \
  -H 'X-Auth: <token>'
```

---

### WS: `wss://nkdoym.com/ws`

协议: JSON-RPC 2.0

#### 连接

```javascript
ws = new WebSocket("wss://nkdoym.com/ws");
```

#### 心跳

发送:
```json
{"jsonrpc": "2.0", "method": "ping", "id": 1}
```

响应: `pong`

#### 订阅消息格式

```json
{"jsonrpc": "2.0", "method": "subscribe", "params": ["<频道名>", <频道参数>], "id": 2}
```

#### 取消订阅

```json
{"jsonrpc": "2.0", "method": "unsubscribe", "params": ["<频道名>", <频道参数>], "id": 3}
```

#### 频道列表

| 频道 | params 示例 | 说明 |
|------|-------------|------|
| pricev2 | `["pricev2", ["0xpair1...", "0xpair2..."]]` | 价格订阅 (传pair地址数组) |
| kline | `["kline", "0xpair...", "1", "bsc"]` | K线 (pair, 分辨率, 链) |
| multi_kline | `["multi_kline", ["0xpair...", "1"], ...]` | 多交易对K线 |
| liq | `["liq", "0xpair..."]` | 流动性 |
| simple_tx | `["simple_tx", {"tks":[{"ch":"bsc","tk":"0xtoken..."}], "rt":"json"}]` | 简化交易 |
| asset | `["asset", ["0xtoken1...", "0xtoken2..."]]` | 资产变化 |

K线分辨率: "1"(1分), "5", "15", "30", "60", "240"(4时), "1D"

#### 推送事件格式

```json
{"method": "<事件名>", "params": {"channel": "<频道>", "data": {...}}}
```

事件列表: price_extra / pricev2 / price / price-new / price-gainer / kline / tx / simple_tx / liq / asset / switch_main_pair / tgbot / monitor / pumpstate / gold_signal / signalsv2_public_monitor / public_portrait

#### pricev2 推送示例

```json
{
  "method": "pricev2",
  "params": {
    "channel": "pricev2",
    "data": {
      "pair": "0x...",
      "price": "0.00012345",
      "price_usd": "0.00012345",
      "change_24h": "5.67",
      "tvl": "123456.78",
      "volume_24h": "50000"
    }
  }
}
```

---

### 重要字段

- `appendix`: JSON字符串, 需 `JSON.parse()` 解析, 含 website/twitter/telegram/discord/github/whitepaper
- `intro_cn` / `intro_en`: 项目介绍 (仅详情接口返回, 列表接口不含)
- `target_token`: 代币合约地址
- `pair`: 交易对标识
- Chain ID: bsc/eth/solana/base/arbitrum/polygon/optimism/avalanche/fantom

### 错误处理

- Token过期: 响应 `{"status": 10001}`, 需重新login
- 通用成功: `{"status": 1}`

### 注意

- 收录列表不含 intro, 脚本会自动请求详情接口补充
- WS 不推送新收录事件, 监控靠 HTTP 轮询 diff 地址
- Token 过期返回 `status:10001`
