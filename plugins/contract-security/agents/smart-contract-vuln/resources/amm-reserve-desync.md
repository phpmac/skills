# 漏洞参考: AMM储备不同步漏洞

**关键词**: skim, sync, reserve-balance-desync, transfer-to-pair, reflection-token, rebasing-token, AMM-manipulation, MEV-front-run, LP-drain

**来源URL**:
- UniswapV2Pair 源码: https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2Pair.sol
- Uniswap V2 白皮书: https://uniswap.org/whitepaper.pdf
- Hacken Uniswap V2 安全分析: https://hacken.io/discover/uniswap-v2-core-contracts-security/
- Dedaub Yield Skimming: https://dedaub.com/blog/yield-skimming-forcing-bad-swaps-on-yield-farming/
- Alpha Homora MEV 事件: https://blog.alphaventuredao.io/mev-bots-uniswap-implicit-assumptions/
- Schnoodle 事件分析: https://vishvesh-rao.github.io/posts/Detailed-Postmortem-of-Uniswap-v2-Schnoodle-exploit/
- Zealynx Uniswap V2 安全指南: https://www.zealynx.io/blogs/uniswap-v2

## 概述

所有基于恒定乘积公式 (x*y=k) 的 AMM/DEX 协议都存在 reserve-balance 不同步问题, 包括但不限于:

| 协议 | 网络覆盖 | 风险等级 |
|------|---------|---------|
| Uniswap V2 | Ethereum + 所有 EVM 链 | 高 |
| PancakeSwap V2 | BSC + 多链 | 高 |
| SushiSwap | 多链 | 高 |
| QuickSwap | Polygon | 高 |
| TraderJoe | Avalanche | 高 |
| Raydium | Solana (类似机制) | 中 |
| 所有 Uniswap V2 Fork | 取决于链 | 高 |

**核心问题**: AMM Pair 合约维护两个独立的值:
- `reserve` (存储变量) - 用于价格/流动性计算, 仅在 `_update()` 时更新
- `balance` (实际代币余额 `IERC20.balanceOf(pair)`) - 可被外部操作改变

当 `balance > reserve` 时, 差值可被任何人通过 `skim()` 提取, 或被 MEV 机器人抢跑获利.

## 漏洞原理

以 UniswapV2Pair 为例 (所有 V2 Fork 共享相同机制):

```solidity
// === 核心机制 ===

// _update: 仅在此处将 reserve 同步为 balance
function _update(uint balance0, uint balance1, uint112 _reserve0, uint112 _reserve1) private {
    require(balance0 <= uint112(-1) && balance1 <= uint112(-1), 'UniswapV2: OVERFLOW');
    reserve0 = uint112(balance0);
    reserve1 = uint112(balance1);
    // ...
}

// swap: 通过 balance - reserve 计算输入量
function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) external lock {
    (uint112 _reserve0, uint112 _reserve1,) = getReserves();
    // ... 乐观转账 ...
    balance0 = IERC20(_token0).balanceOf(address(this)); // 读取实际余额
    balance1 = IERC20(_token1).balanceOf(address(this));
    uint amount0In = balance0 > _reserve0 - amount0Out ? balance0 - (_reserve0 - amount0Out) : 0;
    uint amount1In = balance1 > _reserve1 - amount1Out ? balance1 - (_reserve1 - amount1Out) : 0;
    // 验证: balance0Adjusted * balance1Adjusted >= reserve0 * reserve1 * 1000^2
    _update(balance0, balance1, _reserve0, _reserve1);
}

// mint: 通过 balance - reserve 计算存入量
function mint(address to) external lock returns (uint liquidity) {
    uint balance0 = IERC20(token0).balanceOf(address(this));
    uint balance1 = IERC20(token1).balanceOf(address(this));
    uint amount0 = balance0.sub(_reserve0); // 差值即为存入量
    uint amount1 = balance1.sub(_reserve1);
    // ... LP 计算基于差值 ...
}

// === 风险函数 ===

// skim: 提取 balance - reserve 的差值给任意地址
function skim(address to) external lock {
    _safeTransfer(_token0, to, IERC20(_token0).balanceOf(address(this)).sub(reserve0));
    _safeTransfer(_token1, to, IERC20(_token1).balanceOf(address(this)).sub(reserve1));
}

// sync: 将 reserve 更新为 balance (修复不同步)
function sync() external lock {
    _update(IERC20(token0).balanceOf(address(this)), IERC20(token1).balanceOf(address(this)), reserve0, reserve1);
}
```

## 攻击场景

| 场景 | 触发条件 | 攻击方式 | 受影响协议类型 |
|------|---------|---------|-------------|
| 反射代币分红 | token 余额自动增加, reserve 不变 | MEV 监控 transfer 事件后调用 `skim()` 提取增量 | 所有使用反射代币的池 |
| Rebase 代币 | 弹性供应导致 pair 余额变化 | `skim()` 提取 rebase 产生的增量余额 | Olympus, AMPL 类代币 |
| 合约先转币后操作 | `transfer()` 到 pair 后未在同一 tx 内 sync/mint | 攻击者在操作间隙调用 `skim()` | 收益合约, 分配合约 |
| 收益收割夹击 | harvest 中 swap 前余额已变化 | MEV 在 swap 前后夹击, 低买高卖 | Yield Farm, Vault |
| Fee-on-transfer 代币 | 转账金额与到账金额不一致 | 差额被 `skim()` 提取, 或 mint 时 LP 计算错误 | 通缩代币, 税费代币 |
| uint112 溢出 | 余额超过 2^112-1 | 所有操作 revert, 需 `skim()` 恢复 | 高通胀代币 |
| 自定义 Router 非原子操作 | transfer 和 pair 操作不在同一 tx | MEV 在两笔 tx 之间插入 skim/swap | 自定义流动性管理 |

## 攻击步骤示例

### 示例1: Schnoodle 事件 (2022-06, 损失 104 ETH)

```
1. 攻击者查询 pair 的 SNOOD 余额 (ERC-777 反射代币)
2. 利用整数除法漏洞, transferFrom 将 pair 中几乎全部代币转走 (留1个)
   // _getStandardAmount() 中 reflectedAmount / _getReflectRate() 因整数除法截断为0
   // 导致 _spendAllowance() 实际扣除0, 但代币被转走
3. 调用 sync() 更新 reserve (reserve 显示只有1个 SNOOD, WETH不变)
4. 将 SNOOD 转回 pair (但 reserve 未更新, 仍显示1个)
5. 调用 swap():
   balance0 = IERC20(SNOOD).balanceOf(pair) // 实际有大量 SNOOD
   reserve0 = 1 // 但 reserve 只有1
   amount0In = balance0 - (reserve0 - amount0Out) // 极小值
   // K 值检查通过: balance0Adjusted * balance1Adjusted >= reserve0 * reserve1 * 1000^2
   // 攻击者用极少 SNOOD 换走 pair 中几乎所有 WETH
```

### 示例2: Alpha Homora V2 (2021-10, 20 地址损失 40.93 ETH)

```
1. 用户在 Alpha Homora V2 开杠杆仓位
2. 合约内部: swap 输入代币 -> 添加流动性
3. Router.addLiquidity 隐式假设 amountADesired >= amountAMin
   // 如果 amountADesired < amountAMin, 滑点检查被跳过
4. MEV 机器人:
   a. 在 mempool 发现用户交易
   b. 通过 Flashbots 私有交易打包:
      - 前置交易: 操纵 AMM 价格
      - 用户交易: 以劣价执行
      - 后置交易: 恢复价格, 获利
5. 用户 LP 价值低于预期, 差额被 MEV 提取
```

### 示例3: Vesper Finance / BT Finance Yield Skimming (2021-03)

```
1. 收益合约 harvest() 函数公开可调用
2. 攻击者:
   a. 在 AMM 池中大额卖出 tokenA, 压低价格 (池中1000A -> 2000A, 价格降4x)
   b. 调用 victim.harvest(), 合约以被操纵的低价 swap 奖励代币
      // 合约 swap 100A, 本应得50B, 实际只得12B
   c. 在 AMM 池中买回 tokenA, 获利 = 被贱卖的收益
3. 数学条件: 当 victim swap 金额 > 池子储备的 0.3% 时即可盈利
```

## 修复方案

```solidity
// 方案1: 转入后立即 sync (推荐, 适用于所有 AMM)
token.transfer(pairAddress, amount);
IUniswapV2Pair(pairAddress).sync(); // PancakeSwap/SushiSwap 等同理

// 方案2: 在单笔交易内完成 transfer + swap/mint (Router 模式)
// Router 保证原子性, EOA 无法在中间插入 skim
// 适用于 Uniswap/PancakeSwap/SushiSwap 的标准 Router

// 方案3: 反射/Rebase 代币使用 ERC4626 Vault 包装后再入池
// 避免余额自动变化导致不同步
// 适用于 SafeVault, xToken 等包装方案

// 方案4: 自定义 pair 合约强制 sync (适用于 Fork 项目)
function _beforeSwap() internal {
    sync(); // 每次操作前强制同步
}

// 方案5: 限制 skim 权限 (破坏 AMM 兼容性, 谨慎使用)
function skim(address to) external onlyOwner { ... }

// 方案6: 使用 try/catch 处理 uint112 溢出
function safeDeposit(uint amount0, uint amount1) external {
    token0.transfer(pair, amount0);
    token1.transfer(pair, amount1);
    try IUniswapV2Pair(pair).mint(to) returns (uint liquidity) {
        // 成功
    } catch {
        // 可能溢出, 先 skim 再 mint
        IUniswapV2Pair(pair).skim(address(this));
        IUniswapV2Pair(pair).mint(to);
    }
}
```

## 审计检查清单

### AMM 交互相关

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 1 | 是否存在先 `transfer()` 到 pair 再在单独交易中调用 `sync/mint/swap` 的模式 | 高 |
| 2 | 自定义 Router 是否保证 transfer + pair 操作的原子性 | 高 |
| 3 | 合约内是否有 `token.transfer(pair, amount)` 后未紧跟 pair 操作的代码 | 高 |
| 4 | 是否在 mint/swap 前调用了 `sync()` 确保储备一致 | 高 |

### 代币类型相关

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 5 | 代币是否为 rebasing/reflection 类型 (会自动增加 pair 余额) | 高 |
| 6 | Fee-on-transfer 代币的差额是否被正确处理 | 高 |
| 7 | 代币总供应量是否可能超过 uint112 上限 | 中 |
| 8 | ERC-777 代币的 hooks 是否可被利用 | 高 |

### MEV/抢跑相关

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 9 | 是否有公开函数可触发 pair 操作 (MEV 可夹击) | 高 |
| 10 | 收益合约的 harvest/swap 是否有公开调用入口且缺少滑点保护 | 高 |
| 11 | swap 是否设置了合理的 amountOutMin | 高 |
| 12 | 是否使用了 Flashbots/私有交易池防止抢跑 | 中 |

## 检测方法

1. 搜索所有 `transfer(pairAddress` 或 `transferFrom(*, pairAddress` 调用
2. 检查 transfer 后是否在同一函数内调用了 pair 的 sync/mint/swap
3. 使用 `slither --detect reentrancy` 检查跨函数的状态不一致
4. 验证代币类型: 是否实现 `rebasing`/`reflection` 机制
5. 检查 `skim()` 函数是否被移除或添加了权限控制
6. 使用 Foundry mainnet fork 模拟 skim 攻击:
   ```solidity
   function testSkimExploit() public {
       // 1. 向 pair 转入额外代币
       token0.transfer(pairAddress, extraAmount);
       // 2. 验证 skim 可提取差值
       uint256 before = token0.balanceOf(attacker);
       vm.prank(attacker);
       IUniswapV2Pair(pairAddress).skim(attacker);
       uint256 stolen = token0.balanceOf(attacker) - before;
       assertEq(stolen, extraAmount); // 确认可提取
   }
   ```

## 实际案例

| 事件 | 日期 | 损失 | 根因 | 攻击链 |
|------|------|------|------|--------|
| Schnoodle | 2022-06-18 | 104 ETH | ERC-777 整数除法 + sync 延迟 | transferFrom->sync->transfer->swap |
| Alpha Homora V2 | 2021-10 | 40.93 ETH (20地址) | Router 隐式假设 + MEV 夹击 | mempool 监控 + Flashbots 打包 |
| Vesper Finance | 2021-03 | ~$150K | harvest 公开调用 + 无滑点保护 | 操纵 AMM 价格 + 触发 harvest |
| BT Finance | 2021-03 | ~$150K | 同上模式 | 同上 |
| DefiPlaza | 2024-07-05 | 全部用户资金 | swap 逻辑漏洞 + 储备不同步 | 单 tx 攻击 |
| TMM/USDT (BSC) | 2026-04-05 | $1.665M | `to==0xdead`白名单绕过+swap(to=0xdead)烧毁Pair的TMM+sync()锁定虚假储备 | 闪电贷 → removeLP → swap(to=0xdead)烧6.8B TMM → pair.swap()提干BSC-USD |
| MONA/USDT (BSC) | 2026-04-14 | ~$60,950 | 延迟烧毁(sellMona)与swap不同步, burnsellMona()事后从Pair扣币+sync() | 闪电贷+Venus → 刷10K MONA → 卖9900制造延迟凭证 → 买空MONA → 零值transferFrom触发burn → Pair归零 → 卖100提干 |
