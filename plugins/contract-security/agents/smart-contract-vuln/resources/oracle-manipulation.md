# Oracle 操纵 / 假代币抵押攻击

**关键词**: oracle-manipulation, fake-collateral, spot-price, TWAP, DEX-lending, price-feed, flashloan-oracle, liquidity-pool-manipulation

**来源URL**:
- CertiK Alert (Rhea Finance): https://x.com/CertiKAlert/status/2044791732575912321
- SlowMist Hacked DB: https://hacked.slowmist.io/zh/
- BeInCrypto: https://beincrypto.com/rhea-finance-near-exploit-oracle/
- MEXC News: https://www.mexc.com/news/1032272
- DefiLlama: https://defillama.com/protocol/rhea-finance

**适用范围**: 所有依赖 DEX/AMM spot price 作为抵押品估值或清算价格的借贷协议, 收益聚合器, 衍生品协议

## 核心原因

协议直接使用单一低流动性 DEX 池的瞬时 spot price 作为资产估值依据 + 抵押品准入缺乏白名单/流动性/池龄过滤 -> 攻击者以极小成本创建假代币池并扭曲价格 -> Oracle 返回虚假高价 ->  worthless 代币被当作高价值 collateral -> 借出/提取真实资产

## 漏洞原理

Oracle 操纵的本质是协议**信任了不可信的价格源**. 当借贷协议直接使用 DEX 池余额计算的价格作为抵押品价值时, 任何人都可以通过注入流动性来操纵该价格.

典型漏洞代码模式: 直接使用 `getReserves()` 的 spot price 作为抵押品价格, 而非 TWAP 或多源聚合:

```solidity
contract VulnerableLending {
    IPair public pair;
    
    // 有漏洞: 直接使用池子的瞬时 spot price
    function getCollateralValue(address token, uint256 amount) public view returns (uint256) {
        (uint112 reserve0, uint112 reserve1, ) = pair.getReserves();
        
        // 假设 token0 是抵押品, token1 是计价资产(如 USDC)
        // 这个价格可以被任何人在单个 tx 内操纵
        uint256 price = uint256(reserve1) * 1e18 / reserve0;
        return amount * price / 1e18;
    }
    
    function borrow(address collateralToken, uint256 collateralAmount, uint256 borrowAmount) external {
        uint256 collateralValue = getCollateralValue(collateralToken, collateralAmount);
        require(collateralValue >= borrowAmount, "insufficient collateral");
        
        // 将 worthless 代币作为高价值抵押, 借出真实资产
        IERC20(borrowToken).transfer(msg.sender, borrowAmount);
    }
}
```

### 触发条件
1. 协议接受任意 token 作为抵押品(无白名单)
2. Oracle 从单一 DEX 池读取 spot price(无 TWAP/多源校验)
3. 新创建的池子没有流动性深度/池龄/交易量门槛即可被 Oracle 采纳
4. 没有 price deviation circuit breaker

## 变种与衍生

| 变种 | 区别 | 检测差异 |
|------|------|----------|
| **Flash Loan Spot Price Manipulation** | 用闪电贷在单个 tx 内临时扭曲已存在的大池子价格 | 检查 Oracle 是否用 TWAP, 借贷/清算函数是否有闪电贷防护 |
| **Fake Collateral / Fresh Pool Attack** | 攻击者自己部署假 token 并创建全新低流动性池 | 检查抵押品白名单, 池子年龄和 TVL 门槛, 新资产隔离机制 |
| **Oracle Latency MEV** | 利用预言机更新延迟, 在价格剧烈波动后抢先清算或借款 | 检查预言机心跳频率, 清算/借款是否有价格新鲜度校验 |
| **Cross-Chain Price Relay Manipulation** | 跨链桥价格中继层被操纵, 导致目标链定价失真 | 检查跨链价格消息的来源验证, 延迟确认, 多签/共识机制 |

## 审计检查清单

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 1 | 借贷协议的抵押品是否有严格白名单, 禁止任意 FT/ERC-20 直接作为抵押 | 高 |
| 2 | Oracle 是否使用 TWAP (至少30分钟窗口) 而非单一 DEX 的 spot price | 高 |
| 3 | Oracle 是否有最小流动性深度, 池龄, 交易量门槛过滤 | 高 |
| 4 | 是否有价格偏离检查 (multi-source 对比 / circuit breaker / 最大波动阈值) | 高 |
| 5 | DEX 的新池创建是否与借贷协议的抵押品估值系统隔离 | 高 |
| 6 | 对于新上线资产, 是否有借贷限额 / 隔离市场 / 初始 LTV 上限机制 | 中 |
| 7 | 清算逻辑是否也使用同样的 Oracle, 避免清算价格和抵押品价格来自不同源 | 中 |
| 8 | 协议是否验证 token 合约的元数据/已知合约列表/排除可疑新部署 | 中 |

## 检测方法

1. **Grep 搜索关键词**:
   ```
   getReserves\(\)
   spot price
   IUniswapV2Pair\( *\).getReserves
   IUniswapV3Pool\( *\).slot0
   oracle = .*pair
   ```

2. **Slither 检测**:
   - 查找 `getReserves()` 调用位置, 追踪其是否被用于资产估值/清算逻辑
   - 查找外部价格源调用, 确认是否有 TWAP 或多源聚合

3. **Foundry 模拟测试框架**:
   ```solidity
   // 测试: 创建假 token -> 建池 -> 注入流动性扭曲价格 -> 作为抵押借出资产
   function testOracleManipulation() public {
       // 1. 部署假 token
       MockToken fakeToken = new MockToken();
       
       // 2. 创建新池并添加极端比例的流动性
       fakeToken.mint(address(this), 1e18);
       usdc.mint(address(this), 1e6); // 仅 1 USDC
       pair = factory.createPair(address(fakeToken), address(usdc));
       router.addLiquidity(address(fakeToken), address(usdc), 1e18, 1e6, 0, 0, address(this), block.timestamp);
       
       // 3. 将假 token 作为抵押
       fakeToken.approve(address(lending), type(uint256).max);
       lending.deposit(address(fakeToken), 1e18);
       
       // 4. 尝试借出大量真实资产 (期望失败, 若成功则存在漏洞)
       vm.expectRevert();
       lending.borrow(address(usdc), 1000e6);
   }
   ```

## 真实案例

| 事件 | 日期 | 损失 | 根因 | 攻击链 |
|------|------|------|------|--------|
| Rhea Finance (NEAR) | 2026-04-16 | ~$7.6M | 使用单一低流动性 DEX 池 spot price + 无抵押品白名单/池龄过滤 | 部署假 FT -> 在 Ref Finance 创建新池 -> 注入流动性扭曲价格 -> Oracle 采信虚假高价 -> 存入 worthless 假币作为抵押 -> 借出 USDC/USDT/NEAR/ZEC -> 撤离 |
