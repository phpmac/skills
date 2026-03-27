// ========== Forge Console 辅助函数 ==========
// 用途: 解决 Forge console.log 不支持多参数混合输出的问题
// 使用: 复制到测试合约中, 直接调用 _logStage() 和 _logLine()

/// @dev 输出阶段分隔, 让日志更容易按流程阅读
/// @param title 阶段标题, 如 "阶段1: 获取价格"
function _logStage(string memory title) internal pure {
    console.log(unicode"");
    console.log(string.concat("  -> ", title));
}

/// @dev 按单行输出 前 +/- 变化 = 后 (带格式化)
/// @param label 标签, 如 "    [用户余额]"
/// @param beforeValue 变化前的值
/// @param afterValue 变化后的值
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

/// @dev 将 wei 转换为带小数点的可读格式 (18位精度)
/// @param value 以 wei 为单位的值
/// @return 格式化的字符串, 如 "123.456"
function _formatEther(uint256 value) internal pure returns (string memory) {
    if (value == 0) return "0";

    uint256 integerPart = value / 1e18;
    uint256 decimalPart = value % 1e18;

    if (decimalPart == 0) {
        return vm.toString(integerPart);
    }

    string memory decimalStr = _trimTrailingZeros(decimalPart);
    return string.concat(vm.toString(integerPart), ".", decimalStr);
}

function _trimTrailingZeros(uint256 value) internal pure returns (string memory) {
    string memory str = _toStringPadded(value, 18);
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

function _toStringPadded(uint256 value, uint256 length) internal pure returns (string memory) {
    string memory str = vm.toString(value);
    bytes memory strBytes = bytes(str);

    if (strBytes.length >= length) {
        return str;
    }

    bytes memory result = new bytes(length);
    uint256 padding = length - strBytes.length;

    for (uint256 i = 0; i < padding; i++) {
        result[i] = bytes1("0");
    }
    for (uint256 i = 0; i < strBytes.length; i++) {
        result[padding + i] = strBytes[i];
    }

    return string(result);
}
