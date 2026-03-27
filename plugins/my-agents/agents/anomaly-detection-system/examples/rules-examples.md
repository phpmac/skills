# 检测规则示例代码

## Python 实现

### 资金流水检测器

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum

class AlertLevel(Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

@dataclass
class Alert:
    level: AlertLevel
    user_id: str
    rule_name: str
    message: str
    metadata: dict
    timestamp: datetime

class CashFlowDetector:
    """资金流水异常检测器"""

    def __init__(self, config: dict):
        self.config = config
        self.ratio_threshold = config['cash_flow']['ratio']['withdraw_deposit_ratio']
        self.fast_in_out_minutes = config['cash_flow']['fast_in_out']['minutes']
        self.fast_in_out_ratio = config['cash_flow']['fast_in_out']['ratio']

    def detect_withdraw_deposit_ratio(
        self,
        user_id: str,
        deposits: List[dict],
        withdraws: List[dict],
        window_days: int = 30
    ) -> Optional[Alert]:
        """
        检测充值-提现比例异常
        核心风控: 入金100但出金200 = 明显问题
        """
        cutoff_date = datetime.now() - timedelta(days=window_days)

        recent_deposits = [d for d in deposits if d['timestamp'] > cutoff_date]
        recent_withdraws = [w for w in withdraws if w['timestamp'] > cutoff_date]

        total_deposit = sum(d['amount'] for d in recent_deposits)
        total_withdraw = sum(w['amount'] for w in recent_withdraws)

        if total_deposit == 0:
            return None

        ratio = total_withdraw / total_deposit

        if ratio > self.ratio_threshold:
            return Alert(
                level=AlertLevel.P0,
                user_id=user_id,
                rule_name="withdraw_deposit_ratio",
                message=f"提现充值比例异常: {ratio:.2f} (阈值: {self.ratio_threshold})",
                metadata={
                    'total_deposit': total_deposit,
                    'total_withdraw': total_withdraw,
                    'ratio': ratio
                },
                timestamp=datetime.now()
            )

        return None

    def detect_fast_in_out(
        self,
        user_id: str,
        deposits: List[dict],
        withdraws: List[dict]
    ) -> Optional[Alert]:
        """
        检测快进快出
        入金后短时间立即出金
        """
        threshold_seconds = self.fast_in_out_minutes * 60

        for deposit in deposits:
            for withdraw in withdraws:
                if withdraw['timestamp'] > deposit['timestamp']:
                    time_diff = (withdraw['timestamp'] - deposit['timestamp']).total_seconds()

                    if 0 < time_diff < threshold_seconds:
                        # 检查金额比例
                        fast_amount = min(deposit['amount'], withdraw['amount'])
                        ratio = fast_amount / deposit['amount'] if deposit['amount'] > 0 else 0

                        if ratio > self.fast_in_out_ratio:
                            return Alert(
                                level=AlertLevel.P0,
                                user_id=user_id,
                                rule_name="fast_in_out",
                                message=f"快进快出: {time_diff/60:.1f}分钟内完成",
                                metadata={
                                    'deposit_amount': deposit['amount'],
                                    'withdraw_amount': withdraw['amount'],
                                    'time_diff_minutes': time_diff / 60,
                                    'amount_ratio': ratio
                                },
                                timestamp=datetime.now()
                            )

        return None

    def detect_daily_spike(
        self,
        user_id: str,
        today_withdraw: float,
        historical_daily_avg: float
    ) -> Optional[Alert]:
        """
        检测日内出金突变
        当日出金远超历史均值
        """
        spike_ratio = self.config['cash_flow']['daily_spike']['ratio']
        threshold = historical_daily_avg * spike_ratio

        if today_withdraw > threshold:
            return Alert(
                level=AlertLevel.P1,
                user_id=user_id,
                rule_name="daily_withdraw_spike",
                message=f"日内出金突变: 今日{today_withdraw} vs 均值{historical_daily_avg:.2f}",
                metadata={
                    'today_withdraw': today_withdraw,
                    'historical_avg': historical_daily_avg,
                    'spike_ratio': spike_ratio
                },
                timestamp=datetime.now()
            )

        return None
```

### 资金盘检测器

```python
class PonziDetector:
    """资金盘异常检测器"""

    def __init__(self, config: dict):
        self.config = config
        self.staking_lock_minutes = config['ponzi']['staking']['lock_minutes']
        self.daily_release_limit = config['ponzi']['static_release']['daily_limit']

    def detect_staking_fast_out(
        self,
        user_id: str,
        staking_records: List[dict]
    ) -> List[Alert]:
        """
        检测质押快速进出
        质押后短时间解除
        """
        alerts = []
        lock_seconds = self.staking_lock_minutes * 60

        stakes = [s for s in staking_records if s['type'] == 'STAKE']
        unstakes = [s for s in staking_records if s['type'] == 'UNSTAKE']

        for stake in stakes:
            for unstate in unstakes:
                if unstate['timestamp'] > stake['timestamp']:
                    time_diff = (unstate['timestamp'] - stake['timestamp']).total_seconds()

                    if time_diff < lock_seconds:
                        alerts.append(Alert(
                            level=AlertLevel.P0,
                            user_id=user_id,
                            rule_name="staking_fast_out",
                            message=f"质押快速解除: {time_diff/60:.1f}分钟",
                            metadata={
                                'stake_amount': stake['amount'],
                                'unstake_amount': unstate['amount'],
                                'time_diff_minutes': time_diff / 60
                            },
                            timestamp=datetime.now()
                        ))

        return alerts

    def detect_static_release_frequency(
        self,
        user_id: str,
        release_records: List[dict],
        date: datetime
    ) -> Optional[Alert]:
        """
        检测静态释放频率
        每日释放次数超过产品设定
        """
        day_start = datetime(date.year, date.month, date.day)
        day_end = day_start + timedelta(days=1)

        daily_releases = [
            r for r in release_records
            if day_start <= r['timestamp'] < day_end
        ]

        if len(daily_releases) > self.daily_release_limit:
            return Alert(
                level=AlertLevel.P0,
                user_id=user_id,
                rule_name="static_release_frequency",
                message=f"静态释放频率异常: 今日{len(daily_releases)}次 (限制: {self.daily_release_limit})",
                metadata={
                    'release_count': len(daily_releases),
                    'limit': self.daily_release_limit
                },
                timestamp=datetime.now()
            )

        return None

    def detect_batch_unstake(
        self,
        user_id: str,
        unstake_records: List[dict],
        window_seconds: int = 60,
        count_threshold: int = 5
    ) -> Optional[Alert]:
        """
        检测同时大量解除质押
        同一时间批量解除
        """
        if len(unstake_records) < count_threshold:
            return None

        # 按时间排序
        sorted_records = sorted(unstake_records, key=lambda x: x['timestamp'])

        for i in range(len(sorted_records) - count_threshold + 1):
            window_records = sorted_records[i:i + count_threshold]
            time_span = (window_records[-1]['timestamp'] - window_records[0]['timestamp']).total_seconds()

            if time_span < window_seconds:
                total_amount = sum(r['amount'] for r in window_records)
                return Alert(
                    level=AlertLevel.P0,
                    user_id=user_id,
                    rule_name="batch_unstake",
                    message=f"批量解除质押: {count_threshold}笔 在 {time_span:.1f}秒内",
                    metadata={
                        'count': count_threshold,
                        'time_span_seconds': time_span,
                        'total_amount': total_amount
                    },
                    timestamp=datetime.now()
                )

        return None
```

### 关联检测器

```python
class CorrelationDetector:
    """关联检测器 - 跨系统协同"""

    def __init__(self, config: dict):
        self.config = config

    def detect_staking_withdraw_correlation(
        self,
        user_id: str,
        staking_records: List[dict],
        withdraw_records: List[dict],
        time_window_minutes: int = 30
    ) -> Optional[Alert]:
        """
        检测质押+出金关联
        质押解除后立即大额提现
        """
        threshold = time_window_minutes * 60

        for stake in staking_records:
            if stake['type'] != 'UNSTAKE':
                continue

            for withdraw in withdraw_records:
                if withdraw['timestamp'] > stake['timestamp']:
                    time_diff = (withdraw['timestamp'] - stake['timestamp']).total_seconds()

                    if time_diff < threshold:
                        amount_ratio = withdraw['amount'] / stake['amount'] if stake['amount'] > 0 else 0

                        if amount_ratio > 0.5:
                            return Alert(
                                level=AlertLevel.P0,
                                user_id=user_id,
                                rule_name="staking_withdraw_correlation",
                                message=f"质押解除后立即提现: {time_diff/60:.1f}分钟后提现{withdraw['amount']}",
                                metadata={
                                    'unstake_amount': stake['amount'],
                                    'withdraw_amount': withdraw['amount'],
                                    'time_diff_minutes': time_diff / 60
                                },
                                timestamp=datetime.now()
                            )

        return None

    def detect_multi_account_correlation(
        self,
        device_to_users: dict,
        ip_to_users: dict,
        threshold: int = 3
    ) -> List[Alert]:
        """
        检测多账户协同
        同设备/IP多账户操作
        """
        alerts = []

        # 同一设备多账户
        for device, users in device_to_users.items():
            if len(users) >= threshold:
                alerts.append(Alert(
                    level=AlertLevel.P1,
                    user_id=','.join(users),
                    rule_name="multi_account_device",
                    message=f"同一设备{len(users)}个账户",
                    metadata={
                        'device': device,
                        'user_count': len(users),
                        'users': users
                    },
                    timestamp=datetime.now()
                ))

        # 同一IP多账户
        for ip, users in ip_to_users.items():
            if len(users) >= threshold:
                alerts.append(Alert(
                    level=AlertLevel.P1,
                    user_id=','.join(users),
                    rule_name="multi_account_ip",
                    message=f"同一IP{len(users)}个账户",
                    metadata={
                        'ip': ip,
                        'user_count': len(users),
                        'users': users
                    },
                    timestamp=datetime.now()
                ))

        return alerts
```

## SQL 查询示例

### 检测充值-提现比例异常

```sql
WITH user_transactions AS (
    SELECT
        user_id,
        SUM(CASE WHEN type = 'DEPOSIT' THEN amount ELSE 0 END) as total_deposit,
        SUM(CASE WHEN type = 'WITHDRAW' THEN amount ELSE 0 END) as total_withdraw,
        COUNT(CASE WHEN type = 'DEPOSIT' THEN 1 END) as deposit_count,
        COUNT(CASE WHEN type = 'WITHDRAW' THEN 1 END) as withdraw_count
    FROM transactions
    WHERE created_at >= NOW() - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT
    user_id,
    total_deposit,
    total_withdraw,
    CASE WHEN total_deposit > 0
         THEN total_withdraw / total_deposit
         ELSE 0 END as ratio,
    CASE
        WHEN total_withdraw > total_deposit * 1.5 THEN 'P0'
        WHEN total_withdraw > total_deposit * 1.2 THEN 'P1'
        ELSE 'NORMAL'
    END as risk_level
FROM user_transactions
WHERE total_deposit > 0
HAVING total_withdraw / total_deposit > 1.5
ORDER BY ratio DESC;
```

### 检测快进快出

```sql
SELECT
    d.user_id,
    d.id as deposit_id,
    d.amount as deposit_amount,
    d.created_at as deposit_time,
    w.id as withdraw_id,
    w.amount as withdraw_amount,
    w.created_at as withdraw_time,
    EXTRACT(EPOCH FROM (w.created_at - d.created_at)) / 60 as minutes_diff
FROM deposits d
JOIN withdraws w ON d.user_id = w.user_id
WHERE w.created_at > d.created_at
  AND w.created_at - d.created_at < INTERVAL '10 minutes'
  AND w.amount >= d.amount * 0.8
ORDER BY minutes_diff;
```

### 检测拆分交易 (Structuring)

```sql
WITH daily_deposits AS (
    SELECT
        user_id,
        DATE(created_at) as deposit_date,
        COUNT(*) as deposit_count,
        SUM(amount) as total_amount,
        MAX(amount) as max_single_deposit
    FROM deposits
    WHERE created_at >= NOW() - INTERVAL '30 days'
    GROUP BY user_id, DATE(created_at)
)
SELECT
    user_id,
    deposit_date,
    deposit_count,
    total_amount,
    max_single_deposit,
    CASE
        WHEN max_single_deposit BETWEEN 9000 AND 9999 THEN 'SUSPICIOUS_AMOUNT'
        WHEN deposit_count >= 5 AND max_single_deposit < 10000 THEN 'STRUCTURING'
        ELSE 'NORMAL'
    END as risk_type
FROM daily_deposits
WHERE max_single_deposit BETWEEN 9000 AND 9999
   OR (deposit_count >= 5 AND max_single_deposit < 10000)
ORDER BY deposit_count DESC;
```

## 规则引擎配置 (Drools)

```java
package com.anomaly.detection.rules;

import com.anomaly.detection.model.Transaction;
import com.anomaly.detection.model.Alert;
import com.anomaly.detection.model.AlertLevel;

global AlertService alertService;

rule "Withdraw Deposit Ratio Exceeded"
    when
        $userTx : TransactionUserSummary(
            totalWithdraw > totalDeposit * 1.5,
            totalDeposit > 0
        )
    then
        Alert alert = new Alert();
        alert.setLevel(AlertLevel.P0);
        alert.setUserId($userTx.getUserId());
        alert.setRuleName("withdraw_deposit_ratio");
        alert.setMessage("提现充值比例异常: " + $userTx.getRatio());
        alertService.createAlert(alert);
end

rule "Fast In Fast Out"
    when
        $deposit : Transaction(type == "DEPOSIT", $userId : userId, $amount : amount, $time : timestamp)
        $withdraw : Transaction(type == "WITHDRAW", userId == $userId, amount >= $amount * 0.8, this after $deposit)
        eval(java.time.Duration.between($deposit.getTimestamp(), $withdraw.getTimestamp()).toMinutes() < 10)
    then
        Alert alert = new Alert();
        alert.setLevel(AlertLevel.P0);
        alert.setUserId($userId);
        alert.setRuleName("fast_in_out");
        alert.setMessage("快进快出检测");
        alertService.createAlert(alert);
end

rule "Staking Fast Unlock"
    when
        $stake : StakingRecord(type == "STAKE", $userId : userId, $amount : amount, $time : timestamp)
        $unstake : StakingRecord(type == "UNSTAKE", userId == $userId, amount == $amount, this after $stake)
        eval(java.time.Duration.between($stake.getTimestamp(), $unstake.getTimestamp()).toMinutes() < 60)
    then
        Alert alert = new Alert();
        alert.setLevel(AlertLevel.P0);
        alert.setUserId($userId);
        alert.setRuleName("staking_fast_unlock");
        alert.setMessage("质押快速解除");
        alertService.createAlert(alert);
end
```
