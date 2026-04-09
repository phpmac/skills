# Solidity 注释清理示例

## 文件顶部注释

清理前:
```solidity
/**
 * @title LiquidityBackflowPool
 * @dev 回流底池合约 - 接收手续费并直接注入流动性池
 *
 * [处理流程]
 *   1. JMTokenV2 调用 receiveJM() 转入手续费
 *   2. 合约直接将 JM 转给 PancakePair
 *   3. 调用 pair.sync() 更新储备
 *   4. 价格由市场自然调整
 */
```

清理后:
```solidity
/**
 * @title LiquidityBackflowPool
 * @dev 回流底池合约 - 接收手续费并直接注入流动性池
 *
 * [核心机制]
 *   直接注入 JM 到 Pair, 不经过 swap, 避免 K 错误
 */
```

## 函数注释

清理前:
```solidity
/**
 * @dev 接收 JM 手续费并注入池子
 * @param amount JM数量
 * @param sourceType 来源类型: 0=买入, 1=卖出, 2=撤池子
 *
 * [调用者]
 *   仅限 JMTokenV2 合约
 *
 * [处理流程]
 *   1. 验证调用者
 *   2. 将 JM 转给 Pair
 *   3. 触发事件
 */
```

清理后:
```solidity
/**
 * @dev 接收 JM 手续费并注入池子
 * @param amount JM数量
 * @param sourceType 来源: 0=买入, 1=卖出, 2=撤池子
 */
```

## 简单函数 - 删除注释

清理前:
```solidity
/**
 * @dev 紧急提取 JM (仅owner)
 * @param amount 提取数量
 */
function emergencyWithdraw(uint256 amount) external onlyOwner {
```

清理后:
```solidity
function emergencyWithdraw(uint256 amount) external onlyOwner {
```

## 内部实现 - 精简

清理前:
```solidity
/**
 * @dev 尝试调用sync更新Pair储备
 *
 * [设计目的]
 *   - 解决swap期间调用sync导致的LOCKED错误
 *   - 普通转账时Pair未被lock, 可以安全调用sync
 *   - 使用try-catch防止任何意外revert
 */
function trySync() external {
    require(msg.sender == jmToken, "Only JMToken");
    // 尝试调用sync更新储备
    // 普通转账时Pair未被lock, 应该成功
    try IPancakePair(lpPair).sync() {
        // sync成功, 储备已更新
    } catch {
        // sync失败, 下次转账时会再次尝试
    }
}
```

清理后:
```solidity
/**
 * @dev 尝试调用sync更新储备 (普通转账时触发)
 * swap期间Pair被lock, 普通转账时安全调用
 */
function trySync() external {
    require(msg.sender == jmToken, "Only JMToken");
    try IPancakePair(lpPair).sync() {} catch {}
}
```
