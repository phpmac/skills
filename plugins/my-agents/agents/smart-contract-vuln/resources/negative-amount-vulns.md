# 负数金额漏洞

**关键词**: negative-amount, signed-integer, int128-bypass, missing-positive-check, donation-drain, withdraw-disguised, zero-value-attack, unsigned-integer-missing, Int128-vs-Uint128, input-validation, amount-check

**来源URL**:
- Dango 官方公告: https://x.com/dango/status/2043669424805216745
- Dango 后续更新 (白帽子归还): https://x.com/dango/status/2043710283244331409
- 白帽子 pozersol 分析: https://x.com/pozersol/status/2043701837056876779
- 社区技术分析: https://x.com/0xasrequired/status/2043694280422641801
- Quillaudits Donation 攻击研究: https://quillaudits.medium.com/resupply-hack-how-a-donation-attack-led-to-9-5m-in-losses-91e4e34d3bf5
- Compound Fork 捐赠攻击: https://dev.to/ohmygod/donation-attacks-on-compound-fork-lending-protocols-dissecting-the-venus-protocol-the-exploit-dn8
- Phemex 事件报道: https://phemex.com/news/article/dango-defi-platform-suffers-410010-usdc-exploit-due-to-logic-flaw-72936

**适用范围**: 所有处理金额/数量的智能合约, 包括:
- DeFi 协议 (借贷/交易/质押/保险基金)
- 跨链桥资产操作
- NFT 市场 (批量转账/定价)
- 任何接受外部金额输入的公开函数
- Rust/CosmWasm/Solidity/Move 等所有智能合约语言

## 漏洞原理

### 核心问题: 有符号整数 + 缺少正数校验

当合约的金额参数使用有符号整数类型 (`int128`/`int256`/`Int128`/`i128`) 时, 调用者可以传入负数. 如果函数内部没有显式校验 `amount > 0`, 负数会进入不同的逻辑分支, 可能导致:

1. **余额减少而非增加**: `fund += amount` 当 `amount < 0` 时变为减少
2. **取反后转出**: `transfer(caller, abs(amount))` 将资金发给调用者
3. **条件绕过**: 某些 `require(amount >= minAmount)` 在负数下可能产生非预期行为

### 漏洞代码 (Dango 保险基金 - Rust/CosmWasm)

```rust
// src/insurance.rs (漏洞版本)

use cosmwasm_std::{
    DepsMut, Env, MessageInfo, Response, Int128, Uint128, BankMsg, coins, StdResult
};
use cw_storage_plus::Item;

pub const INSURANCE_FUND: Item<Uint128> = Item::new("insurance_fund");

#[derive(cw_serde)]
pub enum ExecuteMsg {
    // 危险: amount 使用有符号整数 Int128
    DonateToInsurance { amount: Int128 },
    // ... 其他消息
}

pub fn execute_donate_to_insurance(
    deps: DepsMut,
    _env: Env,
    info: MessageInfo,
    amount: Int128,
) -> Result<Response, ContractError> {
    // 只校验了零, 没有拒绝负数!
    if amount.is_zero() {
        return Err(ContractError::InvalidAmount {});
    }
    // ============================================
    // 缺少: if amount < Int128::zero() { return Err(...); }
    // ============================================

    let mut fund = INSURANCE_FUND.load(deps.storage).unwrap_or_default();
    let mut messages = vec![];

    if amount > Int128::zero() {
        // 正常路径: 余额增加
        let add = Uint128::try_from(amount)
            .map_err(|_| ContractError::InvalidAmount {})?;
        fund = fund.checked_add(add)?;
    } else {
        // ========== 攻击路径: 负数进入这里 ==========
        // -amount 得到正数, 变成提款金额
        let withdraw = Uint128::try_from(-amount)
            .map_err(|_| ContractError::InvalidAmount {})?;
        fund = fund.checked_sub(withdraw)?;
        // 将 USDC 从合约转给调用者!
        messages.push(BankMsg::Send {
            to_address: info.sender.to_string(),
            amount: coins(withdraw.u128(), "usdc"),
        });
    }

    INSURANCE_FUND.save(deps.storage, &fund)?;

    Ok(Response::new()
        .add_messages(messages)
        .add_attribute("action", "donate_to_insurance")
        .add_attribute("amount", amount.to_string()))
}
```

### 等价的 Solidity 漏洞模式

```solidity
// Solidity 中同样的问题

// 危险写法: 使用 int256
function donate(int256 amount) external {
    // 缺少: require(amount > 0, "positive only");
    if (amount > 0) {
        insuranceFund += uint256(amount);
    } else {
        // 负数变成提款
        uint256 withdraw = uint256(-amount);
        insuranceFund -= withdraw;
        IERC20(usdc).transfer(msg.sender, withdraw); // 资金转出!
    }
}

// 安全写法: 使用 uint256 + 显式校验
function donate(uint256 amount) external {
    require(amount > 0, "zero amount");
    // ... 只处理正数
}
```

### 修复代码

```rust
// 修复方案1: 使用无符号类型 (推荐)
#[derive(cw_serde)]
pub enum ExecuteMsg {
    DonateToInsurance { amount: Uint128 },  // Uint128: 负数不可能存在
}

pub fn execute_donate_to_insurance(
    deps: DepsMut,
    _env: Env,
    info: MessageInfo,
    amount: Uint128,
) -> Result<Response, ContractError> {
    if amount.is_zero() {
        return Err(ContractError::InvalidAmount {});
    }

    let mut fund = INSURANCE_FUND.load(deps.storage).unwrap_or_default();
    fund = fund.checked_add(amount)?;

    INSURANCE_FUND.save(deps.storage, &fund)?;
    Ok(Response::new()
        .add_attribute("action", "donate_to_insurance")
        .add_attribute("amount", amount.to_string()))
}

// 修复方案2: 如果必须用有符号类型, 显式拒绝负数
pub fn execute_donate_to_insurance(
    deps: DepsMut,
    _env: Env,
    info: MessageInfo,
    amount: Int128,
) -> Result<Response, ContractError> {
    if amount <= Int128::zero() {
        return Err(ContractError::InvalidAmount {});
    }
    // ... 只处理正数
}
```

### 攻击流程图

```
攻击者调用: DonateToInsurance { amount: Int128::from(-1_900_000_000_000) }
   |
   v
[1] amount.is_zero() = false -> 通过
   |
   v
[2] amount > Int128::zero() = false -> 进入 else 分支
   |
   v
[3] withdraw = Uint128::try_from(-(-1_900_000)) = 1_900_000
   |
   v
[4] fund = fund.checked_sub(1_900_000) -> 保险基金减少 $1.9M
   |
   v
[5] BankMsg::Send { 1_900_000 USDC -> 攻击者 } -> 资金转出
   |
   v
[6] 攻击者尝试桥接到以太坊:
    -> 成功: $410,010 (速率限制内)
    -> 卡住: $1,490,012 (超出速率限制, 留在 Dango 链上)
   |
   v
[7] 团队暂停链, 恢复资金
   |
   v
[8] 白帽子全额归还, 获得 bug bounty, 用户零损失

攻击者 Dango 地址: 0x023ef9e3e20caca6ef3743cbfba6469d69978999
攻击者 ETH 地址:   0x271d1f2f4194e61f2a17ea82d82e31cea9f6762a
```

## 变种与衍生

**变种1: donation 函数变提款 (Dango 模式)**
- 公开的 donate 函数接受负数, else 分支触发转出逻辑
- 差异: 函数本意是双向 (存入/提取), 但缺少权限控制
- 检测要点: 所有包含 if-else 正负分支的金融函数

**变种2: 余额操纵 via 大额捐赠 (Euler 模式)**
- 向池/金库捐赠大量代币操纵汇率, 不一定是负数
- 差异: 利用正数大额捐赠扭曲 share/token 比率, 不直接提款
- 检测要点: ERC4626 vault 的 donate/deposit 是否影响 totalSupply/totalAssets 计算

**变种3: 零值攻击**
- 传入 amount=0 绕过某些逻辑或触发非预期状态变更
- 差异: 不造成直接资金损失, 但可能触发空事件/空状态更新
- 检测要点: 搜索 `require(amount > 0)` 是否真的覆盖了所有路径

**变种4: 整数类型转换漏洞**
- Rust 中 `Int128::try_from()` / `Uint128::try_from()` 的边界行为
- 差异: 类型转换可能静默失败或产生意外值
- 检测要点: 搜索所有 `try_from`/`into()`/`as` 类型转换, 验证边界

**变种5: 反向操作函数伪装**
- stake(-amount) 变成 unstake, deposit(-amount) 变成 withdraw
- 差异: 函数名暗示单向操作, 但参数类型允许反向
- 检测要点: 所有参数名暗示单向 (deposit/stake/donate/add) 但用了有符号类型的函数

## 审计检查清单

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 1 | 所有金融函数的金额参数是否使用无符号类型 (uint256/Uint128) | 严重 |
| 2 | 如果必须用有符号类型, 是否有 `require(amount > 0)` | 严重 |
| 3 | 所有公开 (public/external) 函数的数值参数是否有正数校验 | 严重 |
| 4 | if-else 正负分支的函数是否需要权限控制 | 严重 |
| 5 | 类型转换 (Int128->Uint128) 是否处理了负数输入 | 高 |
| 6 | donate/deposit/stake 等函数是否真的需要对外开放 | 高 |
| 7 | 保险基金/金库的余额变更是否有 rate limit/cap | 中 |
| 8 | 金额计算中是否有 checked_add/checked_sub 或 SafeMath | 高 |
| 9 | 是否有 pause/emergency 机制阻止异常提款 | 中 |
| 10 | 错误处理路径是否可能静默吞掉负数错误 | 高 |

## 检测方法

1. **Grep 搜索**:
   ```
   # 搜索有符号整数参数 (Rust)
   grep -rn "Int128\|int128\|Int256\|int256\|i128\|i256" contracts/

   # 搜索有符号整数参数 (Solidity)
   grep -rn "int256\|int128\|int64" src/

   # 搜索缺少正数校验的函数
   grep -B3 "function.*donate\|function.*deposit\|function.*stake" | grep -v "require.*> 0\|require.*> 0"

   # 搜索 if-else 正负分支模式
   grep -A10 "if.*amount.*>.*0\|if.*amount.*>.*zero" | grep "else\|BankMsg::Send\|transfer"

   # 搜索公开的金额处理函数
   grep -rn "pub fn.*amount.*Int\|external.*int256\|public.*int256"
   ```

2. **Slither 检测**:
   ```
   # 检测有符号整数的使用
   slither --detect signed-integer-usage .

   # 检测缺少输入验证
   slither --detect missing-input-validation .
   ```

3. **Foundry/Forge 边界测试**:
   ```solidity
   // 测试负数金额应被拒绝
   function test_RevertNegativeAmount() public {
       vm.expectRevert("positive amount only");
       insurance.donate(-1000);
   }

   // 测试零值应被拒绝
   function test_RevertZeroAmount() public {
       vm.expectRevert("zero amount");
       insurance.donate(0);
   }

   // 测试正数金额正常工作
   function test_PositiveDonation() public {
       uint256 balanceBefore = usdc.balanceOf(address(insurance));
       insurance.donate(1000e6);
       assertEq(insurance.fundBalance(), balanceBefore + 1000e6);
   }

   // Fuzz: 测试所有负数和零都被拒绝
   function testFuzz_OnlyPositiveAllowed(int256 amount) public {
       vm.assume(amount <= 0);
       vm.expectRevert();
       insurance.donate(amount);
   }

   // Fuzz: 测试所有正数正常处理
   function testFuzz_PositiveWorks(uint256 amount) public {
       vm.assume(amount > 0 && amount < MAX_FUND);
       insurance.donate(int256(amount));
       assertEq(insurance.fundBalance(), amount);
   }
   ```

4. **CosmWasm 单元测试**:
   ```rust
   #[test]
   fn reject_negative_donation() {
       let mut app = App::default();
       let err = app.execute_contract(
           Addr::unchecked("attacker"),
           insurance_addr.clone(),
           &ExecuteMsg::DonateToInsurance { amount: Int128::from(-1000) },
           &[],
       );
       assert!(err.is_err(), "negative amount should be rejected");
   }

   #[test]
   fn reject_zero_donation() {
       let err = app.execute_contract(
           Addr::unchecked("user"),
           insurance_addr.clone(),
           &ExecuteMsg::DonateToInsurance { amount: Int128::zero() },
           &[],
       );
       assert!(err.is_err(), "zero amount should be rejected");
   }
   ```

## 真实案例

| 事件 | 日期 | 损失 | 根因 | 分析链接 |
|------|------|------|------|----------|
| [Dango](https://x.com/dango/status/2043669424805216745) | 2026-04-13 | ~$410K (已归还) | 保险基金 donate 函数接受负数 Int128, else 分支触发 BankMsg::Send 转出资金 | [官方公告](https://x.com/dango/status/2043669424805216745) / [归还更新](https://x.com/dango/status/2043710283244331409) / [pozersol 分析](https://x.com/pozersol/status/2043701837056876779) |
| [Euler Finance](https://etherscan.io/tx/0xc310a0affe2169d1f6feec1c63dbc7f7c62a887fa48795d327d4d2da2d2bbaaa) | 2023-03-13 | $197M (后归还) | donateToVault 捐赠机制操纵 ETH/dai 池汇率, 利用 donate 扭曲 share/asset 比率实现低抵押借贷 | [rekt.news](https://rekt.news/euler-rekt/) / [CoinDesk 分析](https://www.coindesk.com/tech/2023/03/13/euler-finance-suffers-197m-exploit/) |
| [Resupply](https://quillaudits.medium.com/resupply-hack-how-a-donation-attack-led-to-9-5m-in-losses-91e4e34d3bf5) | 2025 | $9.5M | donation 攻击导致借贷协议保险基金余额被操纵, 通过捐赠扭曲汇率实现低抵押借贷 | [Quillaudits 分析](https://quillaudits.medium.com/resupply-hack-how-a-donation-attack-led-to-9-5m-in-losses-91e4e34d3bf5) |
| [Venus Protocol](https://dev.to/ohmygod/donation-attacks-on-compound-fork-lending-protocols-dissecting-the-venus-protocol-the-exploit-dn8) | 2024 | ~$200K | Compound fork 的捐赠攻击, 通过大额捐赠扭曲利率模型和利用率计算 | [技术分析](https://dev.to/ohmygod/donation-attacks-on-compound-fork-lending-protocols-dissecting-the-venus-protocol-the-exploit-dn8) |
