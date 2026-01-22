---
name: hardhat2-fork-testing
description: Use when testing smart contracts with Hardhat v2 against deployed mainnet/testnet contracts, need to impersonate existing addresses without private keys, or want to test with real chain state
---

# Hardhat v2 Fork Testing

## Overview
使用 Hardhat v2 Network 的 fork 功能，在本地环境中模拟主网/测试网状态，无需私钥即可模拟任何地址进行测试。

**注意：Hardhat v3 语法不同，本技能仅适用于 Hardhat v2**

## When to Use

```dot
digraph when_fork {
    "需要测试已部署合约?" [shape=diamond];
    "没有私钥?" [shape=diamond];
    "需要真实链状态?" [shape=diamond];
    "使用 Fork 测试" [shape=box];
    "使用普通测试" [shape=box];

    "需要测试已部署合约?" -> "没有私钥?";
    "没有私钥?" -> "需要真实链状态?";
    "需要真实链状态?" -> "使用 Fork 测试" [label="是"];
    "需要真实链状态?" -> "使用普通测试" [label="否"];
    "没有私钥?" -> "使用 Fork 测试" [label="是"];
    "没有私钥?" -> "使用普通测试" [label="否"];
}
```

**使用场景：**
- 测试与已部署合约的交互
- 模拟任意地址（无需私钥）
- 验证升级后的合约兼容性
- 在真实链状态上测试复杂交互

**不使用：**
- 简单的单元测试（使用本地网络即可）
- 不依赖链状态的逻辑测试

## Core Pattern

**Before (直接连接真实网络):**
```typescript
// ❌ 不支持 impersonateAccount
const signers = await ethers.getSigners();
user = signers[0]; // 只能用配置的账户
```

**After (使用 fork):**
```typescript
// ✅ 可以模拟任何地址
await ethers.provider.send("hardhat_impersonateAccount", [TARGET_ADDRESS]);
user = await ethers.getSigner(TARGET_ADDRESS);
```

## Quick Reference

| 操作 | 命令/代码 |
|------|----------|
| **启动 fork 测试** | `FORK_ENABLED=true FORK_URL=<RPC_URL> bunx hardhat test --network hardhat` |
| **模拟账户** | `await ethers.provider.send("hardhat_impersonateAccount", [address])` |
| **设置账户余额** | `await ethers.provider.send("hardhat_setBalance", [address, balance])` |
| **推进时间** | `await ethers.provider.send("evm_increaseTime", [seconds])` |
| **挖出新块** | `await ethers.provider.send("evm_mine", [])` |

## Implementation

### 1. hardhat.config.ts 配置 (Hardhat v2)

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

### 2. 测试文件模板 (Hardhat v2)

```typescript
import { ethers } from "hardhat";
import { expect } from "chai";
import { parseEther } from "ethers";

describe("Fork test", function () {
  const TARGET_ADDRESS = "0x1234...";  // 要模拟的地址
  const CONTRACT_ADDRESS = "0xabcd..."; // 已部署的合约地址

  let contract: any;
  let user: any;

  this.beforeAll(async function () {
    const network = await ethers.provider.getNetwork();
    const isHardhat = network.chainId === BigInt(31337) || network.chainId === BigInt(1337);

    // 获取已部署合约
    const factory = await ethers.getContractFactory("ContractName");
    contract = factory.attach(CONTRACT_ADDRESS);

    if (isHardhat) {
      // Fork 环境：模拟账户
      await ethers.provider.send("hardhat_impersonateAccount", [TARGET_ADDRESS]);
      user = await ethers.getSigner(TARGET_ADDRESS);

      // 给账户转入 BNB 用于 gas
      const [signer] = await ethers.getSigners();
      await signer.sendTransaction({
        to: TARGET_ADDRESS,
        value: parseEther("1"),
      });
    } else {
      // 真实网络：使用配置的账户
      const signers = await ethers.getSigners();
      user = signers[0];
    }
  });

  it("测试场景", async function () {
    // 使用 user 进行测试
    const tx = await contract.connect(user).someMethod();
    await tx.wait();
  });
});
```

### 3. 运行测试 (Hardhat v2)

```bash
# 使用 bunx (推荐)
FORK_ENABLED=true FORK_URL=https://your-rpc-url bunx hardhat test test/YourTest.ts --network hardhat

# 或使用 npx
FORK_ENABLED=true FORK_URL=https://your-rpc-url npx hardhat test test/YourTest.ts --network hardhat

# 或者在 hardhat.config.ts 中预设 URL，只需启用
FORK_ENABLED=true bunx hardhat test test/YourTest.ts --network hardhat
```

## Common Mistakes

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `hardhat_impersonateAccount does not exist` | 直接连接真实网络，不是 fork 环境 | 使用 `--network hardhat` 并启用 fork |
| `missing trie node` | RPC 节点不是归档节点 | 使用 Alchemy/QuickNode 等归档节点 |
| `insufficient funds for gas` | 模拟账户没有 BNB | 用 `hardhat_setBalance` 或转账 |
| 测试在真实网络执行 | 使用了 `--network bscTestnet` | 使用 `--network hardhat` |

## RPC 节点要求

**必须使用归档节点**，公共节点通常不支持 fork：

| 网络 | 推荐归档节点 |
|------|-------------|
| Ethereum | Alchemy, Infura |
| BSC 主网 | Alchemy, QuickNode |
| BSC 测试网 | QuickNode (公共节点不支持) |
| Polygon | Alchemy, QuickNode |

## Hardhat v2 vs v3

| 特性 | Hardhat v2 | Hardhat v3 |
|------|-----------|-----------|
| Provider API | `ethers.provider.send()` | `hre.viem.getPublicClient()` |
| Signer 获取 | `ethers.getSigner()` | `hre.viem.getWalletClient()` |
| Time 操作 | `evm_increaseTime` | `setNextBlockTimestamp` |
| Fork 配置 | `networks.hardhat.forking` | 不同配置方式 |
