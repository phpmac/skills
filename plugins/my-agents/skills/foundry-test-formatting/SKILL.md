---
name: foundry-test-formatting
description: Use when 用户提到 Foundry 单元测试输出格式化, 数值格式化显示小数点, console.log 格式化 ether, 想美化测试日志输出, 处理 uint256 数值可读性
---

# Foundry 单元测试输出格式化技能

## 目标

用于在 Foundry 单元测试中格式化数值输出, 使其更易读:
- 将 wei (1e18 精度) 转换为带小数点的可读格式
- 统一测试日志输出风格 (阶段格式 + 数值变化)
- 提供可复用的辅助函数模板

## 核心问题

Foundry 的 `console.log` 直接输出 `uint256` 时显示为原始 wei 值:
```
// 原始输出
用户余额: 200000000000000000

// 期望输出
用户余额: 0.2 BNB
```

## 解决方案

### 1. 基础格式化函数

在测试合约中添加以下辅助函数:

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

/**
 * @dev 去除小数末尾的0
 */
function _trimTrailingZeros(uint256 value) internal pure returns (string memory) {
    // 将小数部分补齐18位
    string memory str = _toStringPadded(value, 18);

    bytes memory strBytes = bytes(str);
    uint256 end = strBytes.length;

    // 从末尾开始查找第一个非零字符
    while (end > 0 && strBytes[end - 1] == "0") {
        end--;
    }

    // 截取字符串
    bytes memory result = new bytes(end);
    for (uint256 i = 0; i < end; i++) {
        result[i] = strBytes[i];
    }

    return string(result);
}

/**
 * @dev 将数字转换为固定长度的字符串,不足位在前面补0
 */
function _toStringPadded(uint256 value, uint256 length) internal pure returns (string memory) {
    string memory str = vm.toString(value);
    bytes memory strBytes = bytes(str);

    if (strBytes.length >= length) {
        return str;
    }

    // 前面补0
    bytes memory result = new bytes(length);
    uint256 padding = length - strBytes.length;

    for (uint256 i = 0; i < padding; i++) {
        result[i] = "0";
    }
    for (uint256 i = 0; i < strBytes.length; i++) {
        result[padding + i] = strBytes[i];
    }

    return string(result);
}
```

### 2. 标准日志输出格式

#### 阶段分隔
```solidity
function _logStage(string memory title) internal pure {
    console.log("");
    console.log(string.concat("  -> ", title));
}
```

#### 数值变化输出 (前 +/- 变化 = 后)
```solidity
function _logLine(
    string memory label,
    uint256 beforeValue,
    uint256 afterValue
) internal pure {
    bool increased = afterValue >= beforeValue;
    uint256 delta = increased
        ? afterValue - beforeValue
        : beforeValue - afterValue;

    console.log(
        string.concat(
            label,
            " ",
            _formatEther(beforeValue),
            increased ? " +" : " -",
            _formatEther(delta),
            " = ",
            _formatEther(afterValue)
        )
    );
}
```

#### 显示用户地址 (Fork测试必备)
```solidity
// 使用 vm.toString() 直接输出完整地址
console.log(string.concat(unicode"    [用户地址]: ", vm.toString(user)));

// 输出效果:
// [用户地址]: 0x1234567890123456789012345678901234567890
```

### 3. 使用示例

#### 基础测试
```solidity
function test_PrivateSale() public {
    console.log(unicode"=== 私募测试 ===");

    _logStage(unicode"阶段1 -> 准备账户");
    uint256 userBalanceBefore = user.balance;
    vm.deal(user, 1 ether);
    _logLine(unicode"    [用户][BNB]:", userBalanceBefore, user.balance);

    _logStage(unicode"阶段2 -> 执行私募");
    uint256 price = jmToken.privateSalePrice();
    console.log(unicode"    [私募价格]:", _formatEther(price), unicode" BNB");

    // 执行转账...

    _logStage(unicode"阶段3 -> 验证结果");
    console.log(
        unicode"    [用户获得JM]:",
        _formatEther(jmToken.balanceOf(user)),
        unicode" JM"
    );
}
```

#### Fork测试 (显示用户地址)
```solidity
function test_SellHST() public {
    console.log(unicode"=== 用户卖出 HST ===");
    console.log(string.concat(unicode"  [测试用户]: ", vm.toString(USER)));

    _logStage(unicode"阶段1 -> 查询用户余额");
    console.log(string.concat(unicode"    [用户][HST]: ", _formatEther(hst.balanceOf(USER)), unicode" HST"));
    console.log(string.concat(unicode"    [用户][USDT]: ", _formatEther(usdt.balanceOf(USER)), unicode" USDT"));

    _logStage(unicode"阶段2 -> 准备 Gas");
    uint256 bnbBefore = USER.balance;
    vm.deal(USER, 0.01 ether);
    _logLine(unicode"    [用户][BNB]:", bnbBefore, USER.balance);

    _logStage(unicode"阶段3 -> 执行卖出");
    console.log(string.concat(unicode"    [卖出数量]: ", _formatEther(sellAmount), unicode" HST"));
    // 执行卖出...

    _logStage(unicode"阶段4 -> 验证结果");
    _logLine(unicode"    [用户][HST]:", hstBefore, hst.balanceOf(USER));
    _logLine(unicode"    [用户][USDT]:", usdtBefore, usdt.balanceOf(USER));
}
```

### 4. 输出效果

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

见: [resources/test-formatting-template.md](resources/test-formatting-template.md)

## 注意事项

1. `_formatEther()` 假设精度为 18 位 (标准 ERC20)
2. 对于非 18 位精度的代币,需要调整除数
3. 极大数值 (> 2^128) 的小数部分可能会溢出,建议先检查
4. 这些辅助函数会增加一点 gas 消耗,仅用于测试环境

## 命令行过滤技巧

### 快速查看测试关键信息

当测试输出太多编译警告和无关信息时,使用 grep 过滤:

```bash
# 过滤显示阶段/结果/JM数值/错误信息
forge test --match-test testFunc -vvv --offline 2>&1 | grep -E "(阶段|结果|JM|Revert|Error)" | head -40

# 过滤显示所有关键日志关键词
forge test -vvv --offline 2>&1 | grep -E "(阶段|结果|通过|失败|Revert|Error)" | head -50

# 只看数值变化
forge test -vvv --offline 2>&1 | grep -E "(\+|-|=)" | head -30
```

**常用过滤关键词**:
- `阶段|结果|通过|失败` - 测试进度
- `JM|BNB|USDT` - 代币数值
- `Revert|Error|FAIL` - 错误信息
- `assert` - 断言相关

**好处**:
- 快速定位测试失败原因
- 省去翻阅大量警告信息的时间
- 一眼看到数值变化是否符合预期

## 变体需求

### 显示固定小数位
```solidity
function _formatEtherFixed(uint256 value, uint256 decimals) internal pure returns (string memory) {
    string memory formatted = _formatEther(value);
    // 补充或截断到指定位数
    // ...
    return formatted;
}
```

### 带单位的格式化
```solidity
function _formatWithUnit(uint256 value, string memory unit) internal pure returns (string memory) {
    return string.concat(_formatEther(value), " ", unit);
}
// 使用: _formatWithUnit(200000000000000000, "BNB") -> "0.2 BNB"
```

## 最小检查清单

- [ ] 已添加 `_formatEther()` 辅助函数
- [ ] 已添加 `_trimTrailingZeros()` 辅助函数
- [ ] 已添加 `_toStringPadded()` 辅助函数
- [ ] 数值输出使用 `_formatEther()` 格式化
- [ ] 测试日志有清晰的阶段分隔
- [ ] 余额变化使用 `_logLine()` 显示前/变化/后
