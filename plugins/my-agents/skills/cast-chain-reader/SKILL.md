---
name: cast-chain-reader
description: 当用户要求 "读取链上合约", "查看合约数据", "链上数据读取", "cast call", "合约信息", "读取合约状态", "链上查询", "读取存储槽", "查看事件日志", "读取代币信息" 时应使用此技能. 使用 cast 工具读取 EVM 链上合约数据, 支持多链 RPC 自动切换
allowed-tools: Read, Grep, Glob, Bash
---

# 链上合约数据读取

使用 cast 读取 EVM 链上合约数据.

## 核心原则

- **工具预检**: 执行前必须检测 cast 是否已安装, 未安装则立即停止, 根据系统环境查安装方法
- **只读操作**: 仅执行读取操作, 禁止执行 cast send 等写入交易
- **显式 RPC**: 每条 cast 命令必须带 --rpc-url, 不依赖环境变量
- **地址校验**: 合约地址用 cast to-check-sum-address 校验后再使用
- **按需查阅**: 具体 cast 子命令用法通过 cast \<subcommand\> --help 实时查阅, 不写死命令

---

## 阶段 1: 环境预检与链选择

### 1.1 检测 cast

执行 `cast --version`, 未安装则停止并输出安装命令: `curl -L https://foundry.paradigm.xyz | bash && foundryup`

### 1.2 默认链与 RPC

默认使用 BSC 链, RPC: `https://icy-sly-rain.bsc.quiknode.pro/144c3b82f11e9ba4b2d3bf02aaab284b25528c42/`

该节点无私钥速率限制, 无需分批查询. 如用户需要其他链, 可切换:

| 链 | Chain ID | 公共 RPC |
|----|----------|----------|
| Ethereum | 1 | https://eth.llamarpc.com |
| Arbitrum | 42161 | https://arb1.arbitrum.io/rpc |
| Base | 8453 | https://mainnet.base.org |
| Polygon | 137 | https://polygon-rpc.com |
| Optimism | 10 | https://mainnet.optimism.io |
| Avalanche | 43114 | https://api.avax.network/ext/bc/C/rpc |
| Fantom | 250 | https://rpc.ftm.tools |

### 1.3 验证连通性

执行 `cast block-number --rpc-url <RPC>`, 失败则提示更换 RPC

---

## 阶段 2: 识别读取模式

根据用户输入匹配模式, 不确定时用 AskUserQuestion 让用户选择:

| 模式 | 触发关键词 |
|------|-----------|
| 合约元信息 | bytecode, 合约代码, 存储槽, 代理实现, 函数选择器, ABI |
| 状态读取 | 调用函数, 读取状态, 查看变量, balanceOf, owner |
| 事件日志 | 事件, 日志, Transfer, 历史记录, log |
| 代币标准 | 代币信息, ERC20, ERC721, name, symbol, decimals |
| 交易信息 | 交易详情, tx, receipt, 交易收据 |

---

## 阶段 3: 构造并执行

根据模式, 查阅 cast --help 确认命令语法后执行. 核心子命令速查:

| 需求 | 主命令 | 用法速查 |
|------|--------|----------|
| 调用合约函数 | cast call | `cast call <ADDR> "func(types)(retTypes)" args --rpc-url <RPC>` |
| 读取存储槽 | cast storage | `cast storage <ADDR> <SLOT> --rpc-url <RPC>` |
| mapping 槽位计算 | cast index | `cast index <KEY_TYPE> <KEY> <SLOT>` |
| 查看日志 | cast logs | `cast logs [SIG] --address <ADDR> --from-block <N> --rpc-url <RPC>` |
| 合约字节码 | cast code | `cast code <ADDR> --rpc-url <RPC>` |
| 代理实现 | cast implementation | `cast implementation <ADDR> --rpc-url <RPC>` |
| 函数选择器 | cast selectors | `cast code <ADDR> \| cast selectors -r` |
| ERC20 代币 | cast erc20-token | `cast erc20-token <subcmd> --erc20 <ADDR> --rpc-url <RPC>` |
| 合约源码 | cast source | `cast source <ADDR> --chain <CHAIN> -e <API_KEY>` |
| 交易详情 | cast tx / receipt | `cast tx <HASH> --rpc-url <RPC>` |
| 常用查询 | balance/nonce/block | `cast balance/nonce/block-number --rpc-url <RPC>` |

> 具体参数和选项执行 `cast <subcommand> --help` 查阅, 禁止猜测参数

---

## 输出规范

所有结果以表格形式输出:

```
## [模式名] 结果

| 项目 | 值 |
|------|-----|
| ... | ... |
```

- uint256 值需转换为可读格式 (cast from-wei / cast to-unit)
- 多条记录并行执行, 全部完成后统一输出
- 默认 BSC 节点无速率限制, 可直接批量查询
