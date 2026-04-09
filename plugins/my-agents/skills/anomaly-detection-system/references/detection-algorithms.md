# 检测算法详解

## 算法选择指南

| 算法 | 适用场景 | 延迟要求 | 复杂度 |
|------|----------|----------|--------|
| 规则引擎 | 已知明确阈值 | < 100ms | 低 |
| 统计检测 | 频率异常,阈值偏离 | < 1s | 低 |
| 序列分析 | 质押进出,快进快出 | < 1s | 中 |
| 图关联分析 | 多账户协同,邀请关系 | < 10s | 高 |
| 机器学习 | 复杂模式,未知异常 | < 1min | 高 |

---

## 规则引擎

### 适用场景

- 已知明确阈值的检测
- 充值100提现200等明确规则
- 配置简单,实时性要求高

### 常用规则引擎

- **Drools**: Java规则引擎,功能强大
- **EasyRules**: 轻量级规则引擎
- **ORule**: 简单规则定义

### 示例

```java
rule "Withdraw Deposit Ratio"
    when
        $transaction : Transaction(type == "WITHDRAW")
        $deposits : Number() from accumulate(
            Transaction(type == "DEPOSIT", userId == $transaction.userId, timestamp > $transaction.timestamp - 30d),
            count()
        )
        $withdraws : Number() from accumulate(
            Transaction(type == "WITHDRAW", userId == $transaction.userId),
            sum(Transaction.amount)
        )
    then
        double ratio = $withdraws.doubleValue() / $deposits.doubleValue();
        if (ratio > 1.5) {
            alertService.createAlert(AlertLevel.P0, $transaction.userId, "Withdraw Deposit Ratio Exceeded");
        }
end
```

---

## 统计检测

### 3σ原则

**原理**: 假设数据服从正态分布,超过3σ的数据点为异常

```python
def detect_anomaly_3sigma(values: List[float], threshold: float = 3.0) -> List[int]:
    """
    values: 时间序列数据
    threshold: σ倍数,默认3
    返回: 异常点的索引
    """
    mean = np.mean(values)
    std = np.std(values)

    anomalies = []
    for i, v in enumerate(values):
        z_score = abs((v - mean) / std) if std > 0 else 0
        if z_score > threshold:
            anomalies.append(i)

    return anomalies
```

### Z-Score检测

```python
def z_score_anomaly(value: float, history: List[float], threshold: float = 3.0) -> bool:
    """检测单点是否异常"""
    mean = np.mean(history)
    std = np.std(history)

    if std == 0:
        return value != mean

    z_score = abs((value - mean) / std)
    return z_score > threshold
```

### 移动平均检测

```python
def moving_average_anomaly(
    current: float,
    window: List[float],
    threshold: float = 2.0
) -> bool:
    """
    当前值 vs 移动平均
    threshold: 倍数阈值
    """
    ma = np.mean(window)
    return abs(current) > ma * threshold
```

---

## 序列分析

### 快进快出检测

```python
def detect_fast_in_out(
    transactions: List[Transaction],
    threshold_minutes: int = 10
) -> List[Alert]:
    """
    检测快进快出模式
    入金后短时间立即出金
    """
    alerts = []
    deposits = [tx for tx in transactions if tx.type == "DEPOSIT"]
    withdraws = [tx for tx in transactions if tx.type == "WITHDRAW"]

    for deposit in deposits:
        for withdraw in withdraws:
            if withdraw.user_id == deposit.user_id:
                time_diff = withdraw.timestamp - deposit.timestamp
                if 0 < time_diff < threshold_minutes * 60:
                    alerts.append(Alert(
                        level=AlertLevel.P0,
                        user_id=deposit.user_id,
                        message=f"Fast In-Out: {time_diff/60:.1f} minutes"
                    ))

    return alerts
```

### 质押快速进出检测

```python
def detect_staking_fast_out(
    staking_records: List[StakingRecord],
    lock_minutes: int = 60
) -> List[Alert]:
    """
    检测质押快速解除
    质押后短时间解除
    """
    alerts = []

    for stake in staking_records:
        unlocks = [u for u in staking_records
                   if u.user_id == stake.user_id
                   and u.amount == stake.amount
                   and u.timestamp > stake.timestamp]

        for unlock in unlocks:
            time_diff = unlock.timestamp - stake.timestamp
            if time_diff < lock_minutes * 60:
                alerts.append(Alert(
                    level=AlertLevel.P0,
                    user_id=stake.user_id,
                    message=f"Staking fast out: {time_diff/60:.1f} minutes"
                ))

    return alerts
```

---

## 图关联分析

### 多账户关联检测

```python
def detect_related_accounts(
    transactions: List[Transaction],
    device_mapping: Dict[str, List[str]],
    ip_mapping: Dict[str, List[str]]
) -> List[AccountGroup]:
    """
    检测关联账户群体
    共享设备/IP的账户被认定为关联
    """
    graph = {}

    # 设备关联
    for device, accounts in device_mapping.items():
        for account in accounts:
            if account not in graph:
                graph[account] = set()
            graph[account].update(accounts)

    # IP关联
    for ip, accounts in ip_mapping.items():
        for account in accounts:
            if account not in graph:
                graph[account] = set()
            graph[account].update(accounts)

    # 使用并查集找连通分量
    parent = {k: k for k in graph}

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for accounts in graph.values():
        accounts = list(accounts)
        for i in range(1, len(accounts)):
            union(accounts[0], accounts[i])

    # 提取连通分量
    groups = {}
    for account in parent:
        root = find(account)
        if root not in groups:
            groups[root] = []
        groups[root].append(account)

    return [AccountGroup(accounts=v) for v in groups.values() if len(v) > 1]
```

### 资金流向追踪

```python
from collections import deque

def trace_fund_flow(
    start_address: str,
    max_hops: int = 5,
    max_nodes: int = 1000
) -> List[FundPath]:
    """
    追踪资金流向
    BFS遍历交易图
    """
    visited = {start_address}
    queue = deque([(start_address, 0, [])])
    paths = []

    while queue and len(visited) < max_nodes:
        current, depth, path = queue.popleft()

        if depth >= max_hops:
            continue

        out_transfers = get_outgoing_transfers(current)

        for transfer in out_transfers:
            if transfer.to not in visited:
                visited.add(transfer.to)
                new_path = path + [transfer]

                if transfer.is_suspicious:
                    paths.append(FundPath(
                        addresses=new_path,
                        risk_score=calculate_risk(new_path)
                    ))

                queue.append((transfer.to, depth + 1, new_path))

    return paths
```

---

## 机器学习检测

### Isolation Forest

```python
from sklearn.ensemble import IsolationForest
import numpy as np

class AnomalyDetector:
    def __init__(self, contamination: float = 0.1):
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=100
        )
        self.feature_names = None

    def train(self, features: np.ndarray, feature_names: List[str]):
        """
        训练异常检测模型
        features: 特征矩阵 (n_samples, n_features)
        """
        self.feature_names = feature_names
        self.model.fit(features)

    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        预测异常
        返回: 1=正常, -1=异常
        """
        return self.model.predict(features)

    def score(self, features: np.ndarray) -> np.ndarray:
        """
        返回异常分数
        分数越低越异常
        """
        return self.model.score_samples(features)

    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性"""
        # Isolation Forest 不直接提供特征重要性
        # 可用置换重要性或其他方法
        pass
```

### 特征工程示例

```python
def extract_transaction_features(
    transactions: List[Transaction],
    user_id: str,
    window_days: int = 30
) -> np.ndarray:
    """
    提取用户交易特征
    """
    user_txs = [tx for tx in transactions
                if tx.user_id == user_id
                and tx.timestamp > time.time() - window_days * 86400]

    features = {
        'tx_count': len(user_txs),
        'total_deposit': sum(tx.amount for tx in user_txs if tx.type == 'DEPOSIT'),
        'total_withdraw': sum(tx.amount for tx in user_txs if tx.type == 'WITHDRAW'),
        'avg_tx_amount': np.mean([tx.amount for tx in user_txs]) if user_txs else 0,
        'max_tx_amount': max([tx.amount for tx in user_txs]) if user_txs else 0,
        'tx_velocity': len(user_txs) / window_days,
        'withdraw_deposit_ratio': total_withdraw / total_deposit if total_deposit > 0 else 0,
        'unique_counterparties': len(set(tx.to for tx in user_txs)),
        'night_tx_ratio': len([tx for tx in user_txs if is_night(tx.timestamp)]) / len(user_txs) if user_txs else 0,
    }

    return np.array(list(features.values()))
```

---

## 技术架构

```
[数据采集层]
     |
     v
+------------------+
|  Kafka/Flink    |  实时流处理
+------------------+
     |
     v
+------------------+
|  规则引擎        |  Drools/EasyRules (<100ms)
+------------------+
     |
     v
+------------------+
|  统计检测        |  3σ/Z-Score (<1s)
+------------------+
     |
     v
+------------------+
|  AI模型层        |  LSTM/GNN/Isolation Forest (<1min)
+------------------+
     |
     v
+------------------+
|  决策层          |  自动处置/人工审核
+------------------+
```

---

## 性能指标

| 指标 | 目标 | 说明 |
|------|------|------|
| 检测延迟 | < 100ms | 实时规则检测 |
| 误报率 | < 5% | 合法用户不被打扰 |
| 召回率 | > 90% | 真实异常不漏报 |
|吞吐量 | > 10,000 TPS | 单节点处理能力 |
