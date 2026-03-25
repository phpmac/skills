# 广告积分异常检测规则

## 检测场景

广告积分系统用于奖励用户观看广告,异常行为包括刷积分,虚假广告点击,积分重复等.

## 检测规则

### 规则1: 积分重复检测

**逻辑**: 同一用户短时间内获得相同积分值,正常广告积分随机,重复=异常

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| repeat_window_minutes | 时间窗口 | 30分钟 |
| repeat_count_threshold | 重复次数报警阈值 | 2次 |

**检测公式**:
```
相同积分值出现次数 = COUNT(积分记录 WHERE user_id=X AND 积分值=Y AND 时间差<窗口)

IF 相同积分值出现次数 >= repeat_count_threshold THEN 触发报警
```

**风险等级**: P1

---

### 规则2: 大额积分检测

**逻辑**: 单次广告积分超过正常范围

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| large_threshold | 大额阈值 | 1000 |
| daily_large_count_limit | 每日大额次数上限 | 10 |

**检测公式**:
```
IF 单次积分 > large_threshold THEN 大额报警

每日大额次数 = COUNT(大额积分记录 WHERE user_id=X AND 日期=今天)
IF 每日大额次数 > daily_large_count_limit THEN 频率报警
```

**风险等级**: P2

---

### 规则3: 小额积分检测

**逻辑**: 单次积分低于正常范围,可能为测试或异常

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| small_threshold | 小额阈值 | 1 |
| small_ratio_threshold | 小额占比阈值 | 0.9 |

**检测公式**:
```
小额占比 = 小额积分次数 / 总积分次数

IF 单次积分 < small_threshold THEN 小额记录
IF 小额占比 > small_ratio_threshold THEN 异常占比报警
```

**风险等级**: P2

---

### 规则4: 频率异常检测

**逻辑**: 用户在短时间内获得积分次数异常频繁

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| frequency_window_minutes | 频率窗口 | 30分钟 |
| frequency_limit | 次数上限 | 50 |
| daily_frequency_limit | 每日总次数上限 | 500 |

**检测公式**:
```
窗口内积分次数 = COUNT(积分记录 WHERE user_id=X AND 时间差<窗口)

IF 窗口内积分次数 > frequency_limit THEN 频率异常报警

每日总次数 = COUNT(积分记录 WHERE user_id=X AND 日期=今天)
IF 每日总次数 > daily_frequency_limit THEN 日频率异常报警
```

**风险等级**: P1

---

### 规则5: 未验证占比检测

**逻辑**: 广告验证状态未通过比例过高,可能存在虚假广告

**配置参数**:
| 参数 | 说明 | 默认值 |
|------|------|--------|
| unverified_ratio_threshold | 未验证占比阈值 | 0.7 (70%) |
| verification_window_hours | 验证窗口 | 24小时 |

**检测公式**:
```
未验证占比 = 未验证广告次数 / 总广告次数

IF 未验证占比 > unverified_ratio_threshold THEN 验证异常报警
```

**风险等级**: P1

---

## 关联检测

| 关联场景 | 检测逻辑 |
|----------|----------|
| 积分+充值双异常 | 积分频率异常高 + 充值金额异常高 |
| 积分+设备关联 | 多账户同一设备刷积分 |
| 积分+IP关联 | 多账户同一IP刷积分 |

---

## 配置示例

```yaml
ad_score:
  # 重复检测
  repeat:
    window_minutes: 30
    count_threshold: 2
    severity: P1

  # 大额检测
  large:
    threshold: 1000
    daily_count_limit: 10
    severity: P2

  # 小额检测
  small:
    threshold: 1
    ratio_threshold: 0.9
    severity: P2

  # 频率检测
  frequency:
    window_minutes: 30
    limit: 50
    daily_limit: 500
    severity: P1

  # 验证状态检测
  verification:
    ratio_threshold: 0.7
    window_hours: 24
    severity: P1
```
