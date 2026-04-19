# 奖励操纵/全局状态分母/奖励会计时序漏洞

**关键词**: reward-manipulation, global-variable-denominator, mining-reward-inflation, post-transfer-balance-reward, _mining-manipulation, staking-reward-bug, reward-accounting-timing, transient-holder-reward, dividend-share-update, flash-loan-reward-capture, duplicate-id-reward, array-validation-reward, nextRedeem-ordering

**来源URL**:
- audit911 BTCN告警: https://x.com/audit_911/status/2044672856097952193
- audit911 ListaDAO告警: https://x.com/audit_911/status/2044677392728510799
- clara_oracle ListaDAO分析: https://x.com/clara_oracle/status/2044691138439778430
- DefimonAlerts LootBot告警: https://x.com/DefimonAlerts/status/2044709964091187660
- clara_oracle LootBot分析: https://x.com/clara_oracle/status/2044717004037243064
- AstraSecAI LootBot告警: https://x.com/AstraSecAI/status/2044731019891220567
- 类似案例 MasterChef startBlock重设: https://rekt.news/pefarm/

**适用范围**: 使用全局变量作为奖励计算分母的代币合约, Staking/Vault协议, 买入后立即更新奖励份额的分红型协议, 以及接受数组参数的批量领取/赎回函数

## 核心原因

- **变种A**: 全局变量分母可被外部操作压至极小值 + 奖励按转账后余额结算 -> 分母趋零奖励膨胀至天文数字 + 少量转入基于总余额触发天量铸造
- **变种B**: 买入后立即更新分红份额 + claimReward无持有期要求 -> 闪电贷买入即获分红资格 -> 同tx领取奖励/分红后卖出 -> 零持有期风险套取奖励
- **变种C**: redeem/batchClaim接受数组参数不校验重复ID + 状态映射在奖励计算发放后才更新 -> 同一ID重复N次获得N倍奖励

## 漏洞原理

### 变种A: 全局变量分母操纵

奖励计算依赖全局变量(如 `_mining`)作为分母, 攻击者通过反复操作将该变量压到极小值, 导致分母趋近零, 奖励值被放大到天文数字. 同时接收方奖励按"转账后余额"结算而非转账金额, 转入少量代币即可基于总余额触发大量奖励铸造.

```solidity
// 漏洞1: 全局变量做分母, 无下限保护
function _getReward(address account) internal view returns (uint256) {
    return _balances[account] * _rewardPerToken / _mining; // _mining可被压到极小值
}

// 漏洞2: 转账后余额结算奖励, 而非按转账金额
function _transfer(address from, address to, uint256 amount) internal {
    super._transfer(from, to, amount);
    // 用转账后的总余额计算奖励, 而非本次转账金额
    uint256 reward = _getReward(to); // to的余额可能很大, 奖励膨胀
    _mint(to, reward);
}

// _mining 被反复swap压低的过程:
// swap1: _mining = 100 -> swap2: _mining = 10 -> swap3: _mining = 0.001
// 分母极小 = 奖励极大
```

**触发条件**:
- 奖励计算使用可被外部操作影响的全局变量作分母
- 分母无最小值保护(require _mining >= threshold)
- 奖励基于接收方总余额而非增量计算
- 无单次铸造上限

### 变种B: 奖励会计时序漏洞 (Reward Accounting Timing)

买入/存款后立即更新分红份额, 闪电贷攻击者可在单一交易内获取奖励资格而无需承担持有期风险. 核心问题: 奖励资格的认定没有时间锁/延迟机制.

```solidity
// 漏洞: 买入后立即更新分红份额, 无持有期要求
function buy(uint256 amount) external {
    token.transferFrom(msg.sender, address(this), amount);
    // 买入即刻获得分红权! 闪电贷买入后同tx内就能claimReward
    _updateDividendShare(msg.sender, amount);
}

function claimReward() external {
    // 只要份额>0就能领取, 不管持有时间
    uint256 reward = _pendingReward(msg.sender);
    rewardToken.transfer(msg.sender, reward);
}

function withdrawDividends() external {
    // 领取分红也不需要持有期
    uint256 dividend = dividends[msg.sender];
    payable(msg.sender).transfer(dividend);
}
```

**触发条件**:
- 买入/存款操作会立即更新分红/奖励份额
- claimReward/withdrawDividends 无最小持有时间要求
- 攻击者可用闪电贷在单tx内完成: 借款 -> 买入 -> 领取奖励/分红 -> 卖出 -> 还款
- 无需任何特权访问(No privileged access needed)

### 变种C: 重复输入奖励倍增 (Duplicate Input Reward Multiplication)

redeem/batchClaim等函数接受ID数组参数但不校验重复, 且状态映射(如nextRedeem)在奖励计算和发放之后才更新, 导致同一ID重复N次获得N倍奖励.

```solidity
// 漏洞: 数组参数不去重 + 状态在奖励发放后才更新
mapping(uint256 => uint256) public nextRedeem; // 每个NFT ID上次领取的epoch

function redeem(uint256[] calldata ids) external {
    uint256 totalReward = 0;

    // 计算阶段: 同一ID重复N次就累加N次奖励
    for (uint256 i = 0; i < ids.length; i++) {
        uint256 id = ids[i];
        // nextRedeem[id] 还是旧值, 每次重复ID都用同一个旧值计算
        totalReward += _redeemable(id, nextRedeem[id]);
    }

    // 发放阶段: 转出膨胀后的总额
    payable(msg.sender).transfer(totalReward);

    // 更新阶段: 此时才更新nextRedeem, 但钱已经发出去了!
    for (uint256 i = 0; i < ids.length; i++) {
        nextRedeem[ids[i]] = currentEpoch;
    }
}
```

**触发条件**:
- redeem/batchClaim/claimRewards 函数接受ID数组参数
- 数组内不校验重复ID(无seen mapping/无Set去重)
- 状态映射(nextRedeem/claimed)在奖励发放之后才更新, 违反Checks-Effects-Interactions
- 无数组长度上限限制

## 变种与衍生

| 变种 | 触发方式 | 区别 |
|------|----------|------|
| 全局变量分母操纵 | 反复swap/转账压低`_mining`等全局变量 | 分母趋零导致奖励膨胀 |
| 转账后余额奖励 | 给目标地址转少量代币, 触发基于总余额的奖励结算 | 余额越大奖励越多, 与转账金额无关 |
| 奖励会计时序 | 闪电贷买入后立即更新分红份额, 同tx领取奖励后卖出 | 无需特权, 利用买入即获得分红资格的设计缺陷 |
| 重复输入奖励倍增 | redeem数组中重复同一ID, 状态映射在发放后才更新 | 同一ID传N次获N倍奖励, 违反Checks-Effects-Interactions |
| MasterChef startBlock重设 | 修改startBlock使奖励累积期变长 | 时间维度而非变量维度的操纵 |
| 快照余额操纵 | 在快照前大量存入, 快照后取出 | 利用快照时机差获取不对称奖励 |

## 审计检查清单

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 1 | 奖励计算的分母是否使用全局变量, 该变量是否可被外部操作影响 | 高 |
| 2 | 全局变量分母是否有最小值保护(require _mining >= MIN_THRESHOLD) | 高 |
| 3 | 转账触发的奖励是按"转账后余额"还是"转账金额"结算 | 高 |
| 4 | 单次奖励铸造是否有cap上限 | 中 |
| 5 | swap/转账操作是否会影响奖励计算的全局状态变量 | 高 |
| 6 | 奖励计算是否基于增量变化而非绝对余额 | 中 |
| 7 | 买入/存款后是否立即更新分红/奖励份额, 是否有持有期锁 | 高 |
| 8 | claimReward/withdrawDividends 是否要求最小持有时间 | 高 |
| 9 | 闪电贷买入->领取奖励->卖出->还款是否可在单tx内完成 | 高 |
| 10 | redeem/batchClaim数组参数是否校验重复ID(seen mapping或去重) | 高 |
| 11 | nextRedeem/claimed等状态映射是否在奖励计算循环**内部**更新而非之后 | 高 |
| 12 | 数组参数是否有长度上限限制 | 中 |

## 检测方法

1. **Grep搜索**:
```bash
grep -rn "_mining\|rewardPerToken\|rewardRate" contracts/
grep -rn "_balances\[.*\].*_mining\|totalSupply.*reward" contracts/
grep -rn "_mint.*reward\|_mint.*_getReward" contracts/
```

2. **Slither检测**:
```bash
slither . --detect divide-before-multiply
# 自定义: 检查除法中变量是否可被外部函数修改
```

3. **Foundry模糊测试**:
```solidity
// 变种A: 测试分母操纵
function testFuzz_MiningDenominator(uint256 swapCount) public {
    for (uint256 i = 0; i < swapCount; i++) {
        token.swap(amount);
    }
    uint256 reward = token.getReward(attacker);
    assertLt(reward, MAX_REWARD_CAP);
}

// 变种C: 测试重复ID奖励倍增
function test_DuplicateIdRewardMultiplication() public {
    uint256[] memory ids = new uint256[](10);
    // 同一个ID重复10次
    for (uint256 i = 0; i < 10; i++) {
        ids[i] = 1; // ID=1重复10次
    }
    uint256 balanceBefore = address(staking).balance;
    staking.redeem(ids);
    uint256 balanceAfter = address(staking).balance;
    // 单次奖励不应超过实际应得的倍数
    assertLt(balanceBefore - balanceAfter, singleReward * 2); // 应该只领1次
}
```

## 真实案例

| 事件 | 日期 | 损失 | 根因 | 攻击链 |
|------|------|------|------|--------|
| BTCN (BSC) | 2026-04-15 | ~300 USD | `_mining`全局变量分母操纵+转账后余额奖励结算 | 闪电贷23WBNB → 反复swap压低_mining → 转少量BTCN触发天量奖励铸造 → 卖回LP池 → 净利0.072BNB |
| ListaDAO FLAP (BSC) | 2026-04-16 | ~1.6+2.3 BNB | FLAP买入后立即更新分红份额, 闪电贷买家无需持有期即可领取奖励 | 闪电借11WBNB → swap 10.1WBNB买FLAP → deposit 0.85WBNB到Dividend → 卖FLAP触发TaxProcessor清算 → claimReward(2992052143954255 slisBNB) → withdrawDividends(136295689120776664 wei) |
| LootBot xLoot (ETH) | 2026-04-15 | ~4.1 ETH ($9600) | `redeem()`不校验重复NFT ID, `nextRedeem`在奖励发放后才更新 | Balancer闪电借2.1ETH → 发送ETH到staking触发新epoch → redeem(7个ID各重复155次=1085项) → 领6.21ETH → 还闪电贷 → 净利4.09ETH |