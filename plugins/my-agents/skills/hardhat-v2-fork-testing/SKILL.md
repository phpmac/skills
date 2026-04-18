---
name: hardhat-v2-fork-testing
description: 当用户使用 Hardhat v2 测试智能合约, 需要测试已部署的主网/测试网合约, 模拟现有地址, 或在真实链状态上进行测试时应使用此技能
metadata: {"clawdbot":{"emoji":"green","os":["darwin","linux"],"requires":{"bins":["bun"]},"install":[{"id":"bun","kind":"bash","raw":"curl -fsSL https://bun.sh/install | bash","bins":["bun"],"label":"安装 bun"}]}}
---

# Hardhat v2 Fork Testing

使用 Hardhat v2 Network 的 fork 功能, 在本地环境中模拟主网/测试网状态.

**注意: Hardhat v3 语法不同, 本技能仅适用于 Hardhat v2**

## 工具预检

| 工具 | 用途 | 检测命令 |
|------|------|----------|
| bun | 包管理/运行测试 | `which bun` |

- 任何工具缺失 -> 立即停止, 报告用户安装后再继续

## When to Use

- 测试与已部署合约的交互
- 模拟任意地址 (无需私钥)
- 验证升级后的合约兼容性
- 在真实链状态上测试复杂交互

**不使用:** 简单的单元测试 / 不依赖链状态的逻辑测试

## Quick Reference

| 操作 | 命令/代码 |
|------|----------|
| **启动 fork 测试** | `FORK_ENABLED=true FORK_URL=<RPC_URL> bunx hardhat test --network hardhat` |
| **模拟账户** | `await ethers.provider.send("hardhat_impersonateAccount", [address])` |
| **设置账户余额** | `await ethers.provider.send("hardhat_setBalance", [address, balance])` |
| **推进时间** | `await ethers.provider.send("evm_increaseTime", [seconds])` |
| **挖出新块** | `await ethers.provider.send("evm_mine", [])` |

## hardhat.config.ts 配置

```typescript
networks: {
  hardhat: {
    chainId: 1337,
    accounts: {
      mnemonic: "test test test test test test test test test test test junk",
      count: 400,
    },
    forking: {
      url: process.env.FORK_URL || "https://bsc-dataseed.binance.org/",
      blockNumber: process.env.FORK_BLOCK_NUMBER ? parseInt(process.env.FORK_BLOCK_NUMBER) : undefined,
      enabled: process.env.FORK_ENABLED === "true",
    },
  },
}
```

## 极简测试模板

```typescript
import { ethers } from "hardhat";
import { expect } from "chai";
import { parseEther } from "ethers";

describe("Fork Test", function () {
    const CONTRACT_ADDRESS = "0x...";
    const ADMIN_ADDRESS = "0x...";

    let contract: any;
    let admin: any;

    before(async function () {
        await ethers.provider.send("hardhat_impersonateAccount", [ADMIN_ADDRESS]);
        admin = await ethers.getSigner(ADMIN_ADDRESS);
        contract = await ethers.getContractAt("ContractName", CONTRACT_ADDRESS);
    });

    it("测试场景", async function () {
        const tx = await contract.connect(admin).someMethod();
        await tx.wait();
    });
});
```

## 完整测试模板

```typescript
import { ethers } from "hardhat";
import { expect } from "chai";
import { parseEther } from "ethers";

describe("Fork test", function () {
  const TARGET_ADDRESS = "0x1234...";
  const CONTRACT_ADDRESS = "0xabcd...";

  let contract: any;
  let user: any;

  this.beforeAll(async function () {
    const network = await ethers.provider.getNetwork();
    const isHardhat = network.chainId === BigInt(31337) || network.chainId === BigInt(1337);

    const factory = await ethers.getContractFactory("ContractName");
    contract = factory.attach(CONTRACT_ADDRESS);

    if (isHardhat) {
      await ethers.provider.send("hardhat_impersonateAccount", [TARGET_ADDRESS]);
      user = await ethers.getSigner(TARGET_ADDRESS);

      const [signer] = await ethers.getSigners();
      await signer.sendTransaction({
        to: TARGET_ADDRESS,
        value: parseEther("1"),
      });
    } else {
      const signers = await ethers.getSigners();
      user = signers[0];
    }
  });

  it("测试场景", async function () {
    const tx = await contract.connect(user).someMethod();
    await tx.wait();
  });
});
```

## 运行测试

```bash
# 使用 bunx (推荐)
FORK_ENABLED=true FORK_URL=https://your-rpc-url bunx hardhat test test/YourTest.ts --network hardhat

# 或在 hardhat.config.ts 中预设 URL
FORK_ENABLED=true bunx hardhat test test/YourTest.ts --network hardhat
```

## Common Mistakes

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `hardhat_impersonateAccount does not exist` | 直接连接真实网络 | 使用 `--network hardhat` 并启用 fork |
| `missing trie node` | RPC 节点不是归档节点 | 使用 Alchemy/QuickNode 等归档节点 |
| `insufficient funds for gas` | 模拟账户没有 BNB | 用 `hardhat_setBalance` 或转账 |
| `AccessControlUnauthorizedAccount` | 签名者没有权限 | 模拟合约管理员/部署者地址 |

## Useful Snippets

```typescript
// 检查余额
const balance = await token.balanceOf(address);
console.log("Balance:", ethers.formatEther(balance));

// 推进时间
await ethers.provider.send("evm_increaseTime", [3600]);
await ethers.provider.send("evm_mine", []);

// 从事件获取数据
const event = receipt.logs.find((log: any) => {
    try {
        return contract.interface.parseLog(log)?.name === "EventName";
    } catch {
        return false;
    }
});
const value = contract.interface.parseLog(event).args.paramName;

// 检查是否在 fork 环境
const network = await ethers.provider.getNetwork();
const isHardhat = network.chainId === BigInt(1337);
```

## RPC 节点要求

必须使用归档节点, 公共节点通常不支持 fork:

| 网络 | 推荐归档节点 |
|------|------------|
| Ethereum | Alchemy, Infura |
| BSC 主网 | Alchemy, QuickNode |
| BSC 测试网 | QuickNode |
| Polygon | Alchemy, QuickNode |
