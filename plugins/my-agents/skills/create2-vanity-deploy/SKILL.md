---
name: create2-vanity-deploy
description: 当用户提到靓号地址, 0x1111/8888 前后缀, cast create2, CREATE2 部署脚本, 或 CREATE2 单元测试时应使用此技能
metadata: {"clawdbot":{"emoji":"yellow","os":["darwin","linux"],"requires":{"bins":["forge","cast"]},"install":[{"id":"forge","kind":"bash","raw":"curl -L https://foundry.paradigm.xyz | bash && foundryup","bins":["forge","cast"],"label":"安装 Foundry (forge/cast)"}]}}
---

# CREATE2 靓号部署

## 工具预检

| 工具 | 用途 | 检测命令 |
|------|------|----------|
| forge | 编译/测试/部署 | `which forge` |
| cast | 链上交互 | `which cast` |

- 任何工具缺失 -> 立即停止, 报告用户安装后再继续

## 标准流程

```bash
# 1. 搜索 salt
forge script script/<path>/FindVanitySalt.s.sol --offline

# 2. 将输出的 VANITY_SALT 写入 .env

# 3. 测试验证地址一致
forge test --match-path test/<path>/Create2Vanity.t.sol -vvv --offline

# 4. 部署
forge script script/<path>/DeployVanity.s.sol --broadcast
```

## 环境变量配置 (.env)

```bash
# 必需
PRIVATE_KEY=0x...
VANITY_SALT=0x...  # 由 FindVanitySalt 脚本生成

# 可选
VANITY_TARGET=0x1111          # 目标后缀 (默认 0x1111)
VANITY_MAX_ITER=500000        # 最大迭代次数 (默认 500000)
VANITY_MODE=suffix            # suffix(后缀) 或 prefix(前缀)
```

## 核心文件

| 文件 | 用途 |
|------|------|
| `FindVanitySalt.s.sol` | 搜索 salt |
| `DeployVanity.s.sol` | 使用 salt 部署合约 |
| `Create2Vanity.t.sol` | 验证 CREATE2 地址计算 |

## 模板文件

参考 `resources/` 目录下的模板:

- [find-salt-script-template.md](create2-vanity-deploy/resources/find-salt-script-template.md) - 搜索 salt 脚本
- [deploy-script-template.md](create2-vanity-deploy/resources/deploy-script-template.md) - 部署脚本
- [create2-vanity-test-template.md](create2-vanity-deploy/resources/create2-vanity-test-template.md) - 单元测试

## CREATE2 地址计算

```solidity
function computeCreate2Address(
    address deployer,
    bytes32 salt,
    bytes32 initCodeHash
) internal pure returns (address) {
    return address(
        uint160(uint256(keccak256(
            abi.encodePacked(hex"ff", deployer, salt, initCodeHash)
        )))
    );
}
```

## initCode 计算

```solidity
// initCode = creationCode + encoded constructor args
bytes memory initCode = abi.encodePacked(
    type(YourContract).creationCode,
    abi.encode(constructorArgs...)
);
bytes32 initCodeHash = keccak256(initCode);
```

## 安全要点

见: [permissionless-security-notes.md](create2-vanity-deploy/resources/permissionless-security-notes.md)

- CREATE2 工厂不加 access control 是行业通用设计
- 地址由 `deployer + salt + initCodeHash` 决定, 与调用者身份无关
- `same salt + same initCode` 只能部署一次
- 注意 front-running 风险和参数漂移风险

## 注意事项

- `VANITY_TARGET` 写 `0x1111` 表示十六进制后缀 `...1111`, 写 `1111` 是十进制 `0x457`
- 构造参数会改变 `initCode`, 参数变化后需要重新搜索 salt
- 测试和部署必须使用相同的 deployer (私钥)
- initCode = creationCode + abi.encode(constructor args)

## 检查清单

- [ ] 已搜索 salt 并获取 VANITY_SALT
- [ ] 已验证部署地址符合目标靓号 (前后缀匹配)
- [ ] 测试和部署使用相同的 deployer (私钥)
- [ ] 构造参数未改变 (如有改变需重新搜索 salt)
- [ ] .env 中已配置 PRIVATE_KEY 和 VANITY_SALT
- [ ] 已运行离线测试验证地址计算正确
- [ ] 目标网络地址空间未被占用 (可选但建议检查)
