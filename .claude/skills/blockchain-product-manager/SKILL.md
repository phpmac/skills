---
name: blockchain-product-manager
description: Use when 规划, 设计或审查区块链 DApp/App 产品. 适用于 PRD 编写, 代币经济模型设计, ERC20 转账手续费分配 (SafeMoon/反射代币), 推荐奖励体系 (直推/级差/团队奖), 手续费/分润比例计算, 质押/LP 参数计算, 业务逻辑漏洞审查, 或 DeFi/NFT/GameFi 项目中的智能合约交互流程设计.
---

# 区块链 DApp/App 产品经理

## Overview
作为区块链产品经理角色, 协助整理产品文档, 审查业务逻辑漏洞, 计算代币经济/费率参数, 输出结构化的产品设计文档. 覆盖 ERC20 手续费代币机制, 推荐奖励体系(直推/级差/团队奖), 合约安全审查等核心领域. 

## 使用时机
- 设计新的 DApp/App 产品功能
- 编写或审查 PRD (产品需求文档)
- 设计代币经济模型 (Tokenomics)
- 设计 ERC20 转账手续费分配 (反射/销毁/回流)
- 设计推荐奖励体系 (直推奖/级差奖/团队奖)
- 计算手续费/分润/质押/LP 等比例参数
- 审查业务流程中的逻辑漏洞
- 梳理智能合约交互流程
- 评估产品方案的可行性和安全性

## 核心工作流

### 1. 需求梳理与文档输出

收到产品需求时, 按以下模板输出结构化文档:

```markdown
# [产品/功能名称] PRD

## 1. 概述
- 产品定位: [一句话描述]
- 目标用户: [用户画像]
- 支持链: [ETH/BSC/Solana/...]
- 核心价值: [解决什么问题]

## 2. 功能清单
| 功能模块 | 优先级 | 描述 | 涉及合约 |
|---------|--------|------|---------|
| ... | P0/P1/P2 | ... | ... |

## 3. 用户流程
[使用 Mermaid 流程图描述核心用户路径]

## 4. 数据模型
- 链上数据: [需要存储在合约中的状态]
- 链下数据: [后端/数据库存储]

## 5. 合约交互设计
| 操作 | 合约方法 | 参数 | 权限 | Gas 预估 |
|------|---------|------|------|---------|
| ... | ... | ... | ... | ... |

## 6. 经济模型
[代币分配/费率/激励机制]

## 7. 风险评估
[业务逻辑风险/合约风险/监管风险]
```

### 2. ERC20 手续费代币机制 (SafeMoon 类)

设计转账自动扣税代币时, 必须明确以下参数:

**核心机制 - 每笔转账自动拆分:**
```
transfer(amount) 触发:
  taxFee%     -> 反射分红 (持币者按比例自动获得)
  liquidityFee% -> 自动回流LP池
  burnFee%    -> 销毁 (发送到死地址)
  marketingFee% -> 营销钱包
  devFee%     -> 开发钱包

// 验证: 所有Fee之和 = 总税率
// 常见总税率: 买入 5%-10%, 卖出 5%-15%
// 买卖税率可以不同 (卖出税高于买入 = 鼓励持有)
```

**反射(Reflection)机制原理:**
```
// 双空间映射: rSpace(反射空间) 和 tSpace(实际空间)
rTotal = MAX - (MAX % tTotal)  // 反射总量
currentRate = rSupply / tSupply

// 每次扣税时:
rTotal -= rFee  // 减少反射总量
// 导致 currentRate 变小
// 所有持币者的 balanceOf = rOwned / currentRate 自动增大
// 无需遍历所有地址, 零Gas分红

// 排除列表: 合约地址/LP地址/项目方 可设为 isExcludedFromReward
```

**测试规范 - 机制代币买卖税必须用 Router 测试:**
```
// transfer() 的 from/to 都不是 pair 地址, 不会触发买卖税分支
// 必须使用 DEX Router 接口才能模拟真实买卖场景:

// 买入测试:
router.swapExactETHForTokensSupportingFeeOnTransferTokens(...)

// 卖出测试:
router.swapExactTokensForETHSupportingFeeOnTransferTokens(...)

// 注意: 必须使用 SupportingFeeOnTransferTokens 后缀版本
// 否则普通 swap 因为扣税后 amountOut 对不上会直接 revert
```

**必须审查的安全点:**
- [ ] 是否有 `excludeFromFee` 白名单 (合约/路由器/LP必须排除, 否则交易失败)
- [ ] 是否有 `excludeFromReward` (防止LP池/合约地址吃反射)
- [ ] `maxTxAmount` 单笔最大交易限制 (防鲸鱼砸盘)
- [ ] `maxWalletBalance` 单地址最大持仓 (防集中持仓)
- [ ] `swapAndLiquify` 阈值是否合理 (太低频繁触发Gas高, 太高影响价格)
- [ ] Owner 是否可以修改税率 (应有上限限制或时间锁)
- [ ] 是否可以关闭交易 (Owner禁止交易 = 跑路后门, CRITICAL风险)
- [ ] LP是否锁定 (未锁定 = 可以撤池跑路)

**移除流动性单独收费 (Remove Liquidity Fee):**
```
// 买入 from==pair 时, 需区分: 普通买入 vs 移除LP
// 移除LP时 pair 里的 otherToken balance 会减少, 可用此判断:

function _isRemoveLiquidity() internal view returns (bool) {
    (uint r0, uint r1,) = pair.getReserves();
    uint bal = IERC20(otherToken).balanceOf(address(pair));
    return r >= bal;  // 移除时余额先减少, reserve还没更新 → true
}

// 在 _transfer 里:
if (from == pair) {
    if (_isRemoveLiquidity()) {
        takeFee(..., removeLiquidityFee);  // 单独高税率, 如 10%
    } else {
        takeFee(..., buyFee);             // 普通买入税率, 如 3%
    }
}

// 用途: 防止大户移除LP砸价 / 单独对撤池行为惩罚性收费
// BSC/Arb 验证合约: FatToken(0x45E4fC54240C9beC351098aaFE684177eF790D01)
// 搜索关键词: _isRemoveLiquidity / removeLiquidityFee
```

**必须审查: removeLiquidityFee 风险点:**
- [ ] `_isRemoveLiquidity` 判断是否会误判 (正常买入被错收高税)
- [ ] removeLiquidityFee 是否有上限 (设100%可锁死撤池)
- [ ] 是否开放 `setRemoveLiquidityFee()` 给 Owner 随意修改 (应加时间锁或上限)
- [ ] 收取的费用去向是否透明 (国库/销毁/分红)

**典型税率设计参考:**
| 项目类型 | 买入税 | 卖出税 | 反射 | LP回流 | 销毁 | 营销 |
|---------|--------|--------|------|--------|------|------|
| 持币分红型 | 5% | 5% | 3% | 1% | 0% | 1% |
| 通缩销毁型 | 3% | 5% | 0% | 1% | 3% | 1% |
| 营销驱动型 | 5% | 8% | 1% | 2% | 0% | 5% |
| 混合型 | 6% | 10% | 2% | 2% | 1% | 5% |

### 3. 推荐奖励体系 (直推/级差/团队奖)

**A. 直推奖**: A邀请B, B交易/质押时A按固定比例获奖. 链上 `mapping(address => address) inviter` 记录关系, 绑定后不可修改. 

**B. 级差奖**: 多层级推荐, 逐级递减比例(如L1:10%, L2:5%, L3:3%), 向上遍历inviter链分发. 必须设 MAX_LEVEL 防Gas超限. 

**C. 团队奖**: 按团队总业绩划分等级, 达标后获额外奖励比例. 等级判定必须同时要求自身投入 + 团队业绩. 

**安全审查清单:**
- [ ] inviter 绑定后不可篡改, 防循环引用 (A->B->A)
- [ ] 级差遍历有 MAX_LEVEL 上限, 各层比例之和 < 总手续费
- [ ] 有最低投入门槛防 create2 批量刷假团队
- [ ] 团队业绩防闪电贷 (冷却期/快照机制)
- [ ] unstake 时团队业绩向上正确扣减
- [ ] address(0) 的奖励去向明确 (归国库)
- [ ] owner 无法修改推荐关系

### 4. 逻辑漏洞审查

审查产品设计时, 必须检查以下常见漏洞类型:

**资金流向漏洞:**
- 资金是否有无限授权风险 (approve MAX_UINT256)
- 存取款流程是否存在重入攻击路径
- 多签/时间锁是否覆盖关键资金操作
- 紧急暂停机制是否存在

**经济模型漏洞:**
- 通胀/通缩模型是否可持续 (计算死亡螺旋临界点)
- 套利空间是否被恶意利用 (闪电贷攻击路径)
- 价格预言机依赖是否存在操纵风险
- LP 无常损失是否在可控范围

**业务逻辑漏洞:**
- 用户操作顺序是否存在 race condition
- 边界条件: 0值/最大值/溢出
- 权限模型是否存在越权路径
- 前端显示与合约实际执行是否一致

**治理漏洞:**
- 投票权是否可以通过闪电贷临时获取
- 提案执行是否有足够的时间锁
- 多签门槛是否合理 (不能太低也不能太高)

### 5. 比例参数计算

计算经济参数时, 使用以下框架:

**手续费计算:**
```
总手续费 = 交易金额 * 费率
平台收入 = 总手续费 * 平台分成比例
LP收入 = 总手续费 * LP分成比例
回购销毁 = 总手续费 * 销毁比例

// 验证: 各比例之和必须 = 100%
assert(平台分成 + LP分成 + 销毁比例 + 其他 == 100%)
```

**代币分配计算:**
```
总供应量 = X
团队 = X * 团队比例% (需锁仓计划)
投资者 = X * 投资比例% (需释放计划)
社区/空投 = X * 社区比例%
流动性 = X * 流动性比例%
国库/储备 = X * 储备比例%
生态激励 = X * 激励比例%

// 验证: 各比例之和必须 = 100%
// 验证: 团队+投资者 建议 <= 30%, 社区相关 >= 50%
```

**质押收益计算:**
```
APR = (年奖励总量 * 代币价格) / (总质押量 * 代币价格) * 100%
APY = (1 + APR/n)^n - 1  // n=复利次数

// 注意: 实际收益受代币价格波动影响
// 注意: 高APR通常意味着高通胀, 需评估可持续性
```

**LP 池参数:**
```
恒定乘积: x * y = k (Uniswap V2)
集中流动性: 需指定价格区间 (Uniswap V3)
滑点 = |实际价格 - 预期价格| / 预期价格 * 100%

// 建议最大滑点容忍度: 0.5% - 3%
// 大额交易需检查流动性深度
```

### 6. 竞品分析模板

```markdown
| 维度 | 本产品 | 竞品A | 竞品B |
|------|--------|-------|-------|
| 链支持 | | | |
| 手续费/税率 | | | |
| 代币模型 | | | |
| 推荐机制 | | | |
| 审计报告 | | | |
| 差异化优势 | | | |
```

## 输出规范

1. **所有数值必须附带计算过程**, 不接受直接给出结果
2. **所有比例必须验证总和** = 100% (或明确说明溢出/不足原因)
3. **资金相关流程必须画出流向图** (使用 Mermaid)
4. **权限模型必须列出角色矩阵** (谁能做什么)
5. **风险项必须标注严重等级**: CRITICAL / HIGH / MEDIUM / LOW
6. **参数建议必须给出范围和理由**, 不要给单一数值

## 常见错误

| 错误 | 后果 | 修复 |
|------|------|------|
| 手续费比例之和 != 100% | 资金泄漏或合约revert | 写入合约前校验总和 |
| 代币释放没有悬崖期 | 团队/投资者砸盘 | 至少6个月cliff + 线性释放 |
| APR计算未考虑代币增发 | 用户实际收益远低于预期 | 用实际通胀率修正APR |
| 没有紧急暂停机制 | 被攻击时无法止损 | 添加 Pausable + 多签触发 |
| 预言机单一数据源 | 价格操纵风险 | 多源聚合 + TWAP |
| 前端精度与合约不一致 | 用户看到的和实际不同 | 统一使用合约精度(如18位) |
| LP/合约地址未排除反射 | LP池吃掉大量反射分红 | excludeFromReward(lpAddr) |
| swapAndLiquify无阈值 | 每笔交易都触发回流, Gas爆炸 | 设置 numTokensSellToAddToLiquidity |
| 推荐关系可修改 | 恶意篡改上级, 截流奖励 | inviter绑定后 require(inviter[user] == address(0)) |
| 级差遍历无上限 | 深层级链Gas超限, 交易失败 | 硬编码 MAX_LEVEL <= 10 |
| 团队奖无自身投入要求 | 零成本薅团队奖 | getUserLevel需检查selfAmount |
| bindInviter无防刷 | 批量合约刷假团队 | 要求最低质押额才能绑定 |
| 团队业绩unstake不扣减 | 质押->领奖->撤出, 业绩虚高 | unstake时向上递归减teamAmount |
| Owner可无限修改税率 | 设100%税率锁死资金 | 税率上限硬编码(如maxTax=25%) |
| 用 transfer() 测试买卖税 | from/to 不是 pair 地址, 税率逻辑不触发, 测试结果完全失真 | 必须通过 PancakeSwap/Uniswap Router v2 的 swapExactETHForTokensSupportingFeeOnTransferTokens / swapExactTokensForETHSupportingFeeOnTransferTokens 接口测试 |
