---
name: foundry-test-formatting
description: 当用户要求 "Foundry 单元测试输出格式化", "数值格式化显示小数点", "console.log 格式化 ether", "美化测试日志输出", "处理 uint256 数值可读性", 或 "格式化测试输出" 时应使用此技能
---

# Foundry 测试输出格式化

在 Foundry 单元测试中格式化数值输出, 解决 `console.log` 直接输出 uint256 原始 wei 值的问题.

## 核心问题

```
// 原始输出
用户余额: 200000000000000000

// 期望输出
用户余额: 0.2 BNB
```

## 提供的函数

| 函数 | 用途 |
|------|------|
| `_formatEther(value)` | wei 转可读格式: `200000000000000000` → `"0.2"` |
| `_logStage(title)` | 阶段分隔: `  -> 阶段名称` |
| `_logLine(label, before, after)` | 数值变化: `[余额]: 1 +0.5 = 1.5` |
| `_logValue(label, value)` | 键值对: `价格: 0.2` |
| `_formatWithUnit(value, unit)` | 带单位: `"0.2 BNB"` |

## 显示用户地址 (Fork 测试必备)

```solidity
console.log(string.concat(unicode"    [用户地址]: ", vm.toString(user)));
```

## 使用示例

```solidity
function test_PrivateSale() public {
    console.log(unicode"=== 私募测试 ===");

    _logStage(unicode"阶段1 -> 准备账户");
    uint256 userBalanceBefore = user.balance;
    vm.deal(user, 1 ether);
    _logLine(unicode"用户BNB", userBalanceBefore, user.balance);

    _logStage(unicode"阶段2 -> 执行私募");
    console.log(string.concat(unicode"    [私募价格]: ", _formatEther(price), unicode" BNB"));

    _logStage(unicode"阶段3 -> 验证结果");
    console.log(string.concat(unicode"    [用户获得JM]: ", _formatEther(jmToken.balanceOf(user)), unicode" JM"));
}
```

### 输出效果

```
=== 私募测试 ===

  -> 阶段1 -> 准备账户
    [用户][BNB]: 0 +1 = 1

  -> 阶段2 -> 执行私募
    [私募价格]: 0.2 BNB

  -> 阶段3 -> 验证结果
    [用户获得JM]: 6000 JM
```

## 命令行过滤

```bash
forge test --match-test testFunc -vvv --offline 2>&1 | grep -E "(阶段|结果|JM|Revert|Error)" | head -40
```

## 注意事项

- `_formatEther()` 假设精度为 18 位 (标准 ERC20)
- 非 18 位精度的代币需要调整除数
- 仅用于测试环境, 不用于生产合约

## 附加资源

完整模板和快速复制版本详见 `references/test-formatting-template.md`.
