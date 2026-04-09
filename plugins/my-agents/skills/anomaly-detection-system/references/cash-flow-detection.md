# 资金流水异常检测规则

## 检测场景

资金流水检测是核心风控模块,用于监控充值,提现,转账等资金流动,发现入金100却出金200等严重异常.

## 检测规则

### 规则1: 充值-提现比例异常 (核心风控)

**逻辑**: 提现金额远超充值金额,正常情况下提现应小于等于充值

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| withdraw_deposit_ratio | 提现/充值比例上限 | 1.5 |
| cumulative_window_days | 累计窗口天数 | 30天 |

**检测公式**:
```
累计充值 = SUM(充值金额 WHERE user_id=X AND 日期范围)
累计提现 = SUM(提现金额 WHERE user_id=X AND 日期范围)

提现充值比例 = 累计提现 / 累计充值

IF 提现充值比例 > withdraw_deposit_ratio THEN 比例异常报警
```

**风控公式**:
```
净出金 = 累计提现 - 累计充值
IF 净出金 > 0 AND 净出金 / 累计充值 > 0.5 THEN 严重报警
```

**风险等级**: P0

---

### 规则2: 累计净出金异常

**逻辑**: 用户累计出金大于入金,资金盘特征

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| net_withdraw_threshold | 净出金阈值 | 0 |
| risk_ratio_threshold | 风险比例 | 0.5 |

**检测公式**:
```
净出金 = 累计提现 - 累计充值

IF 净出金 > net_withdraw_threshold THEN 净出金报警
IF 净出金 > 0 AND 净出金 / 累计充值 > risk_ratio_threshold THEN 严重报警
```

**风险等级**: P0

---

### 规则3: 快进快出

**逻辑**: 入金后短时间立即出金,洗钱或套利特征

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| fast_in_out_minutes | 快进快出阈值 | 10分钟 |
| fast_in_out_ratio | 快进快出比例 | 0.8 |

**检测公式**:
```
出金等待时间 = 首次提现时间 - 最近充值时间

IF 出金等待时间 < fast_in_out_minutes THEN 快进快出报警

快进快出金额 = MIN(充值金额, 提现金额)
快进快出比例 = 快进快出金额 / 总充值金额

IF 快进快出比例 > fast_in_out_ratio THEN 严重快进快出报警
```

**风险等级**: P0

---

### 规则4: 日内出金突变

**逻辑**: 当日出金突增,远超历史均值

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| daily_withdraw_ratio | 日出金突变倍数 | 3倍 |
| baseline_days | 基线天数 | 7天 |

**检测公式**:
```
日均出金 = SUM(历史出金) / baseline_days
当日出金 = SUM(当日出金)

IF 当日出金 > 日均出金 * daily_withdraw_ratio THEN 日出金突变报警
```

**风险等级**: P1

---

### 规则5: 出金-再入金循环

**逻辑**: 出金后快速重新入金,循环套利

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| cycle_window_minutes | 循环检测窗口 | 60分钟 |
| cycle_count_limit | 循环次数上限 | 3次 |

**检测公式**:
```
检测序列: 充值 -> 提现 -> 充值 -> 提现 ...

IF 循环次数 > cycle_count_limit WITHIN cycle_window_minutes THEN 循环套利报警
```

**风险等级**: P1

---

### 规则6: 账户余额异常

**逻辑**: 余额长期为0或接近0,资金不留存

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| zero_balance_ratio | 零余额比例阈值 | 0.9 |
| observation_days | 观察天数 | 30天 |

**检测公式**:
```
零余额天数 = COUNT(日期 WHERE 余额 < 阈值)
观察天数 = 总天数

零余额比例 = 零余额天数 / 观察天数

IF 零余额比例 > zero_balance_ratio THEN 余额异常报警
```

**风险等级**: P2

---

### 规则7: 新账户首次大额提现

**逻辑**: 新账户注册后立即大额提现

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| new_account_days | 新账户天数 | 7天 |
| first_withdraw_ratio | 首次提现比例 | 0.5 |

**检测公式**:
```
账户年龄 = 当前时间 - 注册时间
IF 账户年龄 < new_account_days THEN 新账户标记

首次提现比例 = 首次提现金额 / 账户余额
IF 新账户 AND 首次提现比例 > first_withdraw_ratio THEN 新账户大额提现报警
```

**风险等级**: P1

---

### 规则8: 充值来源异常

**逻辑**: 充值命中风险地址或黑名单

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| risk_address_threshold | 风险地址匹配 | 1次 |

**检测公式**:
```
充值来源命中风险库 = MATCH(充值地址, 风险地址库)

IF 命中次数 >= risk_address_threshold THEN 充值来源异常报警
```

**风险等级**: P0

---

## 核心风控指标汇总

| 指标 | 公式 | 报警阈值 | 风险等级 |
|------|------|----------|----------|
| 提现充值比 | 累计提现/累计充值 | > 1.5 | P0 |
| 净出金 | 累计提现-累计充值 | > 0 | P0 |
| 快进快出 | 出金时间-入金时间 | < 10分钟 | P0 |
| 日出金突变 | 当日/日均 | > 3倍 | P1 |
| 循环次数 | 循环次数 | > 3次 | P1 |
| 零余额比例 | 零余额天数/总天数 | > 0.9 | P2 |

---

## 配置示例

```yaml
cash_flow:
  # 核心比例检测
  ratio:
    withdraw_deposit_ratio: 1.5
    cumulative_window_days: 30
    net_withdraw_threshold: 0
    risk_ratio_threshold: 0.5

  # 快进快出检测
  fast_in_out:
    minutes: 10
    ratio: 0.8

  # 日内突变检测
  daily_spike:
    ratio: 3.0
    baseline_days: 7

  # 循环检测
  cycle:
    window_minutes: 60
    count_limit: 3

  # 余额异常检测
  balance:
    zero_ratio: 0.9
    observation_days: 30

  # 新账户检测
  new_account:
    days: 7
    first_withdraw_ratio: 0.5
```
