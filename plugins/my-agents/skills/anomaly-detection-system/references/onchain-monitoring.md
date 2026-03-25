# 区块链链上监控规则

## 检测场景

区块链链上异常检测和监控,包括AML,稳定币异常,DEX监控,混币检测等.

## 链上AML监控

### 大额转账监控

| 资产类型 | 建议阈值 |
|----------|----------|
| USDT (ERC-20) | >$100,000 |
| USDC | >$50,000 |
| BTC | >$500,000 (2 BTC) |
| ETH | >$200,000 (100 ETH) |

### 频率检查

| 指标 | 阈值 |
|------|------|
| 1小时内转出比例 | > 50% 资产 |
| 24h交易次数 | > 20次 |
| 关联地址数量 | > 10个 |

---

## 稳定币脱锚检测

### 检测算法

```
实时价格 vs 锚定价格(1.0)
  - 偏差 > 0.5%: Warning
  - 偏差 > 1%: Critical
  - 偏差 > 3%: Emergency
```

### 检测方法对比

| 方法 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| 简单阈值 | 价格偏离>预设值 | 易实现 | 误报高 |
| 面板二元模型 | 历史波动率调整 | 自适应 | 计算复杂 |
| 行为指标 | 交易量/流动性异常 | 提前预警 | 需多数据源 |

---

## 资金快进快出检测

### 检测公式

```
velocity_score = min(inflow, outflow) / max(inflow, outflow)

报警条件:
  - velocity_score > 0.8 AND holding_period < 2h
```

### 行为特征

| 模式 | 特征 | 风险 |
|------|------|------|
| 快速入金快出金 | 高频互换,短持有期 | 洗钱嫌疑 |
| 快速出金不出金 | 充值后立即转出 | 跑分/拆分 |
| 循环交易 | 多地址循环 | 混淆资金链 |
| 批量归集 | 多个小地址->一大地址 | 资金归集 |

---

## DEX异常交易监控

### 异常类型

| 异常类型 | 检测特征 | 监控指标 |
|----------|----------|----------|
| 闪电贷攻击 | 单笔TX操控价格 | 大额借款/还款时间差 |
| 洗售交易 | 同一地址反复买卖 | Wash Trade Score |
| 流动性抽离 | Pool余额骤降 | LP Token流动性变化 |
| 价格操控 | 短期价格剧烈波动 | Oracle Price Deviation |
| 大户砸盘 | 大额卖出->价格下跌 | Whale Ratio |

### 实时监控

```python
Mempool/Block Stream
        |
        v
+------------------+
| DEX Event Parser |  <- Uniswap/SushiSwap/Curve Events
+------------------+
        |
        v
+------------------+
| Pattern Matching |  <- Heuristic Rules + ML Models
+------------------+
```

---

## 混币检测

### 检测层次

| 检测层 | 方法 | 准确率 |
|--------|------|--------|
| 直接关系 | 黑名单匹配 | 已知混币100% |
| 2-3跳关系 | 图遍历分析 | 高 |
| 行为模式 | ML异常检测 | 96.35% |
| 金额特征 | peel chain分析 | 中 |

### GNN检测架构

```
Wallet Transaction Graph
        |
        v
+-------------------+
| Account Relevance |  <- 账户关联度计算
+-------------------+
        |
        v
+-------------------+
| BFS Graph Build   |  <- 广度优先图构建
+-------------------+
        |
        v
+-------------------+
| 3-Layer GCN       |  <- 图卷积网络学习
+-------------------+
```

---

## 跨链桥异常检测

### 异常类型

| 异常类型 | 描述 | 损失案例 |
|----------|------|----------|
| 伪造提现攻击 | 假消息欺骗跨链 | Ronin $611M |
| 最终性绕过 | 提前确认交易 | Nomad $190M |
| 合约实现漂移 | 不同链处理不一致 | - |

### 检测指标

| 指标 | 正常范围 | 异常阈值 |
|------|----------|----------|
| 跨链最终性时间 | >1 min (ETH) | <1 min |
| 锁定代币差异 | $0 | >$1M |
| 未提取资金 | <1% | >5% |

---

## 智能合约异常调用

### 关键监控事件

| 事件类型 | 检测目的 | 危险等级 |
|----------|----------|----------|
| Mint/Burn | 异常代币铸造/销毁 | Critical |
| Ownership Transfer | 权限转移 | High |
| Pausable Pause | 合约暂停 | High |
| Upgradeable Proxy | 逻辑变更 | Critical |
| Large Transfer | 大额转账 | Medium |

---

## 配置示例

```yaml
onchain:
  # AML监控
  aml:
    usdt_threshold: 100000
    usdc_threshold: 50000
    btc_threshold: 2
    eth_threshold: 100
    velocity_outflow_ratio: 0.5
    velocity_period_hours: 1
    frequency_24h: 20
    address_count_limit: 10

  # 稳定币监控
  stablecoin:
    price_deviation_warning: 0.005
    price_deviation_critical: 0.01
    price_deviation_emergency: 0.03

  # DEX监控
  dex:
    flash_loan_size_threshold: 1000000
    wash_trade_score: 0.8
    liquidity_drop_ratio: 0.5
    price_deviation: 0.01
    whale_ratio: 0.1

  # 混币检测
  mixer:
    tornado_cash_blacklist: true
    graph_hop_limit: 3
    peel_chain_analysis: true
    gnn_confidence_threshold: 0.8

  # 跨链桥监控
  bridge:
    finality_time_eth_min: 1
    locked_token_diff: 1000000
    unclaimed_ratio: 0.05

  # 合约监控
  contract:
    monitor_events:
      - Mint
      - Burn
      - OwnershipTransfer
      - PausablePause
      - UpgradeableProxy
      - LargeTransfer
      - ApprovalChange
```
