---
name: hardhat-v3-fork-testing
description: 当用户使用 Hardhat v3 + Foundry 风格在 Fork 主网环境下测试已部署合约时应使用此技能
metadata: {"clawdbot":{"emoji":"blue","os":["darwin","linux"],"requires":{"bins":["bun"]},"install":[{"id":"bun","kind":"bash","raw":"curl -fsSL https://bun.sh/install | bash","bins":["bun"],"label":"安装 bun"}]}}
---

# Hardhat v3 Fork 单元测试

使用 Hardhat v3 + Foundry 风格在 Fork 主网环境下进行 Solidity 智能合约测试.

## 工具预检

| 工具 | 用途 | 检测命令 |
|------|------|----------|
| bun | 包管理/运行测试 | `which bun` |

- 任何工具缺失 -> 立即停止, 报告用户安装后再继续

## When to Use

- 测试与已部署合约的交互
- 模拟任意地址 (无需私钥)
- 验证升级后的合约兼容性
- 在真实链状态上测试复杂交互

**不使用:** 简单的单元测试 / 不依赖链状态的逻辑测试

## 测试文件命名

- `*Fork.t.sol` - Fork 主网已部署合约测试
- Hardhat 3 Solidity 测试只识别 `.t.sol` 结尾的文件

## 核心原则

1. **Fork 创建**: 在 `setUp()` 中使用 `vm.createSelectFork(rpcUrl)`
2. **合约地址**: 使用主网真实合约地址作为常量
3. **接口定义**: 在测试合约外部定义接口
4. **模拟账户**: 使用 `vm.deal()` 给主网地址充值 ETH/BNB
5. **完整模拟**: 使用 `vm.prank(sender, origin)` 完整模拟合约调用
6. **注释**: 使用中文注释说明测试目的
7. **console.log**: 使用中文输出关键信息

## 测试合约模板

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {Test, console} from "forge-std/Test.sol";

interface IERC20 {
    function name() external view returns (string memory);
    function symbol() external view returns (string memory);
    function decimals() external view returns (uint8);
    function balanceOf(address) external view returns (uint256);
}

contract ForkTest is Test {
    address public constant USDT = 0x55d398326f99059fF775485246999027B3197955;

    IERC20 public usdt;

    function setUp() public {
        // 创建 BSC 主网 Fork
        vm.createSelectFork("https://bsc-dataseed.defibit.io");

        // 绑定主网合约接口
        usdt = IERC20(USDT);
    }

    /**
     * @notice [测试] 读取主网 USDT 基本信息
     */
    function test_ReadUSDTInfo() public view {
        string memory name = usdt.name();
        string memory symbol = usdt.symbol();

        console.log(string.concat(unicode"USDT 名称: ", name));
        console.log(string.concat(unicode"USDT 符号: ", symbol));

        assertEq(symbol, "USDT");
    }
}
```

## 关键 Cheatcodes

| Cheatcode | 说明 |
|-----------|------|
| `vm.createSelectFork(url)` | 创建并切换到指定 RPC 的 Fork |
| `vm.deal(addr, amount)` | 给地址设置 ETH/BNB 余额 |
| `vm.prank(sender, origin)` | 完整模拟 (sender, origin) 调用 |
| `vm.roll(blockNumber)` | 设置区块高度 |
| `vm.warp(timestamp)` | 设置区块时间戳 |

## 运行测试

```bash
# 运行所有测试
bunx hardhat test solidity

# 运行单个 Fork 测试文件
bunx hardhat test solidity contracts/MyContractForkTest.t.sol

# 运行指定测试函数
bunx hardhat test solidity contracts/MyContractForkTest.t.sol --grep "test_MyFunction"

# 显示详细输出
bunx hardhat test solidity contracts/MyContractForkTest.t.sol -vv
```

## 实战技巧

### EOA 修饰符绕过

合约使用 `onlyEOA` 检查 `tx.origin == _msgSender()` 时, 使用双参数 `vm.startPrank`:

```solidity
// 正确
vm.startPrank(user, user);
contract.someFunction();
vm.stopPrank();

// 错误
vm.prank(user);
contract.someFunction();
```

### console.log 注意事项

多个参数会换行显示, 分开调用:

```solidity
// 正确
console.log(unicode"用户:");
console.log(user);

// 错误
console.log(unicode"用户:", user);
```

### console.log 辅助函数

参考资源: [console-helpers.sol](hardhat-v3-fork-testing/resources/console-helpers.sol)

复制辅助函数到测试合约, 直接调用:

```solidity
function test_Example() public {
    _logStage(unicode"阶段1: 获取数据");
    _logLine(unicode"    [用户余额]", beforeBalance, afterBalance);
    _logStage(unicode"通过");
}
```

输出:
```
  -> 阶段1: 获取数据
    [用户余额] 0 +100 = 100
  -> 通过
```

## 注意事项

1. **Fork 不持久**: 每个测试函数执行后 Fork 状态重置
2. **RPC 稳定**: 确保 RPC 节点可用, 建议使用稳定的公共节点
3. **主网状态变化**: Fork 的是特定区块, 主网状态变化不影响已执行的测试
4. **无常方法**: Fork 中修改合约状态无效 (调用的是远程合约)
