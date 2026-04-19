# AMM 定点数学溢出检查绕过

**关键词**: checked-shlw, overflow-check-bypass, MSB-truncation, fixed-point-math, CLMM-liquidity, tick-math, left-shift-overflow, Move-u256, flash-loan-drain

**来源URL**:
- Dedaub 深度分析: https://dedaub.com/blog/the-cetus-amm-200m-hack-how-a-flawed-overflow-check-led-to-catastrophic-loss/
- Ottersec Aptos 审计报告: https://github.com/CetusProtocol/Audit/blob/main/Cetus%20Aptos%20Audit%20Report%20by%20OtterSec.pdf
- Ottersec Sui 审计报告: https://github.com/CetusProtocol/Audit/blob/main/Cetus%20Sui%20Audit%20Report%20by%20OtterSec.pdf
- Zellic 审计报告: https://github.com/CetusProtocol/Audit/blob/main/CetusProtocol%20-%20Zellic%20Audit%20Report.pdf
- 攻击交易: https://suivision.xyz/txblock/DVMG3B2kocLEnVMDuQzTYRgjwuuFSfciawPvXXheB3x

**适用范围**: 所有使用定点数学的 CLMM (集中流动性) AMM, 特别是 Move (Sui/Aptos) 和 Solidity 中自定义 u256 运算库的协议

## 漏洞原理

CLMM AMM 的流动性计算涉及 `liquidity * price_diff` 等大数乘法, 中间结果可能超过 192 位. 协议通常实现 `checked_shlw` (带检查的左移) 来防止溢出, 但检查逻辑本身存在缺陷时, 溢出被静默忽略, 导致:
- 天文数字的中间值经左移截断后变成极小值
- 攻击者用 1 个 token 就能铸造巨量流动性头寸
- 移除流动性时掏空整个资金池

```solidity
// 伪代码: 有缺陷的溢出检查 (Move 原始代码的 Solidity 等价)
function checked_shlw(uint256 n) internal pure returns (uint256 result, bool overflow) {
    uint256 mask = 0xffffffffffffffff << 192; // bug: mask 值不等于 2^192
    if (n > mask) {
        return (0, true);
    } else {
        return (n << 64, false); // 移位溢出但未触发 revert
    }
}

// 攻击路径:
// liquidity ~ 2^113, price_diff ~ 2^79
// liquidity * price_diff = 2^192 + epsilon
// (2^192 + epsilon) << 64 溢出 256 位, 截断为 epsilon
// epsilon / denominator ~ 0 --> 只需 1 token 铸造巨量 LP
```

**触发条件**:
1. 语言中左移 (`<<`) 溢出不触发 abort/revert (Move, Solidity `unchecked` 块)
2. 自定义溢出检查的边界值计算错误
3. CLMM 的 tick 范围允许极端价格差, 导致中间值超大

## 变种与衍生

**变种1: mask 常量计算错误 (Cetus 模式)**
- 溢出检查中的 mask 值不等于目标阈值, 大多数超限值通过检查
- 差异: 逻辑结构正确但常量错误, 审计时容易扫一眼就跳过
- 检测要点: 手动验证 mask 的二进制表示是否匹配预期的位数边界

**变种2: 检查了溢出但用了错误分支**
- `checked_shlw` 返回溢出标志, 但调用方 `assert!(!overflowing)` 写反了, 或检查了但继续执行
- 差异: 逻辑运算符错误 (`!` 遗漏), 或 assert 后仍有代码路径绕过
- 检测要点: 搜索所有 checked 操作的返回值处理, 确认 assert 条件正确

**变种3: 移植代码时底层整数语义差异**
- 同一算法从 Aptos (自定义 u256) 移植到 Sui (原生 u256), checked 函数需重写但引入 bug
- 差异: 跨链移植特有, 审计常假设"已审计过的代码"无风险
- 检测要点: 对比移植前后的 checked 算术函数, 逐行验证

**变种4: Solidity unchecked 块内的定点乘法溢出**
- Solidity 0.8+ 中 `unchecked { a * b >> offset }` 左移溢出不 revert
- 差异: 与 Move 同理, 左移/右移在 checked arithmetic 中是唯一的静默溢出操作
- 检测要点: 搜索所有 `unchecked` 块内的位移和乘法组合

## 审计检查清单

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 1 | 验证所有自定义 checked_mul/checked_shl/checked_shlw 的边界常量是否精确 | 高 |
| 2 | 搜索所有 `<<` 左移操作, 确认溢出是否被正确捕获 | 高 |
| 3 | 检查 CLMM 的 tick 范围限制, 评估极端 tick 下中间值是否超出位宽 | 高 |
| 4 | 对比跨链移植前后的算术库, 逐行验证 checked 函数 | 高 |
| 5 | 验证 assert/require 的条件是否正确 (没有写反) | 高 |
| 6 | 用 type.MAX 值对定点数学函数做 fuzz 测试 | 中 |
| 7 | 检查 `unchecked` 块内是否有左移操作 | 中 |
| 8 | 验证 liquidity/delta 计算是否有上限约束 | 中 |

## 检测方法

1. **Grep 搜索**:
   - Move: `checked_shlw`, `checked_shl`, `<< 64`, `<< 128`, `<< 192`
   - Solidity: `unchecked.*<<`, `<<\s*\d+` 在 u256 上下文中
   - 搜索 mask 常量: `0xffffffffffffffff << 192`

2. **形式化验证思路**:
   ```
   // 不变量: 对于所有合法的 (liquidity, sqrt_price_0, sqrt_price_1),
   //         get_delta_a 返回值必须 >= 真实所需 token 数量
   //         如果溢出则必须 abort, 不能返回截断值
   //
   // 验证方法: 用 SMT solver 检查是否存在输入使
   //         (liquidity * price_diff) << 64 溢出但 checked_shlw 未检测到
   ```

3. **Foundry/Move 测试框架**:
   ```solidity
   // 测试极端 tick 范围下的流动性计算
   function testExtremeTickOverflow() public {
       uint128 liquidity = type(uint128).max / 2;
       uint128 sqrtPriceDiff = type(uint128).max / 2;
       uint256 product = fullMul(liquidity, sqrtPriceDiff);
       // 验证: 如果 product > 2^192, 必须 revert
       vm.expectRevert();
       amm.getDeltaA(sqrtPrice0, sqrtPrice1, liquidity, true);
   }

   // 测试 mask 常量正确性
   function testMaskValue() public {
       uint256 expectedMask = type(uint256).max << 192;
       assertEq(MASK, expectedMask);
   }
   ```

## 真实案例

| 事件 | 日期 | 损失 | 根因 | 攻击链 |
|------|------|------|------|--------|
| Cetus AMM (Sui) | 2025-05-22 | ~$223M | `checked_shlw` 的 mask 常量错误, 左移溢出未检测, 1 token 铸造巨量 LP | Flash Swap haSUI -> 极端 tick [300000,300200] -> dust liquidity -> 移除掏空池子 |
| Cetus AMM (Aptos, 早期版本) | 2023年初 | 未触发 (审计发现) | 同类溢出, `shlw` 未做 checked, Ottersec 审计发现并修复 | 审计阶段发现, 未被利用 |
