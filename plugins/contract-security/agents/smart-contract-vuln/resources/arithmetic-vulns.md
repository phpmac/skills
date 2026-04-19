# 算术漏洞

**关键词**: precision-loss, divide-before-multiply, integer-overflow, integer-underflow, unchecked-block, uint256-wraparound, SafeMath, bonding-curve-exploit, AMM-math

**来源URL**:
- ConsenSys 安全最佳实践: https://consensys.github.io/smart-contract-best-practices/
- WTF-Solidity 安全专题: https://github.com/AmazingAng/WTF-Solidity
- Solidity Hacks 合集: https://github.com/chatch/solidity-hacks
- Slither 检测器文档: https://github.com/crytic/slither/wiki/Detectors

**适用范围**: 所有使用 Solidity 的智能合约, 尤其是涉及金融计算的 DeFi 协议

## 漏洞原理

Solidity 中整数除法向零截断, 不会四舍五入. 当先除后乘时, 中间结果丢失精度, 最终结果偏小, 累积后造成资金损失. Solidity 0.8.0 之前没有自动溢出检查, uint256 溢出后模 2^256 回绕.

```solidity
// 漏洞1: 先除后乘, 精度丢失
function calculateReward(uint256 amount, uint256 rate) public pure returns (uint256) {
    return amount / 1000 * rate; // 错误: 先除, 精度已丢失
}

// 正确: 先乘后除
function calculateReward(uint256 amount, uint256 rate) public pure returns (uint256) {
    return amount * rate / 1000; // 精度保留到最后一步
}

// 漏洞2: unchecked 块内溢出
function unsafeDecrement(uint256 x) public pure returns (uint256) {
    unchecked { return x - 1; } // x=0 时下溢为 type(uint256).max
}

// 漏洞3: 复杂公式溢出回绕, 天文数字变成极小值
// Bonding Curve 铸造公式
uint256 numerator = 100 * amount * amount * reserve
                  + 200 * totalSupply * amount * reserve;
return numerator / denominator; // 溢出后几乎为0
```

## 变种与衍生

**变种1: 费率计算精度损失**
- 奖励分配/手续费计算中, 小额持有者的收益被截断为零
- 差异: 影响是渐进式的, 每次操作损失微量, 但高频调用下累积显著
- 检测要点: 搜索所有除法后紧跟乘法的模式, 特别关注费率/奖励分配函数

**变种2: AMM 价格计算精度损失**
- 恒定乘积公式中, 先除后乘导致 swap 输出偏少或 LP 计算不公
- 差异: 发生在 AMM 公式内, 如 `amount * reserveIn / reserveOut` 的顺序
- 检测要点: 搜索 `*/ reserve` 或 `* totalSupply / reserve` 模式

**变种3: 时间加权平均精度丢失**
- TWAP 计算中, 累积价格除以时间间隔可能截断
- 差异: 影响预言机准确性, 可能导致价格偏差
- 检测要点: 搜索 `cumulativePrice / timeElapsed` 或类似 TWAP 计算

**变种4: unchecked 块内的非预期溢出**
- Solidity 0.8+ 的 unchecked 块绕过安全检查
- 差异: 不一定在金融计算中, 可能在循环计数器/索引计算中
- 检测要点: 搜索所有 `unchecked { }` 块, 验证边界条件

## 审计检查清单

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 1 | 搜索所有除法运算, 验证是否先除后乘 | 高 |
| 2 | Solidity 版本 <0.8.0 时, 检查所有算术运算是否有 SafeMath 保护 | 高 |
| 3 | 搜索 `unchecked` 块, 验证每个块内运算的边界条件 | 高 |
| 4 | 检查 bonding curve/AMM/借贷利率等复杂数学公式是否有中间溢出 | 高 |
| 5 | 验证费率/奖励分配函数是否对小额持有者返回零 | 中 |
| 6 | 检查 TWAP/预言机计算中除法是否截断关键精度 | 中 |
| 7 | 检查除法的除数是否可能为零 (除零错误) | 中 |
| 8 | 验证代币精度 (6/8/18/36 decimals) 是否在计算中统一 | 低 |

## 检测方法

1. **Grep 搜索**:
   - 搜索除法后紧跟乘法的模式: `/ ... *` 或 `/\d+.*\*`
   - 搜索 unchecked 块: `unchecked\s*\{`
   - 搜索复杂公式: `*.*.*` 三连乘或更多

2. **Slither 检测命令**:
   ```
   slither --detect divide-before-multiply .
   slither --detect integer-overflow-and-underflow .
   slither --detect incorrect-modifier .
   ```

3. **Foundry 边界测试框架**:
   ```solidity
   function testPrecisionLoss() public {
       // 测试小额精度
       uint256 small = 1;
       uint256 result = small / 1000 * rate;
       assertEq(result, 0); // 精度完全丢失

       // 测试先乘后除
       uint256 result2 = small * rate / 1000;
       assertGt(result2, 0); // 应该保留精度
   }
   ```

## 真实案例

| 事件 | 日期 | 损失 | 根因 | 攻击链 |
|------|------|------|------|--------|
| ERC20 代币合约 (多个) | 2018-2019 | 多次小额损失 | 先除后乘导致代币转账精度丢失 | transfer -> balance 计算 |
| bZx (v1) | 2020-02 | ~$1M | 整数溢出 + 价格操纵 | 闪电贷 + swap + 操纵价格 |
| Cover 协议 | 2020-12 | ~$6.5M | AMM 精度损失导致 LP 不公平铸造 | mint -> LP 计算 |
