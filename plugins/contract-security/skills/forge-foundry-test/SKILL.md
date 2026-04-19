---
name: forge-foundry-test
description: 当用户要求编写 Foundry 单元测试, Fork 主网测试, vm.createSelectFork, vm.etch, 格式化测试输出, 数值格式化, 或需要在真实链状态上测试合约时应使用此技能
metadata: {"clawdbot":{"emoji":"blue","os":["darwin","linux"],"requires":{"bins":["forge"]},"install":[{"id":"forge","kind":"bash","raw":"curl -L https://foundry.paradigm.xyz | bash && foundryup","bins":["forge","cast"],"label":"安装 Foundry (forge/cast)"}]}}
---

# Forge Foundry 测试

## 工具预检

| 工具 | 用途 | 检测命令 |
|------|------|----------|
| forge | 编译/测试 | `which forge` |

- 工具缺失 -> 立即停止, 报告用户安装后再继续

---

## 1. 本地单元测试

标准 Foundry 测试, 不依赖链上状态.

### 测试文件命名

| 命名模式 | 用途 |
|----------|------|
| `*Test.t.sol` | 普通单元测试 |
| `*Fork.t.sol` | Fork 主网测试 |

### 运行命令

```bash
# 运行所有测试
forge test -vvv

# 运行指定文件
forge test --match-path test/MyTest.t.sol -vvv

# 运行指定函数
forge test --match-test test_FunctionName -vvv

# 离线模式 (不连接网络)
forge test --match-test testFunc -vvv --offline

# 过滤输出
forge test --match-test testFunc -vvv --offline 2>&1 | grep -E "(阶段|结果|Error)" | head -40
```

---

## 2. Fork 主网测试

使用主网真实状态测试已部署合约, 分两种模式:

### 模式A: Fork + vm.etch (推荐)

替换链上合约的运行时代码, 保留链上真实存储. 适合:
- 验证已部署合约地址
- 不想频繁重新部署
- 保留链上真实私募/LP/解锁状态

```solidity
function setUp() public {
    vm.createSelectFork("bsc_mainnet");

    address tokenAddr = vm.envAddress("JM_TOKEN");
    vm.etch(tokenAddr, type(JMTokenV2).runtimeCode);

    jmToken = JMTokenV2(payable(tokenAddr));
    // 从合约读取关联地址, 禁止硬编码
    router = IPancakeRouter(jmToken.pancakeRouter());
    pair = IPancakePair(jmToken.lpPair());
}
```

### 模式B: 纯 Fork

只读取主网数据, 不替换代码. 适合:
- 只需只读数据 (价格/储备/余额)
- 不需要替换任何合约逻辑

```solidity
function setUp() public {
    vm.createSelectFork("bsc_mainnet");
    jmToken = JMTokenV2(payable(vm.envAddress("JM_TOKEN")));
}
```

### 关键 Cheatcodes

| Cheatcode | 说明 |
|-----------|------|
| `vm.createSelectFork(rpc)` | 创建并切换到 Fork |
| `vm.etch(addr, runtimeCode)` | 替换合约代码, 保留存储 |
| `vm.deal(addr, amount)` | 设置地址余额 |
| `vm.prank(sender, origin)` | 模拟调用 (双参数解决 onlyEOA) |
| `vm.roll(blockNumber)` | 设置区块高度 |
| `vm.warp(timestamp)` | 设置区块时间戳 |
| `vm.envAddress("KEY")` | 从 .env 读取地址 |

### Fork 注意事项

1. **etch 保留存储**: 只替换 code slot, 不碰 storage slot
2. **env 优先**: 用 `vm.envAddress()` 读取地址, 禁止硬编码
3. **关联地址从合约读**: `jmToken.lpPair()` 而非硬编码
4. **买卖走真实 Router**: 通过 DEX Router swap 验证, 不用 transfer 代替
5. **多合约联动**: 逻辑跨合约时需同时 etch 所有相关合约
6. **Fork 不持久**: 每个测试函数执行后状态重置

### Fork 完整模板

见: [fork-test-template.md](references/fork-test-template.md)

### 检查清单

- [ ] 确认 etch 模式还是纯 fork 模式
- [ ] 存储布局是否兼容
- [ ] 多合约联动时已同时 etch
- [ ] 从合约读取真实 router/pair/distributor
- [ ] 买卖加LP走真实 Router 路径
- [ ] 已覆盖"已有LP"场景
- [ ] 测试日志写清楚阶段和前后变化

---

## 3. 测试输出格式化

解决 `console.log` 直接输出 uint256 原始 wei 值的问题:

```
// 原始输出
用户余额: 200000000000000000

// 格式化后
用户余额: 0.2 BNB
```

### 格式化函数

| 函数 | 用途 | 示例 |
|------|------|------|
| `_formatEther(value)` | wei 转可读格式 | `200000000000000000` -> `"0.2"` |
| `_logStage(title)` | 阶段分隔 | `  -> 阶段名称` |
| `_logLine(label, before, after)` | 数值变化 | `[余额]: 1 +0.5 = 1.5` |
| `_logValue(label, value)` | 键值对 | `价格: 0.2` |
| `_formatWithUnit(value, unit)` | 带单位 | `"0.2 BNB"` |

### 使用示例

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

输出效果:
```
=== 私募测试 ===

  -> 阶段1 -> 准备账户
    [用户][BNB]: 0 +1 = 1

  -> 阶段2 -> 执行私募
    [私募价格]: 0.2 BNB

  -> 阶段3 -> 验证结果
    [用户获得JM]: 6000 JM
```

### console.log 注意事项

- 多参数会换行显示, 分开调用
- 混合输出用 `string.concat(unicode"中文", vm.toString(value))`
- 显示地址: `console.log(string.concat(unicode"    [用户地址]: ", vm.toString(user)))`

### 格式化完整模板

见: [test-formatting-template.md](references/test-formatting-template.md)

### 注意事项

- `_formatEther()` 假设精度 18 位, 非 18 位需调整除数
- 仅用于测试环境, 不用于生产合约
