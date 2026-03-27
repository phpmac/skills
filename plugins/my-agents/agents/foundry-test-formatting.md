---
name: foundry-test-formatting
description: Use when 用户提到 Foundry 单元测试输出格式化, 数值格式化显示小数点, console.log 格式化 ether, 想美化测试日志输出, 处理 uint256 数值可读性
model: sonnet
color: blue
tools: ["Read", "Grep", "Glob", "Edit", "Write", "Bash"]
---

# Foundry 测试输出格式化

在 Foundry 单元测试中格式化数值输出的代码实现模板.

提供 `_formatEther()` (wei 转可读格式), `_logStage()` (阶段分隔), `_logLine()` (数值变化输出).

## 核心问题

Foundry 的 `console.log` 直接输出 `uint256` 时显示为原始 wei 值:
```
// 原始输出
用户余额: 200000000000000000

// 期望输出
用户余额: 0.2 BNB
```

## 代码模板

### 1. 基础格式化函数

```solidity
/**
 * @dev 将 wei 转换为带小数点的可读格式 (18位精度)
 * 例如: 6000000000000000000000 -> "6000"
 *       200000000000000000 -> "0.2"
 */
function _formatEther(uint256 value) internal pure returns (string memory) {
    if (value == 0) return "0";

    uint256 integerPart = value / 1e18;
    uint256 decimalPart = value % 1e18;

    // 如果小数部分为0,只返回整数
    if (decimalPart == 0) {
        return vm.toString(integerPart);
    }

    // 将小数部分转换为字符串并去除末尾的0
    string memory decimalStr = _trimTrailingZeros(decimalPart);

    // 如果小数部分全是0,返回整数
    if (bytes(decimalStr).length == 0) {
        return vm.toString(integerPart);
    }

    return string.concat(
        vm.toString(integerPart),
        ".",
        decimalStr
    );
}

function _trimTrailingZeros(uint256 value) internal pure returns (string memory) {
    string memory str = vm.toString(value);
    bytes memory strBytes = bytes(str);
    uint256 end = strBytes.length;

    while (end > 0 && strBytes[end - 1] == bytes1("0")) {
        end--;
    }

    bytes memory result = new bytes(end);
    for (uint256 i = 0; i < end; i++) {
        result[i] = strBytes[i];
    }

    return string(result);
}
```

### 2. 阶段分隔函数

```solidity
function _logStage(string memory stage) internal pure {
    console.log(string.concat("  -> ", stage));
}
```

### 3. 数值变化输出

```solidity
function _logLine(
    string memory label,
    uint256 beforeValue,
    uint256 delta,
    uint256 afterValue
) internal pure {
    bool increased = afterValue >= beforeValue;
    console.log(string.concat(
        "    [", label, "]: ",
        _formatEther(beforeValue),
        increased ? " +" : " -",
        _formatEther(delta),
        " = ",
        _formatEther(afterValue)
    ));
}
```

### 显示用户地址 (Fork测试必备)

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
    uint256 price = jmToken.privateSalePrice();
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

## 完整模板

见: [test-formatting-template.md](foundry-test-formatting/resources/test-formatting-template.md)

## 命令行过滤

```bash
# 过滤显示阶段/结果/代币/错误信息
forge test --match-test testFunc -vvv --offline 2>&1 | grep -E "(阶段|结果|JM|Revert|Error)" | head -40
```

## 变体需求

### 带单位的格式化

```solidity
function _formatWithUnit(uint256 value, string memory unit) internal pure returns (string memory) {
    return string.concat(_formatEther(value), " ", unit);
}
// 使用: _formatWithUnit(200000000000000000, "BNB") -> "0.2 BNB"
```

## 注意事项

1. `_formatEther()` 假设精度为 18 位 (标准 ERC20)
2. 对于非 18 位精度的代币, 需要调整除数
3. 这些辅助函数会增加一点 gas 消耗, 仅用于测试环境
