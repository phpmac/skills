---
name: anomaly-detection-system
description: Use when 用户要求设计异常检测系统, 创建风控监控系统, 配置积分异常检测, 配置资金盘监控, 添加充值提现监控规则, 或配置预警系统
model: sonnet
color: magenta
tools: ["Read", "Grep", "Glob", "Edit", "Write", "Bash"]
---

# 综合异常检测与预警系统

提供多场景异常检测规则设计和预警机制配置, 用于提前发现问题和风险.

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      综合异常检测平台                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ 广告积分系统  │  │ 资金盘系统  │  │ 资金流水系统 │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         └────────────────┼────────────────┘                   │
│                          │                                      │
│                  ┌───────▼───────┐                              │
│                  │  关联分析引擎  │                              │
│                  └───────┬───────┘                              │
│                          │                                      │
│  ┌─────────────┐  ┌─────▼─────┐  ┌─────────────┐            │
│  │ 交易所风控   │  │  预警引擎  │  │ 银行/金融监控│            │
│  └─────────────┘  └───────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 核心检测模块

| 模块 | 适用场景 | 参考文档 |
|------|----------|----------|
| 广告积分检测 | 刷积分,虚假广告 | [ad-score-detection.md](anomaly-detection-system/references/ad-score-detection.md) |
| 资金盘检测 | 传销,质押套利 | [ponzi-detection.md](anomaly-detection-system/references/ponzi-detection.md) |
| 资金流水检测 | 充值提现比例异常 | [cash-flow-detection.md](anomaly-detection-system/references/cash-flow-detection.md) |
| 交易所风控 | 交易频次,大额交易 | [exchange-risk.md](anomaly-detection-system/references/exchange-risk.md) |
| 银行AML监控 | 反洗钱,合规报告 | [bank-aml.md](anomaly-detection-system/references/bank-aml.md) |
| 区块链监控 | 链上异常,混币检测 | [onchain-monitoring.md](anomaly-detection-system/references/onchain-monitoring.md) |

## 检测规则速查

### 资金流水核心规则 (必须配置)

| 规则名称 | 公式/逻辑 | 默认阈值 | 风险等级 |
|----------|-----------|----------|----------|
| 充值-提现比例 | `提现金额 / 充值金额` | > 1.5 | P0 |
| 累计净出金 | `累计提现 - 累计充值` | > 0 | P0 |
| 快进快出 | `出金时间 - 入金时间` | < 10分钟 | P0 |
| 日内出金突变 | `当日出金 / 日均出金` | > 3倍 | P1 |
| 出金-再入金循环 | 循环次数 | > 3次 | P1 |

### 广告积分检测规则

| 规则名称 | 逻辑 | 默认阈值 |
|----------|------|----------|
| 积分重复检测 | 30分钟内相同积分值 | 时间窗口30分钟 |
| 大额积分检测 | 单次积分超过阈值 | 大额阈值 |
| 频率异常检测 | 30分钟内次数超限 | 次数上限 |
| 未验证占比 | 未验证广告占比 | > 70% |

### 资金盘检测规则

| 规则名称 | 逻辑 | 默认阈值 |
|----------|------|----------|
| 充值重复检测 | 30分钟内相同金额 | 时间窗口30分钟 |
| 质押快速进出 | 质押到解除时间差 | < 1小时 |
| 静态释放频率 | 每日释放次数 | > 产品设定次数 |
| 大额充值 | 单笔充值金额 | 大额阈值 |

## 预警分级

| 级别 | 条件 | 动作 |
|------|------|------|
| **P0-紧急** | 充值100提现200,快进快出,大额可疑 | 立即拦截 + 人工介入 |
| **P1-警告** | 频率超限,质押异常,比例超标 | 延迟处理 + 重点关注 |
| **P2-观察** | 单次异常但未达阈值 | 持续监控 + 记录审计 |
| **P3-记录** | 正常行为但有嫌疑特征 | 日志留存 + 定期分析 |

## 配置模板

### 基础配置结构

```yaml
anomaly_detection:
  # 广告积分检测
  ad_score:
    repeat_window_minutes: 30
    large_threshold: 1000
    small_threshold: 1
    frequency_limit: 50
    unverified_ratio_threshold: 0.7

  # 资金盘检测
  ponzi:
    repeat_window_minutes: 30
    large_deposit_threshold: 10000
    small_deposit_threshold: 100
    frequency_limit: 10
    staking_lock_minutes: 60
    daily_release_limit: 1

  # 资金流水检测
  cash_flow:
    withdraw_deposit_ratio: 1.5
    fast_in_out_minutes: 10
    daily_withdraw_ratio: 3.0
    cycle_limit: 3

  # 交易所风控
  exchange:
    large_tx_threshold: 10000
    ot_ratio_alert: 50
    cancel_rate_alert: 0.8

  # 银行AML
  aml:
    ctr_threshold: 10000
    sar_threshold: 5000
    structuring_window_days: 30
```

完整配置模板: [config-template.yaml](anomaly-detection-system/examples/config-template.yaml)

### 预警通知配置

```yaml
alerts:
  channels:
    - type: email
      recipients: [risk@example.com]
    - type: telegram
      bot_token: ${TELEGRAM_BOT_TOKEN}
      chat_id: ${ALERT_CHAT_ID}
    - type: webhook
      url: ${WEBHOOK_URL}

  levels:
    P0:
      channels: [email, telegram, webhook]
      urgency: immediate
    P1:
      channels: [telegram, webhook]
      urgency: high
    P2:
      channels: [webhook]
      urgency: normal
```

## 关联检测规则

跨系统协同检测, 发现复杂欺诈模式:

| 关联场景 | 检测逻辑 |
|----------|----------|
| 积分+充值双异常 | 积分异常高 + 充值金额异常高 |
| 质押+出金关联 | 质押解除后立即大额提现 |
| 充值+提现比例 | 入金100但出金200 |
| 多账户协同 | 同设备/IP多账户操作 |

## 检测算法选择

| 算法 | 适用场景 | 延迟要求 |
|------|----------|----------|
| 规则引擎 | 已知明确阈值 | < 100ms |
| 统计检测 | 频率异常,阈值偏离 | < 1s |
| 序列分析 | 质押进出,快进快出 | < 1s |
| 图关联分析 | 多账户协同,邀请关系 | < 10s |
| 机器学习 | 复杂模式,未知异常 | < 1min |

算法详解: [detection-algorithms.md](anomaly-detection-system/references/detection-algorithms.md)

## 数据采集要求

| 维度 | 必需字段 |
|------|----------|
| 账户 | user_id, account_type, level, risk_score |
| 资金 | deposit, withdrawal, balance, frozen_amount |
| 行为 | action_type, frequency, duration, timestamp |
| 设备 | device_id, IP, location, fingerprint |
| 关联 | inviter_id, relationship_graph |

## 附加资源

- [ad-score-detection.md](anomaly-detection-system/references/ad-score-detection.md) - 广告积分检测完整规则
- [ponzi-detection.md](anomaly-detection-system/references/ponzi-detection.md) - 资金盘检测完整规则
- [cash-flow-detection.md](anomaly-detection-system/references/cash-flow-detection.md) - 资金流水检测完整规则
- [exchange-risk.md](anomaly-detection-system/references/exchange-risk.md) - 交易所风控检测规则
- [bank-aml.md](anomaly-detection-system/references/bank-aml.md) - 银行AML合规监控
- [onchain-monitoring.md](anomaly-detection-system/references/onchain-monitoring.md) - 区块链链上监控
- [detection-algorithms.md](anomaly-detection-system/references/detection-algorithms.md) - 检测算法详解
- [config-template.yaml](anomaly-detection-system/examples/config-template.yaml) - 完整配置模板
- [rules-examples.md](anomaly-detection-system/examples/rules-examples.md) - 检测规则示例代码

## 实施步骤

1. **评估场景**: 确定需要哪些检测模块
2. **配置阈值**: 根据业务特征调整默认阈值
3. **设置预警**: 配置通知渠道和响应流程
4. **测试验证**: 使用历史数据回测检测效果
5. **持续优化**: 根据误报情况调整规则
