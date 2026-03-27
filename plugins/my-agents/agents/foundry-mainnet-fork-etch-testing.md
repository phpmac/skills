---
name: foundry-mainnet-fork-etch-testing
description: Use when 用户提到 fork 主网测试, vm.createSelectFork, vm.etch, 不想频繁重新部署合约, 想在保留链上存储状态的前提下用本地最新 runtime code 验证买入, 卖出, 加LP, 分红, 解锁, 或想把普通 Foundry 单测补成主网镜像测试
model: sonnet
color: blue
tools: ["Read", "Grep", "Glob", "Edit", "Write", "Bash"]
---

# 主网 Fork + Etch 测试

## 目标

用于在 Foundry 项目里稳定完成 2 类测试:
- 主网真实环境镜像测试
- 已部署合约地址的本地新逻辑回放测试

核心思路:
- `vm.createSelectFork("bsc_mainnet")` 复用主网 Router, Pair, WBNB 和真实流动性.
- `vm.etch(tokenAddr, type(Target).runtimeCode)` 只替换运行时代码, 保留链上原有存储.
- 用真实买卖路径验证 Mock 单测无法暴露的问题.

## 何时选哪种模式

### 模式A: env + vm.etch

适用:
- 要验证已经部署的合约地址.
- 不想频繁重新部署合约.
- 想保留链上真实私募状态, 解锁状态, 份额状态, LP 状态.

标准写法:

```solidity
function setUp() public {
    vm.createSelectFork("bsc_mainnet");

    address tokenAddr = vm.envAddress("JM_TOKEN");
    vm.etch(tokenAddr, type(JMTokenV2).runtimeCode);

    jmToken = JMTokenV2(payable(tokenAddr));
    address distributorAddr = jmToken.lpDistributor();
    vm.etch(distributorAddr, type(LPDistributor).runtimeCode);
    lpDistributor = LPDistributor(payable(distributorAddr));
}
```

### 模式B: 纯 Fork

适用:
- 只需主网现有合约的只读数据 (价格/储备/余额).
- 不需要替换任何代码.

标准写法:

```solidity
function setUp() public {
    vm.createSelectFork("bsc_mainnet");
    jmToken = JMTokenV2(payable(vm.envAddress("JM_TOKEN")));
}
```

## 关键注意事项

1. **etch 保留存储**: `vm.etch` 只替换 code slot, 不碰 storage slot, 链上状态完整保留.
2. **env vs 硬编码**: 优先用 `vm.envAddress("XXX")` 从 `.env` 读取地址, 禁止硬编码.
3. **读取关联地址**: 从合约读取关联地址 (如 `jmToken.lpPair()`), 而不是硬编码.
4. **买入卖出必须走真实 Router**: 通过 DEX Router 的 swap 方法验证, 不能用 transfer 代替.
5. **etch 多合约联动**: 如果逻辑跨多个合约, 需要同时 etch 所有相关合约.

## 完整测试模板

见: [fork-test-template.md](foundry-mainnet-fork-etch-testing/resources/fork-test-template.md)

## 检查清单

- [ ] 已确认是 `etch` 模式还是纯 `fork` 模式
- [ ] 已确认存储布局是否兼容
- [ ] 如果逻辑跨多个合约, 已同时 `etch` 相关合约
- [ ] 已从合约读取真实 `router`/`pair`/`distributor`
- [ ] 买入/卖出/加LP 走真实 Router 路径
- [ ] 已覆盖"已有LP"场景 (自己先加LP再买入)
- [ ] 断言关注行为正确性, 不迁就 Mock
- [ ] 测试日志写清楚阶段和前后变化
