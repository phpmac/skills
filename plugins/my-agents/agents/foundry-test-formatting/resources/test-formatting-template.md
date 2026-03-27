# Foundry 测试格式化模板

这是一个完整的测试文件模板,包含所有数值格式化辅助函数.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "forge-std/Test.sol";

/**
 * @title 格式化输出测试模板
 * @dev 包含完整的数值格式化和日志输出辅助函数
 */
contract FormattedTestTemplate is Test {
    // ============================================
    // 格式化辅助函数
    // ============================================

    /**
     * @dev 将 wei 转换为带小数点的可读格式 (18位精度)
     * 例如: 6000000000000000000000 -> "6000"
     *       200000000000000000 -> "0.2"
     *       1234567890123456789 -> "1.234567890123456789"
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

    /**
     * @dev 带单位的格式化
     */
    function _formatWithUnit(uint256 value, string memory unit) internal pure returns (string memory) {
        return string.concat(_formatEther(value), " ", unit);
    }

    // ============================================
    // 日志输出辅助函数
    // ============================================

    /**
     * @dev 输出阶段分隔
     */
    function _logStage(string memory title) internal pure {
        console.log("");
        console.log(string.concat("  -> ", title));
    }

    /**
     * @dev 按单行输出 前 +/- 变化 = 后
     */
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

    /**
     * @dev 简单的键值对输出
     */
    function _logValue(string memory label, uint256 value) internal pure {
        console.log(string.concat(label, ": "), _formatEther(value));
    }

    function _logValueWithUnit(string memory label, uint256 value, string memory unit) internal pure {
        console.log(string.concat(label, ": "), _formatEther(value), " ", unit);
    }

    // ============================================
    // 使用示例
    // ============================================

    function test_ExampleUsage() public {
        console.log(unicode"=== 格式化输出示例 ===");

        _logStage(unicode"阶段1 -> 数值格式化展示");

        // 直接格式化数值
        console.log(unicode"    [示例1] 6000 JM:", _formatEther(6000 ether));
        console.log(unicode"    [示例2] 0.2 BNB:", _formatEther(0.2 ether));
        console.log(unicode"    [示例3] 1.5 USD:", _formatEther(1.5 ether));

        _logStage(unicode"阶段2 -> 带单位的格式化");

        // 带单位的格式化
        console.log(
            unicode"    [带单位] ",
            _formatWithUnit(100 ether, "JM")
        );

        _logStage(unicode"阶段3 -> 余额变化展示");

        // 模拟余额变化
        uint256 balanceBefore = 1 ether;
        uint256 balanceAfter = 0.8 ether;

        _logLine(unicode"    [用户余额][BNB]:", balanceBefore, balanceAfter);

        _logStage(unicode"阶段4 -> 键值对输出");

        _logValueWithUnit(unicode"    [私募价格]", 0.2 ether, unicode"BNB");
        _logValueWithUnit(unicode"    [获得代币]", 6000 ether, unicode"JM");

        console.log("");
        console.log(unicode"[通过] 所有格式化输出正常");
    }
}
```

## 快速复制版本

如果你只需要核心函数,复制这个:

```solidity
// 核心格式化函数
function _formatEther(uint256 value) internal pure returns (string memory) {
    if (value == 0) return "0";
    uint256 intPart = value / 1e18;
    uint256 decPart = value % 1e18;
    if (decPart == 0) return vm.toString(intPart);
    string memory decStr = _trimTrailingZeros(decPart);
    if (bytes(decStr).length == 0) return vm.toString(intPart);
    return string.concat(vm.toString(intPart), ".", decStr);
}

function _trimTrailingZeros(uint256 value) internal pure returns (string memory) {
    string memory str = _toStringPadded(value, 18);
    bytes memory b = bytes(str);
    uint256 end = b.length;
    while (end > 0 && b[end - 1] == "0") end--;
    bytes memory r = new bytes(end);
    for (uint256 i = 0; i < end; i++) r[i] = b[i];
    return string(r);
}

function _toStringPadded(uint256 value, uint256 len) internal pure returns (string memory) {
    string memory str = vm.toString(value);
    bytes memory b = bytes(str);
    if (b.length >= len) return str;
    bytes memory r = new bytes(len);
    uint256 pad = len - b.length;
    for (uint256 i = 0; i < pad; i++) r[i] = "0";
    for (uint256 i = 0; i < b.length; i++) r[pad + i] = b[i];
    return string(r);
}

// 日志辅助函数
function _logStage(string memory title) internal pure {
    console.log("");
    console.log(string.concat("  -> ", title));
}

function _logLine(string memory label, uint256 before, uint256 after) internal pure {
    bool up = after >= before;
    uint256 d = up ? after - before : before - after;
    console.log(string.concat(label, " ", _formatEther(before), up ? " +" : " -", _formatEther(d), " = ", _formatEther(after)));
}
```
