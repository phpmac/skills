---
name: solidity-comment-style
description: Use when 清理Solidity合约代码注释, 精简冗余注释, 规范代码风格, 提升代码可读性, 移除过时的注释内容
---

# Solidity 注释清理规范

## 目标

清理冗长, 冗余的注释, 保留关键信息, 提升代码可读性.

清理前后对比示例:
- 清理前: 120行 -> 清理后: 70行 (减少 42%)

## 核心原则

### 1. 文件顶部注释 - 保留核心机制, 删除详细流程

清理前:
```solidity
/**
 * @title LiquidityBackflowPool
 * @dev 回流底池合约 - 接收手续费并直接注入流动性池
 *
 * [核心机制]
 *   采用 ShillMoon 方案: 直接注入 JM 到 Pair 合约, 不经过 swap
 *   避免 K 错误和价格滑点损失
 *
 * [处理流程]
 *   1. JMTokenV2 调用 receiveJM() 转入手续费
 *   2. 合约直接将 JM 转给 PancakePair
 *   3. 调用 pair.sync() 更新储备
 *   4. 价格由市场自然调整, 无滑点损失
 *
 * [手续费来源]
 *   - 买入 3%: 1% 回流
 *   - 卖出 3%: 1% 回流
 *   - 撤池子 20%: 5% 回流
 */
```

清理后:
```solidity
/**
 * @title LiquidityBackflowPool
 * @dev 回流底池合约 - 接收手续费并直接注入流动性池
 *
 * [核心机制]
 *   采用 ShillMoon 方案: 直接注入 JM 到 Pair 合约, 不经过 swap
 *   - swap期间: 只转代币, 不调用sync(避免LOCKED)
 *   - 普通转账: 调用trySync()更新储备
 *
 * [手续费来源]
 *   - 买入 3%: 1% 回流
 *   - 卖出 3%: 1% 回流
 *   - 撤池子 20%: 5% 回流
 */
```

### 2. 函数注释 - 简化为一行描述 + 参数说明

清理前:
```solidity
/**
 * @dev 接收 JM 手续费并直接注入池子 (swap场景, 不调用sync避免LOCKED)
 * @param amount JM数量
 * @param sourceType 来源类型: 0=买入, 1=卖出, 2=撤池子
 *
 * [调用者]
 *   仅限 JMTokenV2 合约
 *
 * [处理流程]
 *   1. 验证调用者为 JMTokenV2
 *   2. 将 JM 直接转给 Pair 合约
 *   3. [不调用sync] 避免 swap 期间的 LOCKED 错误
 *   4. 触发事件
 *
 * [sync触发机制]
 *   - swap场景: 只转代币, 不sync, 由普通转账触发sync
 *   - 普通转账: JMTokenV2调用trySync()触发sync更新储备
 */
```

清理后:
```solidity
/**
 * @dev 接收 JM 手续费并注入池子 (swap期间不调用sync避免LOCKED)
 * @param amount JM数量
 * @param sourceType 来源: 0=买入, 1=卖出, 2=撤池子
 */
```

### 3. 事件注释 - 删除冗余的参数说明

清理前:
```solidity
/**
 * @dev JM 注入事件
 * @param amount 注入数量
 * @param sourceType 来源: 0=买入, 1=卖出, 2=撤池子
 */
event JMInjected(uint256 amount, uint8 sourceType);
```

清理后:
```solidity
event JMInjected(uint256 amount, uint8 sourceType);
```

### 4. 简单函数 - 删除注释

清理前:
```solidity
/**
 * @dev 构造函数
 * @param _jmToken JM代币地址
 * @param _lpPair PancakePair地址
 */
constructor(address _jmToken, address _lpPair) Ownable(msg.sender) {

/**
 * @dev 紧急提取 JM (仅owner)
 * @param amount 提取数量
 */
function emergencyWithdraw(uint256 amount) external onlyOwner {
```

清理后:
```solidity
constructor(address _jmToken, address _lpPair) Ownable(msg.sender) {

function emergencyWithdraw(uint256 amount) external onlyOwner {
```

### 5. 内部实现注释 - 删除详细流程, 保留关键逻辑

清理前:
```solidity
/**
 * @dev 尝试调用sync更新Pair储备 (普通转账时触发)
 *
 * [调用者]
 *   仅限 JMTokenV2 合约
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
        // sync失败(极少见), 下次转账时会再次尝试
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

## 检查清单

### 应该删除的注释

- [ ] 详细的步骤流程 (1, 2, 3, 4...)
- [ ] 重复描述函数功能的注释
- [ ] 事件参数的 @param 说明
- [ ] 简单的构造函数/owner函数的注释
- [ ] 内部实现细节的长篇说明
- [ ] ASCII 图表装饰性注释
- [ ] 已删除代码相关的遗留注释

### 应该保留的注释

- [ ] 合约级别的核心机制说明
- [ ] 复杂的数学计算公式
- [ ] 函数的一行功能描述
- [ ] 参数和返回值的 @param/@return
- [ ] 非显而易见的业务逻辑解释
- [ ] 重要的安全警告或注意事项

## 清理流程

1. 识别冗长注释 - 超过 10 行的函数注释通常是目标
2. 保留核心 - 提取最关键的 1-2 行描述
3. 删除示例 - 删除详细的示例说明
4. 简化流程 - 将多步骤流程合并为简短描述
5. 编译验证 - 确保清理后代码仍能编译

## 效果对比

| 合约 | 清理前 | 清理后 | 减少比例 |
|------|--------|--------|----------|
| LPDistributor.sol | ~908行 | 616行 | 32% |
| LiquidityBackflowPool.sol | 120行 | 70行 | 42% |

## 注意事项

1. 不要删除 NatSpec - @title, @dev, @param, @return 是标准文档
2. 保留复杂逻辑 - 涉及数学计算或状态变更的关键逻辑要注释
3. 业务逻辑优先 - 业务相关的约束条件要保留说明
4. 逐步清理 - 建议分多次提交, 便于回滚
