# ERC20 手续费代币机制 (SafeMoon 类)

设计转账自动扣税代币时, 必须明确以下参数:

## 核心机制 - 每笔转账自动拆分

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

## 反射(Reflection)机制原理

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

## 测试规范 - 机制代币买卖税必须用 Router 测试

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

## 安全审查清单

- [ ] 是否有 `excludeFromFee` 白名单 (合约/路由器/LP必须排除, 否则交易失败)
- [ ] 是否有 `excludeFromReward` (防止LP池/合约地址吃反射)
- [ ] `maxTxAmount` 单笔最大交易限制 (防鲸鱼砸盘)
- [ ] `maxWalletBalance` 单地址最大持仓 (防集中持仓)
- [ ] `swapAndLiquify` 阈值是否合理 (太低频繁触发Gas高, 太高影响价格)
- [ ] Owner 是否可以修改税率 (应有上限限制或时间锁)
- [ ] 是否可以关闭交易 (Owner禁止交易 = 跑路后门, CRITICAL风险)
- [ ] LP是否锁定 (未锁定 = 可以撤池跑路)

## 移除流动性单独收费 (Remove Liquidity Fee)

```
// 买入 from==pair 时, 需区分: 普通买入 vs 移除LP
// 移除LP时 pair 里的 otherToken balance 会减少, 可用此判断:

function _isRemoveLiquidity() internal view returns (bool) {
    (uint r0, uint r1,) = pair.getReserves();
    uint bal = IERC20(otherToken).balanceOf(address(pair));
    return r >= bal;  // 移除时余额先减少, reserve还没更新 -> true
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
```

### removeLiquidityFee 安全审查

- [ ] `_isRemoveLiquidity` 判断是否会误判 (正常买入被错收高税)
- [ ] removeLiquidityFee 是否有上限 (设100%可锁死撤池)
- [ ] 是否开放 `setRemoveLiquidityFee()` 给 Owner 随意修改 (应加时间锁或上限)
- [ ] 收取的费用去向是否透明 (国库/销毁/分红)

## 典型税率设计参考

| 项目类型 | 买入税 | 卖出税 | 反射 | LP回流 | 销毁 | 营销 |
|---------|--------|--------|------|--------|------|------|
| 持币分红型 | 5% | 5% | 3% | 1% | 0% | 1% |
| 通缩销毁型 | 3% | 5% | 0% | 1% | 3% | 1% |
| 营销驱动型 | 5% | 8% | 1% | 2% | 0% | 5% |
| 混合型 | 6% | 10% | 2% | 2% | 1% | 5% |
