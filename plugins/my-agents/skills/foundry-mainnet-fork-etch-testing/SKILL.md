---
name: foundry-mainnet-fork-etch-testing
description: Use when 用户提到 fork 主网测试, vm.createSelectFork, vm.etch, 不想频繁重新部署合约, 想在保留链上存储状态的前提下用本地最新 runtime code 验证买入, 卖出, 加LP, 分红, 解锁, 或想把普通 Foundry 单测补成主网镜像测试
---

# 主网 Fork + Etch 测试技能

## 目标

用于在 Foundry 项目里稳定完成 2 类测试:
- 主网真实环境镜像测试
- 已部署合约地址的本地新逻辑回放测试

核心思路:
- `vm.createSelectFork("bsc_mainnet")` 复用主网 Router, Pair, WBNB 和真实流动性.
- `vm.etch(tokenAddr, type(Target).runtimeCode)` 只替换运行时代码, 保留链上原有存储.
- 用真实买卖路径验证 Mock 单测无法暴露的问题.

## 何时选哪种模式

### 模式A: `env + vm.etch`

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
    router = IPancakeRouter(jmToken.pancakeRouter());
    pair = IPancakePair(jmToken.lpPair());
    wbnb = router.WETH();
}
```

### 模式B: Fork 上新部署

适用:
- 要验证新参数, 新初始化流程, 新增分红规则.
- 要做可重复, 可控的测试场景.
- 不依赖链上已有用户状态.

标准写法:

```solidity
function setUp() public {
    vm.createSelectFork("bsc_mainnet");

    jmToken = new JMTokenV2(PANCAKE_ROUTER, address(this));
    lpDistributor = new LPDistributor(address(jmToken), jmToken.lpPair());
    jmToken.setLPDistributor(address(lpDistributor));

    jmToken.addLiquidity{value: 0.02 ether}(15000 ether);
    jmToken.setTradingEnabled(true);
}
```

## 标准流程

1. 先判断目标是"验证链上旧地址"还是"验证新参数初始化".
2. **固定测试地址**: 使用固定的 `USER` 地址进行测试,确保可重复性.
3. **从合约读取关联地址**: 优先通过合约读取 `router`, `pair`, `lpDistributor` 等地址,禁止硬编码.
4. 给测试用户 `vm.deal`, 不修改其链上已有 JM 和 LP 状态.
4. 买入走真实路由:

```solidity
router.swapExactETHForTokensSupportingFeeOnTransferTokens{value: bnbAmount}(
    0,
    path,
    user,
    block.timestamp + 300
);
```

5. 卖出走真实路由:

```solidity
jmToken.approve(address(router), jmAmount);
router.swapExactTokensForETHSupportingFeeOnTransferTokens(
    jmAmount,
    0,
    path,
    user,
    block.timestamp + 300
);
```

6. 官方加 LP 入口, 直接让用户转 BNB 到代币合约:

```solidity
(bool success, ) = payable(address(jmToken)).call{value: amount}("");
assertTrue(success);
```

7. 断言只抓核心结果, 不要对主网浮动状态写死过细数值.
8. 如果逻辑跨多个已部署合约, 要一起 `etch`, 不要只替换 `JMTokenV2`.
9. 必须补一类真实场景: 用户已经有官方LP, 已经有 `JMB/pendingReward`, 再次自己买入触发领取. 这类场景最容易在 mock 中漏掉.

## 推荐断言

### 买入

- `BNB` 下降
- `JM` 上升
- 如果是私募用户, `isUnlocked(user)` 是否按预期变化
- 合约手续费, 黑洞销毁是否增加

### 卖出

- `JM` 下降
- `BNB` 上升
- 卖出过程不能异常
- 分红池 `WBNB` 或用户 `JMB` 是否增加

### 官方加LP

- `shares(user) > 0`
- `getTrackedOfficialLP(user) > 0`
- 满足条件时可参与分红

### 网页端加LP

- `getTrackedOfficialLP(user) == 0`
- `shares(user) == 0`
- `JMB == 0`

## 关键风险

- `vm.etch` 只替换 runtime code, 不会执行构造函数.
- 只有在存储布局兼容时才使用 `vm.etch`.
- 如果新增, 删除, 重排了状态变量, 先不要直接 `etch`, 应先重新部署镜像合约测试.
- 真实 Fork 会暴露 Mock 看不到的 DEX 状态问题, 比如重入式 swap, reserve 时序, 税费路径冲突.

## 命名建议

- 验证链上旧地址行为: `UserBuyForkTest.t.sol`, `UserSellTriggerRewardForkTest.t.sol`
- 验证新逻辑主网镜像: `JMTest1Fork.t.sol`, `JMTest2Fork.t.sol`, `JMTest3Fork.t.sol`
- 公共基类: `JMMainnetForkBase.t.sol`

## 命令规范

单文件:

```bash
set -a && source .env && set +a && forge test --match-path test/jm/UserSellTriggerRewardForkTest.t.sol -vvvv --rpc-url bsc_mainnet
```

批量:

```bash
set -a && source .env && set +a && forge test --match-path "test/jm/JMTest*Fork.t.sol" -vvv --rpc-url bsc_mainnet
```

## 最小检查清单

- [ ] 已确认是 `etch` 模式还是新部署模式
- [ ] 已确认存储布局是否兼容
- [ ] 如果逻辑跨多个合约, 已同时 `etch` 相关合约
- [ ] 已从合约读取真实 `router/pair/distributor`
- [ ] 买入, 卖出, 官方加LP 走的都是真实路径
- [ ] 已覆盖"已有LP + 已有JMB + 自己再次买入"真实场景
- [ ] 断言关注行为正确性, 不迁就 Mock
- [ ] 测试日志写清楚阶段和前后变化

## 模板

见: [resources/fork-test-template.md](resources/fork-test-template.md)
