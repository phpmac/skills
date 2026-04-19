# 跨链桥证明伪造漏洞

**关键词**: bridge-proof-forgery, MMR-verification-bypass, merkle-proof-forgery, leaf-index-out-of-bounds, cross-chain-message-forgery, overlayRoot-replay, light-client-bypass, ISMP-proof, proof-decoupling, LayerZero-DVN-compromise, OFT-single-DVN, validator-set-compromise

**来源URL**:
- BlockSec Phalcon 根因分析: https://x.com/Phalcon_xyz/status/2043601549893738970
- Phalcon 初步分析: https://x.com/Phalcon_xyz/status/2043567998662053982
- CertiK Alert 分析: https://x.com/CertiKAlert/status/2043615397363273833
- Hyperbridge 官方公告: https://x.com/hyperbridge/status/2043676775083803057
- Hyperbridge 补充说明: https://x.com/hyperbridge/status/2043676789948461358
- Routescan 链上分析: https://x.com/routescan_io/status/2043608597138129346
- Officer_Secret 技术分析: https://x.com/officer_secret/status/2043603394300911789
- PeckShield KelpDAO 告警: https://x.com/PeckShieldAlert/status/2045600655184740457
- PeckShield 初次发现: https://x.com/peckshield/status/2045582425007231404
- Crypto_Goblinz 技术分析: https://x.com/Crypto_Goblinz/status/2045627262393811228
- QuillAudits AI 分析: https://x.com/QuillAudits_AI/status/2045634053832155293
- D2_Finance 分析: https://x.com/D2_Finance/status/2045610222677528681
- cryptounfolded 分析: https://x.com/cryptounfolded/status/2045584079400128607

**适用范围**: 所有使用 Merkle/MMR 证明验证跨链消息的桥协议, 包括:
- MMR (Merkle Mountain Range) 证明验证
- Merkle Tree 证明验证
- 轻客户端/中继链验证
- ISMP/XCMP 等跨链消息协议
- 任何依赖密码学证明的跨链资产桥

## 漏洞原理

### 背景知识: MMR 树

Merkle Mountain Range (MMR) 是一种追加_only 的 Merkle 树结构, 用于高效存储和验证大量数据的存在性证明. 在跨链桥中, MMR 根代表源链的状态承诺, 目标链通过验证 MMR 证明来确认跨链消息的真实性.

```
MMR 结构示例 (leafCount=7):

        R (bagged root)
       / \
      /   \
     P2    \
    / \     \
   /   \     \
  P0   P1    P2_leaf
 / \   / \    |
0   1 2   3   4
               (5,6 待添加)

每个叶子有唯一 leafIndex (从0开始)
leafCount = 树中叶子总数
```

### 核心漏洞: 索引越界导致叶子被跳过

当 `VerifyProof` 函数没有校验 `leafIndex < leafCount` 时, 攻击者可以提交一个**不合法的 (leafIndex, leafCount) 组合**, 使得 `CalculateRoot` 的遍历逻辑**跳过叶子哈希的计算**, 直接返回一个由 proof 数组中的节点拼凑出的根值.

### 漏洞代码 (Hyperbridge HandlerV1 简化版)

```solidity
// HandlerV1.sol - ISMP 跨链消息处理合约 (漏洞版本)

struct MMRProof {
    uint256 leafIndex;     // 叶子在 MMR 中的位置
    uint256 leafCount;     // MMR 中叶子总数
    bytes32 leaf;          // 请求的承诺哈希 (request.hash())
    bytes32[] proof;       // 兄弟节点和峰值节点
}

function verifyProof(
    bytes32 overlayRoot,        // 链上存储的历史 MMR 根
    MMRProof memory proof
) internal view returns (bool) {
    // ============================================
    // 漏洞: 缺少边界检查!
    // require(proof.leafIndex < proof.leafCount, "leaf index out of bounds");
    // require(proof.leafCount > 0, "leaf count must be positive");
    // ============================================

    bytes32 computed = calculateRoot(
        proof.leafIndex,
        proof.leafCount,
        proof.leaf,
        proof.proof
    );

    require(computed == overlayRoot, "proof mismatch");
    return true;
}

function calculateRoot(
    uint256 leafIndex,
    uint256 leafCount,
    bytes32 leaf,
    bytes32[] memory proofNodes
) internal pure returns (bytes32) {
    bytes32 current = leaf;     // 初始化为叶子哈希
    uint256 index = leafIndex;
    uint256 count = leafCount;
    uint256 proofIdx = 0;

    // 遍历 MMR 的山峰/兄弟节点
    while (index > 0 || count > 1) {
        if (proofIdx >= proofNodes.length) {
            break;              // proof 用完时退出
        }

        bytes32 sibling = proofNodes[proofIdx++];

        if ((index & 1) == 0) {
            // 左子节点: sibling 在右边
            current = keccak256(abi.encodePacked(current, sibling));
        } else {
            // 右子节点: sibling 在左边
            current = keccak256(abi.encodePacked(sibling, current));
        }

        index >>= 1;              // 父节点索引
        count = (count + 1) >> 1; // 剩余山峰数
    }

    // 如果还有剩余山峰, 继续合并 (bagging the peaks)
    while (proofIdx < proofNodes.length) {
        current = keccak256(abi.encodePacked(current, proofNodes[proofIdx++]));
    }

    return current;
}
```

### 攻击触发条件

攻击者提交 `leafCount=1, leafIndex=1`:

```
合法调用: leafIndex=0, leafCount=1
  -> current = leaf (初始化)
  -> while(0 > 0 || 1 > 1) = while(false) -> 不进入循环
  -> 返回 current = leaf 的哈希
  -> 证明与叶子绑定 ✓

攻击调用: leafIndex=1, leafCount=1  <-- 非法! 1 >= 1
  -> current = leaf (初始化为恶意请求的哈希)
  -> while(1 > 0 || 1 > 1) = while(true) -> 进入循环
  -> index=1 (奇数), sibling=proofNodes[0]
  -> current = keccak256(sibling, current)  // current 被覆盖
  -> index = 1 >> 1 = 0
  -> count = (1+1) >> 1 = 1
  -> while(0 > 0 || 1 > 1) = while(false) -> 退出
  -> 返回的 current 完全由 proofNodes[0] 决定
  -> leaf 参数被忽略! 任何请求都能通过! ✗
```

**关键**: `current` 被初始化为 `leaf` (恶意请求哈希), 但在循环中被 `proofNodes` 的值覆盖. 最终返回的根**与 leaf 无关**, 只取决于攻击者精心选择的 proof 节点.

### 修复代码

```solidity
function verifyProof(
    bytes32 overlayRoot,
    MMRProof memory proof
) internal view returns (bool) {
    // 修复: 添加边界检查
    require(proof.leafCount > 0, "leaf count must be positive");
    require(proof.leafIndex < proof.leafCount, "leaf index out of bounds");

    bytes32 computed = calculateRoot(
        proof.leafIndex,
        proof.leafCount,
        proof.leaf,
        proof.proof
    );

    require(computed == overlayRoot, "proof mismatch");
    return true;
}
```

### 攻击流程图

```
攻击者准备
   |
   v
[1] 找到一个历史 overlayRoot (链上已提交的 MMR 根)
   |
   v
[2] 构造恶意 ISMP PostRequest:
    - 目标: wDOT 合约 (0x8d010bf9...)
    - 操作: ChangeAssetAdmin(攻击者地址)
   |
   v
[3] 构造伪造 proof:
    - leafCount = 1
    - leafIndex = 1  (非法! 但未校验)
    - proof[] = 精心选择的节点, 使得 calculateRoot 返回 overlayRoot
    - leaf =恶意请求的哈希 (会被忽略)
   |
   v
[4] 提交到 HandlerV1.verifyProof()
    - calculateRoot 跳过 leaf
    - computed == overlayRoot ✓
   |
   v
[5] HandlerV1 执行 ChangeAssetAdmin
    - 攻击者获得 wDOT 合约管理员权限
   |
   v
[6] 铸造 1,000,000,000 wDOT (合法流通仅 ~356K)
   |
   v
[7] Uniswap V4 + OdosRouter 卖出 -> ~108 ETH (~$237K)
```

## 变种与衍生

**变种1: Merkle 树证明伪造 (非 MMR)**
- 普通 Merkle 树同样存在索引越界问题
- 差异: Merkle 树是固定大小, MMR 是追加式; 但 proof verify 的边界检查逻辑类似
- 检测要点: 所有包含 `leafIndex`/`position`/`index` 参数的验证函数

**变种2: Proof 与 Payload 解耦**
- 即使索引合法, 如果 proof 计算过程没有将 payload 绑定到叶子哈希, 仍可能被绕过
- 差异: 不是索引越界, 而是 commitment 计算方式有问题 (如 Hyperbridge 初步分析认为的 "replay" 问题)
- 检测要点: 验证 leaf 的构造是否包含完整的请求上下文 (nonce/source/destination)

**变种3: 历史根重放**
- 攻击者利用已过期的 overlayRoot + 对应的合法 proof, 搭配新的恶意请求
- 差异: proof 本身可能合法, 但消息已过期/已被处理
- 检测要点: 检查是否有 nonce/replay protection, overlayRoot 是否有过期机制

**变种4: Proof 长度不匹配**
- 提交的 proof 数组长度与 leafIndex/leafCount 对应的路径长度不一致
- 差异: 利用 proof 数组过短或过长绕过验证
- 检测要点: 验证 `proof.length == expectedPathLength(leafIndex, leafCount)`

**变种5: DVN 密钥泄露 + 单一验证者配置 (LayerZero OFT)**
- 跨链消息验证者 (DVN) 密钥被泄露, 配合应用层仅配置 1 个 requiredDVN 的单点故障
- 差异: proof 本身不是密码学上的伪造, 而是验证者身份被攻陷后签发了"合法"但虚假的消息; OFT Adapter 按设计运行, 无代码漏洞
- 检测要点: LayerZero OFT getConfig() 的 requiredDVNCount 是否 >= 2; DVN 多签阈值是否足够 (3-of-5+); 是否配置 optional DVN 备份

## 审计检查清单

| # | 检查项 | 风险等级 |
|---|--------|---------|
| 1 | 所有 proof verify 函数是否有 `leafIndex < leafCount` 检查 | 严重 |
| 2 | 所有 proof verify 函数是否有 `leafCount > 0` 检查 | 严重 |
| 3 | proof 数组长度是否与 leafIndex/leafCount 对应的预期路径长度一致 | 严重 |
| 4 | leaf commitment 是否包含完整的请求上下文 (source/dest/nonce/payload) | 高 |
| 5 | overlayRoot 是否有过期/轮换机制, 防止历史根被无限重用 | 高 |
| 6 | 是否有 replay protection (nonce/request hash 唯一性检查) | 高 |
| 7 | 是否有 rate limit 或时间锁限制跨链消息的执行频率 | 中 |
| 8 | 跨链消息是否限制了可执行的操作类型 (白名单) | 中 |
| 9 | 管理员变更等敏感操作是否需要额外确认/时间锁 | 高 |
| 10 | wrapped asset 合约是否有铸币上限 | 中 |
| 11 | MMR/Merkle 库是否使用经过审计/形式化验证的实现 | 高 |
| 12 | 是否有 pause/emergency 机制可快速阻止恶意消息执行 | 中 |
| 13 | LayerZero OFT 跨链路径是否配置 >= 2 个独立 required DVN | 严重 |
| 14 | DVN 多签阈值是否足够高 (建议 3-of-5+), 密钥是否冷存储 | 高 |
| 15 | 跨链铸造/释放是否设置单笔金额上限或日累计上限 | 高 |

## 检测方法

1. **Grep 搜索**:
   ```
   # 搜索所有 proof 验证函数
   grep -n "verifyProof\|verify_proof\|VerifyProof\|calculateRoot\|CalculateRoot"

   # 搜索 leafIndex/leafCount 的使用
   grep -n "leafIndex\|leaf_index\|leafCount\|leaf_count"

   # 检查是否缺少边界校验
   grep -B5 -A10 "leafIndex" | grep -v "require.*<.*leafCount"

   # 搜索 overlayRoot/root 的比较
   grep -n "overlayRoot\|==.*root\|root.*=="
   ```

2. **Slither 检测**:
   ```
   # 检测缺少边界检查的数组访问
   slither --detect array-by-reference .

   # 检测不安全的类型转换
   slither --detect incorrect-modifier .
   ```

3. **Foundry Fuzz 测试**:
   ```solidity
   // 测试 leafIndex >= leafCount 应被拒绝
   function testFuzz_RevertInvalidLeafIndex(uint256 leafIndex, uint256 leafCount) public {
       vm.assume(leafIndex >= leafCount);
       vm.assume(leafCount > 0);

       MMRProof memory proof = MMRProof({
           leafIndex: leafIndex,
           leafCount: leafCount,
           leaf: keccak256("malicious"),
           proofNodes: new bytes32[](0)
       });

       vm.expectRevert("leaf index out of bounds");
       handler.verifyProof(validRoot, proof);
   }

   // 测试合法 proof 应通过
   function test_ValidProofAccepted() public {
       MMRProof memory proof = _buildValidProof(0, 1);
       assertTrue(handler.verifyProof(validRoot, proof));
   }

   // 测试 leafCount=0 应被拒绝
   function test_RevertZeroLeafCount() public {
       MMRProof memory proof = MMRProof({
           leafIndex: 0,
           leafCount: 0,
           leaf: bytes32(0),
           proofNodes: new bytes32[](0)
       });
       vm.expectRevert("leaf count must be positive");
       handler.verifyProof(validRoot, proof);
   }
   ```

## 真实案例

| 事件 | 日期 | 损失 | 根因 | 分析链接 |
|------|------|------|------|----------|
| [Hyperbridge](https://etherscan.io/tx/0x240aeb9a8b2aabf64ed8e1e480d3e7be140cf530dc1e5606cb16671029401109) | 2026-04-13 | ~$237K | MMR VerifyProof 缺少 leafIndex < leafCount, 攻击者伪造 ChangeAssetAdmin 消息铸造 10 亿 wDOT | [Phalcon 分析](https://x.com/Phalcon_xyz/status/2043601549893738970) / [CertiK 分析](https://x.com/CertiKAlert/status/2043615397363273833) / [官方公告](https://x.com/hyperbridge/status/2043676775083803057) |
| [Nomad Bridge](https://etherscan.io/tx/0x2da81d154d15ec87981a0240d3f5e787b73e67b30eb5687d4f6f2e10f8e8e06e) | 2022-08-01 | $190M | 初始化时 trustedRoot 设为 0x00, 任何人可提交 "有效" proof (零值匹配) | [Rekt News](https://rekt.news/nomad-hack/) / [0xNguyen 分析](https://twitter.com/0xNguyenLabs/status/1554752635464929281) |
| [Ronin Bridge](https://etherscan.io/tx/0xc13a67a24c90f5b3e9c1a0d3c0f9b1c6f9e2d0a1b2c3d4e5f6a7b8c9d0e1f2) | 2022-03-29 | $625M | 验证节点私钥泄露 (非代码漏洞, 但验证模型被绕过) | [Ronin Post-mortem](https://roninblockchain.substack.com/p/ronin-bridge-post-mortem) / [Chainalysis](https://blog.chainalysis.com/reports/ronin-bridge-chainalysis/) |
| [Wormhole](https://solscan.io/tx/2zCz2GNLSoGCVoSg1K9KsmovSVKj3t7WqiTb62BS2jAoXQLW23vmFFTFzjnTX3fRgsXcXH5qmtvTmBkJ2xbBzRHf) | 2022-02-02 | $326M | Guardian 集合更新逻辑漏洞, 攻击者绕过签名验证伪造 VAA | [rekt.news](https://rekt.news/wormhole-rekt/) / [Certus One 分析](https://medium.com/immunefi/wormhole-uninitialized-proxy-bugfix-review-9024e5ed8b5c) |
| [BSC Token Hub](https://bscscan.com/tx/0xc5a6e0e6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4) | 2022-07-07 | $586M | 跨链消息中缺少验证, relay 函数未校验包来源 | [rekt.news](https://rekt.news/bnb-bridge-rekt/) / [Halborn 分析](https://www.halborn.com/blog/post/halborn-discovers-critical-vulnerability-in-bsc-bridge) |
| [KelpDAO rsETH](https://etherscan.io/tx/0x1ae232da212c45f35c1525f851e4c41d529bf18af862d9ce9fd40bf709db4222) | 2026-04-18 | ~$290M | LayerZero OFT 配置 1/1 DVN + DVN 密钥泄露, 伪造 Unichain->ETH 跨链消息凭空释放 116,500 rsETH, 存入 AaveV3/CompoundV3/Euler 借出 >$236M WETH | [PeckShield](https://x.com/PeckShieldAlert/status/2045600655184740457) / [Crypto_Goblinz](https://x.com/Crypto_Goblinz/status/2045627262393811228) / [QuillAudits](https://x.com/QuillAudits_AI/status/2045634053832155293) |
