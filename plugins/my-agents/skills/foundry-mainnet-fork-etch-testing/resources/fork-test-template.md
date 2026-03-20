# Fork 测试模板

适用:
- 链上旧地址 + 本地新 runtime code 回放
- 主网真实 Router/Pair 行为验证

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "forge-std/Test.sol";
import "../../src/jm/JMTokenV2.sol";
import "../../src/jm/interfaces/IPancakeRouter.sol";
import "../../src/jm/interfaces/IPancakePair.sol";

contract ExampleForkTest is Test {
    JMTokenV2 jmToken;
    IPancakeRouter router;
    IPancakePair pair;
    address wbnb;

    // 固定测试地址,确保测试可重复
    address constant USER = 0x1234567890123456789012345678901234567890;

    function setUp() public {
        vm.createSelectFork("bsc_mainnet");

        address tokenAddr = vm.envAddress("JM_TOKEN");
        vm.etch(tokenAddr, type(JMTokenV2).runtimeCode);

        jmToken = JMTokenV2(payable(tokenAddr));
        // 从合约读取关联地址,禁止硬编码
        router = IPancakeRouter(jmToken.pancakeRouter());
        pair = IPancakePair(jmToken.lpPair());
        wbnb = router.WETH();
    }

    function test_BuyThenSell() public {
        address user = USER;
        vm.deal(user, 0.05 ether);

        _buy(user, 0.008 ether);

        uint256 jmAfterBuy = jmToken.balanceOf(user);
        assertGt(jmAfterBuy, 0, unicode"买入后应有JM");

        _sell(user, jmAfterBuy / 2);

        assertLt(
            jmToken.balanceOf(user),
            jmAfterBuy,
            unicode"卖出后JM应减少"
        );
    }

    function _buy(address user, uint256 bnbAmount) internal {
        address[] memory path = new address[](2);
        path[0] = wbnb;
        path[1] = address(jmToken);

        vm.prank(user);
        router.swapExactETHForTokensSupportingFeeOnTransferTokens{value: bnbAmount}(
            0,
            path,
            user,
            block.timestamp + 300
        );
    }

    function _sell(address user, uint256 jmAmount) internal {
        address[] memory path = new address[](2);
        path[0] = address(jmToken);
        path[1] = wbnb;

        vm.startPrank(user);
        jmToken.approve(address(router), jmAmount);
        router.swapExactTokensForETHSupportingFeeOnTransferTokens(
            jmAmount,
            0,
            path,
            user,
            block.timestamp + 300
        );
        vm.stopPrank();
    }
}
```

最小改造点:
- 替换 `JM_TOKEN`
- 替换测试用户地址
- 补充你的业务断言
- 如需验证官方加LP, 直接 `call{value: amount}("")` 给代币合约
