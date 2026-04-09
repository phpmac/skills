# 资金盘/传销异常检测规则

## 检测场景

资金盘/传销系统常见于入金充值,质押生息,静态释放等场景,核心是检测资金异常流动和套利行为.

## 检测规则

### 规则1: 充值重复检测

**逻辑**: 同一用户短时间内充值相同金额,正常充值随机,重复=异常

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| repeat_window_minutes | 时间窗口 | 30分钟 |
| repeat_count_threshold | 重复次数报警阈值 | 2次 |
| amount_tolerance | 金额容差 | 1% |

**检测公式**:
```
相同充值金额出现次数 = COUNT(充值记录 WHERE user_id=X AND 金额差<容差 AND 时间差<窗口)

IF 相同充值金额出现次数 >= repeat_count_threshold THEN 触发报警
```

**风险等级**: P0

---

### 规则2: 大额充值检测

**逻辑**: 单次充值金额超过正常范围

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| large_threshold | 大额阈值 | 10000 |
| daily_large_count_limit | 每日大额次数上限 | 5 |

**检测公式**:
```
IF 单次充值 > large_threshold THEN 大额报警
IF 24h内大额充值 > daily_large_count_limit THEN 频率报警
```

**风险等级**: P1

---

### 规则3: 小额充值检测

**逻辑**: 单次充值低于正常范围,可能为测试账户或拆分交易

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| small_threshold | 小额阈值 | 100 |
| small_ratio_threshold | 小额占比阈值 | 0.8 |

**检测公式**:
```
小额占比 = 小额充值次数 / 总充值次数

IF 小额占比 > small_ratio_threshold THEN 拆分交易嫌疑
```

**风险等级**: P1

---

### 规则4: 频繁充值/提现

**逻辑**: 短时间多次充值或提现操作

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| frequency_window_minutes | 频率窗口 | 60分钟 |
| frequency_limit | 次数上限 | 5 |
| daily_limit | 每日次数上限 | 20 |

**检测公式**:
```
窗口内充值次数 = COUNT(充值记录 WHERE user_id=X AND 时间差<窗口)
窗口内提现次数 = COUNT(提现记录 WHERE user_id=X AND 时间差<窗口)

IF 窗口内充值次数 > frequency_limit OR 窗口内提现次数 > frequency_limit THEN 频繁操作报警
```

**风险等级**: P1

---

### 规则5: 质押快速进出

**逻辑**: 质押后短时间解除,正常质押有锁定期

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| staking_lock_minutes | 质押锁定时间 | 60分钟 |
| fast_unlock_ratio_threshold | 快速解除比例阈值 | 0.3 |

**检测公式**:
```
质押到解除时间差 = 解除时间 - 质押时间

IF 质押到解除时间差 < staking_lock_minutes THEN 快速解除报警

快速解除比例 = 快速解除次数 / 总解除次数
IF 快速解除比例 > fast_unlock_ratio_threshold THEN 套利模式报警
```

**风险等级**: P0

---

### 规则6: 同时大量解除质押

**逻辑**: 同一时间批量解除质押

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| batch_window_seconds | 批量窗口 | 60秒 |
| batch_count_threshold | 批量笔数阈值 | 5 |

**检测公式**:
```
窗口内解除次数 = COUNT(解除记录 WHERE 时间差<窗口)

IF 窗口内解除次数 > batch_count_threshold THEN 批量解除报警
```

**风险等级**: P0

---

### 规则7: 质押总量异常

**逻辑**: 用户质押总量超过设定阈值

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| total_staking_threshold | 质押总量上限 | 100000 |
| staking_velocity_threshold | 质押增速阈值 | 2倍 |

**检测公式**:
```
当前质押总量 = SUM(质押中金额 WHERE user_id=X)

IF 当前质押总量 > total_staking_threshold THEN 质押超限报警

质押增速 = 当日质押总量 / 日均质押总量
IF 质押增速 > staking_velocity_threshold THEN 增速异常报警
```

**风险等级**: P1

---

### 规则8: 静态释放频率

**逻辑**: 每日静态释放次数超过产品设定次数

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| daily_release_limit | 每日释放次数上限 | 1 |
| release_interval_hours | 释放间隔 | 24小时 |

**检测公式**:
```
每日释放次数 = COUNT(释放记录 WHERE user_id=X AND 日期=今天)

IF 每日释放次数 > daily_release_limit THEN 释放频率异常报警

最近释放间隔 = 当前时间 - 上次释放时间
IF 最近释放间隔 < release_interval_hours THEN 间隔异常报警
```

**风险等级**: P0

---

### 规则9: 大额/小额提现

**逻辑**: 提现金额异常检测

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| large_withdraw_threshold | 大额提现阈值 | 5000 |
| small_withdraw_threshold | 小额提现阈值 | 10 |

**检测公式**:
```
IF 单次提现 > large_withdraw_threshold THEN 大额提现报警
IF 单次提现 < small_withdraw_threshold AND 余额充足 THEN 小额试探报警
```

**风险等级**: P1

---

## 关联检测

| 关联场景 | 检测逻辑 |
|----------|----------|
| 质押+出金关联 | 质押解除后立即大额提现 |
| 充值+提现循环 | 充值后立即提现或提现后立即充值 |
| 多账户协同 | 同设备/IP多账户操作 |

---

## 配置示例

```yaml
ponzi:
  # 充值检测
  deposit:
    repeat_window_minutes: 30
    repeat_count: 2
    amount_tolerance: 0.01
    large_threshold: 10000
    small_threshold: 100
    small_ratio: 0.8

  # 频率检测
  frequency:
    window_minutes: 60
    limit: 5
    daily_limit: 20

  # 质押检测
  staking:
    lock_minutes: 60
    fast_unlock_ratio: 0.3
    batch_window_seconds: 60
    batch_count: 5
    total_threshold: 100000
    velocity_threshold: 2

  # 静态释放
  static_release:
    daily_limit: 1
    interval_hours: 24

  # 提现检测
  withdraw:
    large_threshold: 5000
    small_threshold: 10
```
