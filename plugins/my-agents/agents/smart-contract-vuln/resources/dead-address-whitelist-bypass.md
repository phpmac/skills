# 0xdead地址白名单绕过

**关键词**: 0xdead, whitelist-bypass, magic-address, burn-address-bypass, access-control-bypass, transfer-bypass, DEAD-constant, address-hardcoded, swap-to-dead, buy-restriction-bypass, CPMM-reserve-manipulation

**来源URL**:
- QuillAudits TMM 分析: https://x.com/QuillAudits_AI/status/2040750526833492242
- Halborn TMM 分析: https://www.halborn.com/blog/post/explained-the-tmm-hack-april-2026
- ExVul TMM 分析: https://x.com/exvulsec/status/2040649377803546859
- MONA攻击分析: https://x.com/Defi_Nerd_sec/status/2043963711065604603
- Solidity Hacks 合集: https://github.com/chatch/solidity-hacks

**适用范围**: 所有在权限校验或transfer逻辑中硬编码0xdead/address(0)等魔法地址的DeFi合约, 特别是代币合约, Vault类协议和Ponzi/资金盘模式代币

## 核心原因

`to==0xdead` 绕过transfer安全检查 + 攻击者持有大量LP + 闪电贷 -> removeLP将TMM烧到0xdead + swap(to=0xdead)绕过买入禁令继续烧 -> AMM底池TMM余额骤降至~1 -> CPMM恒定乘积公式使价格异常飙高 -> pair.swap()提干底池中全部BSC-USD -> 偿还闪电贷后净获利

## 漏洞原理

开发者将 `0x000000000000000000000000000000000000dEaD` 硬编码为特殊信任地址, 假设"没人能控制它", 从而在安全检查中为其开辟旁路. 攻击者利用该旁路绕过正常的安全限制.

```solidity
// 变种1: transfer中的0xdead旁路
// 代币合约 _transfer 函数中, 转到0xdead时跳过所有检查
function _transfer(address from, address to, uint256 amount) internal override {
    if (to == address(0xdead)) {
        super._transfer(from, to, amount);
        return; // 跳过: freeTrade检查/手续费/延迟烧毁/黑名单
    }
    // ... 正常安全检查逻辑 ...
}

// 变种2: 权限白名单中的0xdead
// Vault合约的modifier中, 0xdead被视为白名单地址
address public constant DEAD = 0x000000000000000000000000000000000000dEaD;

modifier onlyWhitelisted() {
    require(whitelist[msg.sender] || msg.sender == DEAD, "Not whitelisted");
    _;
}

// 变种3: owner转移给0xdead后的检查不一致
// renounceOwnership 转给0xdead而非address(0), 下游检查用owner()!=address(0)误判
function renounceOwnership() public onlyOwner {
    _transferOwnership(address(0xdead)); // 应该是address(0)
}
```

**触发条件**:
- 变种1: 攻击者调用 `transfer/swap` 指定 `to=0xdead`, 代币直接从合约流到0xdead, 跳过transfer中的所有检查. 当代币设有买入禁令(freeTrade=false)时, `swapTokensForExactTokens(path, to=0xdead)` 可绕过买入限制, 代币直接从Pair烧到0xdead而非攻击者地址, 攻击者无需持有代币即可操纵底池储备
- 变种2: 攻击者通过0xdead的特权身份执行敏感操作(修改汇率/提取资金/铸造代币), 可能通过CREATE2部署合约到0xdead或利用0xdead在协议中的特殊地位
- 变种3: owner==0xdead后, `require(owner() != address(0))` 检查通过(0xdead != address(0)), 但实际已无有效owner

**为什么危险**: 0xdead常被用于代币燃烧/LP铸造/代币分发, 使白名单成为"必要设计", 增加修复难度. 83%+的代币供应可能烧到0xdead, 去掉白名单会破坏代币经济模型.

## 变种与衍生

| 变种 | 触发方式 | 区别 |
|------|----------|------|
| transfer旁路 | `to==0xdead` 跳过transfer检查 | 代币直接流向0xdead, 攻击者无需持有代币 |
| swap-to-0xdead绕过买入 | `swap(to=0xdead)` 绕过买入禁令 | 代币从Pair烧到0xdead而非给攻击者, 用于操纵底池储备而非获取代币 |
| 权限白名单 | `msg.sender==DEAD` 绕过modifier | 0xdead可执行特权操作, 可能通过CREATE2部署合约到0xdead |
| owner转移不一致 | renounce转给0xdead而非address(0) | `owner()!=address(0)` 误判为仍有owner |
| LP铸造旁路 | `_handleFeeAmount` 铸造LP到0xdead | 用户应得的LP被吞, 自动加费机制走0xdead旁路 |

## 审计检查清单

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 1 | 搜索合约中所有 `0xdead` / `dEaD` / `DEAD` 硬编码 | 高 |
| 2 | `_transfer` 中是否有针对0xdead的 early return/跳过检查 | 高 |
| 3 | modifier/require 中是否将0xdead作为白名单或特权地址 | 高 |
| 4 | **0xdead在白名单中时分析具体影响** - 0xdead在白名单中本身可能合理(燃烧需要), 不能直接标高风险, 关键分析: 哪些检查被跳过, 跳过后攻击路径是否成立 | 高 |
| 5 | **购买到销毁地址的绕过路径** - `swap(to=0xdead)` / `transfer(to=0xdead)` 是否能绕过买入限制 | 高 |
| 6 | **底池价格操纵风险** - 大量代币流入0xdead后, AMM底池代币余额骤降, 价格异常飙高, 闪电贷放大此效果 | 高 |
| 7 | renounceOwnership 是否转给0xdead而非address(0) | 中 |
| 8 | 自动加LP/手续费分配是否铸造到0xdead | 中 |
| 9 | 0xdead地址是否可通过CREATE2部署合约 | 中 |

## 检测方法

1. **Grep搜索**:
```bash
grep -rn "0xdead\|dEaD\|DEAD\|0x000000000000000000000000000000000000dEaD" contracts/
grep -rn "address(0xdead)" contracts/
grep -rn "to == .*dead\|msg.sender == .*dead" contracts/
```

2. **Slither检测**:
```bash
slither . --detect constant-address-bypass
# 或自定义检测器搜索硬编码魔法地址
```

3. **Foundry模拟测试**:
```solidity
// 测试transfer旁路
function testDeadAddressBypass() public {
    vm.prank(attacker);
    token.transfer(address(0xdead), amount); // 应该走完整检查
}

// 测试权限白名单
function testDeadAddressWhitelist() public {
    vm.prank(address(0xdead));
    vault.restrictedFunction(); // 应该revert
}

// 测试swap to=0xdead
function testSwapToDeadBypass() public {
    vm.prank(attacker);
    router.swapTokensForExactTokens(amountOut, amountInMax, path, address(0xdead), deadline);
}
```

## 真实案例

| 事件 | 日期 | 损失 | 根因 | 攻击链 |
|------|------|------|------|--------|
| TMM/USDT (BSC) | 2026-04-05 | $1.665M | `_transfer`中`to==0xdead`跳过所有检查(freeTrade/手续费/延迟烧毁/黑名单), 绕过买入禁令; 攻击者通过44个自控钱包囤积96.4% LP(极可能来自团队控制的vault存款合约) | 44钱包囤积1.9M LP(96.4%, 区块90647557-90647867) → 闪电贷$276M(ListaDAO/Venus/AaveV3/PancakeSwap/Uniswap) → removeLiquidity: 109M TMM烧到0xdead + 26K BSC-USD → swapTokensForExactTokens(BSC-USD→TMM, to=0xdead): 6.8B TMM烧掉(绕过freeTrade=false) → Pair剩余~1 TMM + ~272M BSC-USD → pair.swap()提干272M BSC-USD → 偿还闪电贷, 净利润$1.665M |
| MONA/USDT (BSC) | 2026-04-14 | ~$60,950 | 零值`transferFrom(0xdead,0xdead,0)`触发_update()钩子执行BurnAddress.burn()从Pair扣币 | Moolah闪电贷+Venus借USDT → 25账户刷10K MONA → 卖9900制造延迟烧毁凭证 → 买空Pair的MONA → transferFrom(0xdead,0xdead,0)触发burn → Pair储备归零 → 卖100 MONA提干USDT |

**TMM攻击关键补充**:

1. **LP来源闭环**: TMM代币设计为Ponzi/资金盘模式, 用户不能直接在DEX买入(freeTrade=false是设计如此, 非临时限制), 必须转USDT(最低100U)到vault存款合约(0xA1193ba5481Eef92F78a901617B88Fc76A744ccc), vault构建LP, 用户获LP份额+TMM挖矿奖励. 攻击者(极可能为团队本身, 钱包聚类分析确认44个钱包由同一实体控制)通过vault囤积96.4% LP, 安全公司(QuillAudits/Halborn)报告为外部攻击者, 但vault=存款合约使团队嫌疑最大

2. **0xdead白名单是代币设计的必要部分**: TMM总量100亿, ~83%烧到0xdead, 白名单确保燃烧操作不受freeTrade/手续费限制. 去掉白名单会破坏代币经济模型, 这是此类漏洞修复困难的核心原因

3. **攻击者从未持有TMM**: 整个攻击流程中TMM全部流向0xdead. removeLP取出的TMM立即烧到0xdead(走白名单), swap(to=0xdead)让TMM从Pair直接烧到0xdead(绕过买入禁令). 攻击者只操作LP和BSC-USD, 通过pair.swap()的pancakeCall回调以~0 TMM输入提干Pair中全部BSC-USD

4. **CPMM储备操纵机制**: removeLP + swap(to=0xdead)将Pair中TMM余额从正常水平降至~1枚, BSC-USD仍有~272M. CPMM恒定乘积(x*y=k)下, 当reserve_x趋近0时, 任意微小amountIn即可换出接近全部reserve_y

来源:
- QuillAudits TMM分析: https://x.com/QuillAudits_AI/status/2040750526833492242
- Halborn TMM分析: https://www.halborn.com/blog/post/explained-the-tmm-hack-april-2026
- MONA攻击详细分析: https://x.com/Defi_Nerd_sec/status/2043963711065604603
- MONA攻击TX: https://bscscan.com/tx/0x3a60e1b3a4b0736be4f31839bfd7abc8bfc53b93ddbd3702e77fbc64561a7ea4
