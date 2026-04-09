# 常见错误

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
| 用 transfer() 测试买卖税 | from/to 不是 pair 地址, 税率逻辑不触发, 测试结果完全失真 | 必须通过 Router 的 SupportingFeeOnTransferTokens 接口测试 |
