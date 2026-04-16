# 漏洞分类速查表

当收到漏洞推文时, 根据以下特征快速判断漏洞类型.

## 分类决策树

```
收到漏洞推文
  |
  +-- 涉及0xdead/魔法地址?
  |     +-- 是 -> dead-address-whitelist-bypass
  |     +-- 否 -> 继续
  |
  +-- 涉及奖励/分红/staking计算?
  |     +-- 分母被操纵? -> reward-manipulation (变种A: 全局变量分母)
  |     +-- 买入即获得分红权? -> reward-manipulation (变种B: 奖励会计时序)
  |     +-- 转账后余额结算奖励? -> reward-manipulation (变种A: 转账后余额)
  |
  +-- 涉及整数溢出/精度丢失?
  |     +-- 是 -> arithmetic-vulns
  |
  +-- 涉及负数金额?
  |     +-- 是 -> negative-amount-vulns
  |
  +-- 涉及重入?
  |     +-- 是 -> (需新建 reentrancy.md)
  |
  +-- 涉及闪电贷价格操纵?
  |     +-- 是 -> risk-free-arbitrage
  |
  +-- 涉及AMM底池储备不同步?
  |     +-- 是 -> amm-reserve-desync
  |
  +-- 涉及溢出检查绕过?
  |     +-- 是 -> amm-overflow-check-bypass
  |
  +-- 涉及跨链桥证明伪造?
  |     +-- 是 -> bridge-proof-forgery
  |
  +-- 新类型?
        +-- 是 -> 新建资源文件, 命名用小写英文短横线
```

## 已有资源文件清单

| 文件 | 漏洞类型 | 已收录案例数 |
|------|---------|------------|
| dead-address-whitelist-bypass.md | 0xdead白名单绕过 | 1 (TMM) |
| reward-manipulation.md | 奖励操纵/会计时序 | 2 (BTCN, ListaDAO) |
| arithmetic-vulns.md | 算术漏洞 | - |
| negative-amount-vulns.md | 负数金额 | - |
| risk-free-arbitrage.md | 无风险套利 | - |
| amm-reserve-desync.md | AMM储备不同步 | - |
| amm-overflow-check-bypass.md | AMM溢出检查绕过 | - |
| bridge-proof-forgery.md | 跨链桥证明伪造 | - |

## 常见推文关键词 -> 分类映射

| 推文关键词 | 推荐分类 |
|-----------|---------|
| 0xdead, burn address, whitelist bypass | dead-address-whitelist-bypass |
| reward, dividend, staking, _mining, 分红 | reward-manipulation |
| overflow, underflow, precision, 精度 | arithmetic-vulns |
| negative, below zero, 负数 | negative-amount-vulns |
| flash loan, price manipulation, 闪电贷 | risk-free-arbitrage |
| reentrancy, 重入 | 新建 |
| signature, 签名绕过 | 新建 |
| access control, 权限绕过 | 视具体代码定 |