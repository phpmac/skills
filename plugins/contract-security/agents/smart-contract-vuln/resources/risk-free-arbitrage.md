# 审计要点: 无风险套利

**关键词**: risk-free-arbitrage, flash-loan-attack, price-manipulation, oracle-manipulation, MEV-sandwich, harvest-front-run, yield-skimming, TWAP-bypass, spot-price-exploit, zero-cost-attack

**来源URL**:
- Dedaub Yield Skimming 研究: https://dedaub.com/blog/yield-skimming-forcing-bad-swaps-on-yield-farming/
- Alpha Homora MEV 事件: https://blog.alphaventuredao.io/mev-bots-uniswap-implicit-assumptions/
- Immunefi Web3 安全库: https://github.com/immunefi-team/Web3-Security-Library
- Zealynx Uniswap V2 安全: https://www.zealynx.io/blogs/uniswap-v2
- EigenPhi MEV 分析: https://medium.com/@eigenphi/mevs-impact-on-uniswap-c36c7dfbd3d4
- DeGatchi MEV Baiting: https://degatchi.com/articles/baiting-mev-bots-univ2-token-trapper/

**适用范围**: 所有与 AMM/DEX 交互的协议 (借贷, 收益聚合, DEX, 跨链桥, 衍生品等)

## 核心判断标准

无风险套利指攻击者在不承担任何市场风险的情况下, 利用协议设计缺陷稳定获利. 与正常套利(需承担价格波动/滑点风险)不同, 无风险套利意味着协议存在可被确定性利用的经济漏洞.

## 核心判断标准

```
无风险套利 = 确定性收益 + 零市场风险 + 可重复执行
```

正常套利: 承担滑点/gas/价格波动风险, 市场行为
无风险套利: 合约逻辑保证收益, 协议缺陷

## 漏洞原理

无风险套利的本质是: 协议的外部交互逻辑存在可被确定性利用的缺陷, 攻击者在不承担市场风险的情况下稳定获利.

核心公式: `无风险套利 = 确定性收益 + 零市场风险 + 可重复执行`

正常套利 vs 无风险套利:
- 正常: 承担滑点/gas/价格波动风险, 属于市场行为
- 无风险: 合约逻辑保证收益, 属于协议缺陷

**关键代码模式** (以 harvest 夹击为例):

```solidity
// 漏洞: harvest 公开且无滑点保护, 攻击者可操纵价格后触发
function harvest() public {
    uint256 reward = tokenA.balanceOf(address(this));
    // 任何人都能调用, 攻击者先卖砸价格再触发
    unirouter.swapExactTokensForTokens(reward, 0, path, address(this), block.timestamp);
    depositTokenB();
}
```

## 变种与衍生

**变种1: 闪电贷单tx套利**
- 触发条件: 协议使用 AMM 现货价格作为预言机
- 差异: 攻击在单笔交易内完成, 零本金, 零风险
- 检测要点: 搜索 `getSpotPrice` / `getReserves` 后直接用于金额计算的代码

```solidity
uint256 price = getSpotPrice(tokenA, tokenB); // 可被闪电贷操纵
uint256 borrowAmount = collateral * price * ltv / 10000;
```

**变种2: 同池双操作套利**
- 触发条件: mint/burn 的 LP 代币计算与实际存入金额不一致
- 差异: 在同一池中连续操作, 利用状态更新延迟
- 检测要点: 检查 mint/burn 中 fee 扣除与 LP 计算的顺序

**变种3: 跨协议状态不一致套利**
- 触发条件: 两个协议共享同一 AMM 池但更新时机不同
- 差异: 协议 A 读取 reserve 后, 协议 B 修改了 reserve, A 基于过期数据操作
- 检测要点: 搜索 `getReserves()` 后是否有跨合约调用

```solidity
function deposit() external {
    (uint112 res0, uint112 res1,) = pair.getReserves(); // T1 读取
    // ... 中间操作, reserve 可能已被修改
    uint256 shares = calculateShares(res0, res1); // T2 使用, 数据过期
}
```

**变种4: 奖励/分红抢跑套利**
- 触发条件: 协议奖励按余额/份额瞬时快照分配
- 差异: 攻击者在快照前买入大量份额, 获得奖励后立即卖出
- 检测要点: 搜索 `balanceOf` / `totalSupply` 在 reward 分配中的使用, 是否基于时间加权

**变种5: 收益合约 harvest 夹击 (主变种)**
- 触发条件: harvest 函数公开可调用, swap 时无滑点保护
- 差异: 攻击者先操纵 AMM 价格, 再触发 harvest, 合约以劣价 swap
- 检测要点: 搜索公开函数中的 swap 调用, 检查 `amountOutMin` 参数是否为 0

```solidity
// 漏洞代码: harvest 公开且无滑点保护
function harvest() public {
    uint256 reward = tokenA.balanceOf(address(this));
    // 任何人都能调用, 攻击者先卖砸价格再触发
    unirouter.swapExactTokensForTokens(reward, 0, path, address(this), block.timestamp);
    depositTokenB();
}
```

**攻击流程**:
```
1. 攻击者在 AMM 池中大额卖出 tokenA, 压低价格
2. 调用 victim.harvest(), 合约以被操纵的低价 swap
3. 攻击者在 AMM 池中买回 tokenA, 获利 = 被贱卖的收益
```

**数学分析** (Dedaub Yield Skimming):
- 当 victim swap 金额 > 池子储备的 0.3% 时, 攻击即可盈利
- victim swap 金额 = 池子储备的 10% 时, 攻击者可获取几乎全部收益
- Uniswap 0.3% 手续费是唯一成本, 大额 swap 时可忽略

**防御**:
```solidity
// 限制 harvest 调用者
function harvest() external onlyHarvester { ... }

// 或设置最低输出 (但不够, 因为价格已被操纵)
function harvest() external {
    uint256 reward = tokenA.balanceOf(address(this));
    uint256 minOut = getExpectedOutput(reward); // 链下计算
    unirouter.swapExactTokensForTokens(reward, minOut, path, address(this), block.timestamp);
}

// 最佳: 使用 TWAP 预言机获取公平价格
function harvest() external onlyHarvester {
    uint256 fairPrice = getTWAPPrice(tokenA, tokenB, 30 minutes);
    uint256 minOut = reward * fairPrice * (1000 - slippageBps) / 1000;
    unirouter.swapExactTokensForTokens(reward, minOut, path, address(this), block.timestamp);
}
```

### 2. 闪电贷单tx套利

利用闪电贷在单笔交易内完成攻击, 零本金投入, 确定性获利.

**典型场景**: 协议使用现货价格作为预言机, 闪电贷可瞬间操纵.

```solidity
// 漏洞: 使用现货价格
uint256 price = getSpotPrice(tokenA, tokenB); // 可被闪电贷操纵
uint256 borrowAmount = collateral * price * ltv / 10000;
```

**攻击流程**:
```
1. 闪电贷借入大量 tokenA
2. 在 AMM 卖出 tokenA, 操纵现货价格
3. 利用被操纵的价格从协议借出/清算/获利
4. 在 AMM 买回 tokenA 归还闪电贷
5. 净获利 (无市场风险, 全在同一 tx 内)
```

### 3. 同池双操作套利

在同一流动性池中连续操作, 利用状态更新延迟获利.

**典型场景**: mint/burn 的 LP 代币计算与实际存入金额不一致.

```solidity
// 漏洞: fee 扣除在 LP 计算之后
function mint(address to) external returns (uint liquidity) {
    uint amount0 = balance0.sub(reserve0);
    uint amount1 = balance1.sub(reserve1);
    // 扣手续费后实际存入减少, 但 LP 按扣除前计算
    uint fee0 = amount0 * feeRate / 10000;
    liquidity = Math.min(
        (amount0 - fee0) * totalSupply / reserve0,  // 正确: 用扣费后金额
        amount1 * totalSupply / reserve1              // 错误: 用扣费前金额
    );
}
```

### 4. 跨协议状态不一致套利

两个协议共享同一状态源(如 AMM 池), 但更新时机不同.

**典型场景**: 协议 A 读取 reserve 后, 协议 B 修改了 reserve, 协议 A 基于过期数据操作.

```solidity
// 漏洞: 读取 reserve 后未立即使用
function deposit() external {
    (uint112 res0, uint112 res1,) = pair.getReserves(); // 读取时刻 T1
    // ... 中间有其他操作, 此时 reserve 可能已被修改
    uint256 shares = calculateShares(res0, res1); // 使用时刻 T2, 数据已过期
}
```

### 5. 奖励/分红抢跑套利

协议奖励按余额/份额快照分配, 攻击者在快照前买入, 快照后卖出.

```solidity
// 漏洞: 奖励基于实时余额而非时间加权
function distributeReward() external {
    uint256 totalShares = token.totalSupply();
    uint256 reward = rewardToken.balanceOf(address(this));
    // 攻击者: 快照前买入大量份额 -> 获得奖励 -> 立即卖出
    for (uint i = 0; i < holders.length; i++) {
        uint256 share = token.balanceOf(holders[i]) * reward / totalShares;
        rewardToken.transfer(holders[i], share);
    }
}
```

## 审计检查清单

### 价格/预言机相关

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 1 | 协议是否使用 AMM 现货价格作为预言机 | 高 |
| 2 | 价格读取与使用之间是否存在可被利用的时间窗口 | 高 |
| 3 | 是否使用 TWAP 或 Chainlink 等抗操纵预言机 | 高 |
| 4 | 单笔交易内是否可操纵价格并完成攻击 | 高 |

### 操作权限相关

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 5 | harvest/rebalance/claim 类函数是否公开可调用 | 高 |
| 6 | 公开函数是否包含大额 swap 操作 | 高 |
| 7 | 是否有限制调用频率或调用者的机制 | 中 |
| 8 | 紧急操作函数是否缺少时间锁 | 中 |

### 经济模型相关

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 9 | 奖励分配是否基于时间加权而非瞬时快照 | 高 |
| 10 | 手续费计算是否可被绕过或操纵 | 高 |
| 11 | LP 代币铸造/销毁计算是否与实际存取一致 | 高 |
| 12 | 闪电贷攻击的盈亏平衡点是否过低 | 中 |

### 状态一致性相关

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 13 | 多个合约是否依赖同一 AMM 池的 reserve | 高 |
| 14 | reserve 读取后是否在同一调用链内使用 | 高 |
| 15 | 跨合约调用时状态是否可能过期 | 高 |
| 16 | 是否存在 check-effect-interaction 模式漏洞 | 中 |

## 检测方法

1. **静态分析**:
   - 搜索所有公开的 swap/harvest/claim/rebalance 函数
   - 检查这些函数是否使用 spot price
   - `slither --detect arbitrary-send-erc20`, `slither --detect unsafe-ERC721`

2. **经济建模**:
   - 计算攻击成本 = 闪电贷手续费 + AMM swap 手续费 + gas
   - 计算攻击收益 = 被操纵价格导致的差额
   - 当 收益 > 成本 且 风险 = 0 时, 确认为无风险套利漏洞

3. **Foundry 模拟**:
   ```solidity
   function testRiskFreeArbitrage() public {
       // 1. 记录攻击前余额
       uint256 balBefore = token.balanceOf(attacker);

       // 2. 执行攻击 (闪电贷 + 操纵 + 利用 + 归还)
       vm.prank(attacker);
       attackerContract.attack{value: 0}();

       // 3. 验证: 攻击者获利且无风险
       uint256 balAfter = token.balanceOf(attacker);
       assertGt(balAfter, balBefore); // 确定性获利

       // 4. 验证可重复性
       vm.roll(block.number + 1);
       vm.prank(attacker);
       attackerContract.attack{value: 0}(); // 可重复
   }
   ```

4. **MEV 模拟**: 使用 Foundry mainnet fork 模拟真实 MEV 环境

## 相关案例

- Vesper Finance (2021-03): harvest 公开调用 + 无滑点保护, Dedaub 披露
- BT Finance (2021-03): 同上模式, harvest 被夹击
- Alpha Homora V2 (2021-10): Router 隐式假设, 20 地址损失 40.93 ETH
- Cream Finance (2021-10): 闪电贷操纵价格 + 借贷, 损失 $130M
- bZx (2020-02): 闪电贷操纵 Uniswap 价格 + 借贷套利, 首次闪电贷攻击
