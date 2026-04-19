# contract-security

智能合约安全审计插件, 提供从漏洞扫描到审计报告的完整链路.

## Agents

| Agent | 说明 |
|-------|------|
| contract-scanner | Slither/Mythril/Echidna/Medusa 静态分析与模糊测试 |
| smart-contract-vuln | DeFi 漏洞分类/攻击模式/真实案例 PoC |
| vuln-discovery-orchestrator | 安全审计编排, 自动委派专业 Agent |
| vuln-taxonomy-researcher | 漏洞分类体系/CWE 映射/历史攻击案例 |

## Skills

| Skill | 说明 |
|-------|------|
| contract-audit | 合约审计入口, 引导选择 Agent 并生成审计方案 |
| cron-security-audit | 定时安全审计, 支持 Discord 报告 |
| forge-foundry-test | Foundry 单元测试 + Fork 主网测试 |
| hardhat-v2-fork-testing | Hardhat v2 Fork 主网测试 |
| hardhat-v3-fork-testing | Hardhat v3 Fork 主网测试 |
| create2-vanity-deploy | CREATE2 靓号地址部署 |

## 依赖

- foundry/forge/cast (合约测试与链上交互)
- slither (可选, 静态分析)
