---
name: ai-vuln-discovery
description: Use when 进行安全审计, 漏洞发现, 或漏洞验证. 触发场景: (1) 智能合约审计 (Solidity, Foundry, Slither), (2) 前后端框架审计 (React, Next.js, Laravel, FastAPI, Express, ThinkPHP), (3) 漏洞验证与PoC开发, (4) 业务逻辑漏洞检测, (5) 框架版本CVE搜索.
---

# AI驱动漏洞发现分析

全栈安全审计: 智能合约 + 前后端应用.

## 适用角色

- 智能合约开发者
- 前后端安全审计人员
- DeFi协议安全研究员

## 何时使用

- 智能合约安全审计 (Solidity)
- 前后端框架安全审计
- 漏洞验证与PoC开发
- 业务逻辑漏洞检测
- 框架版本CVE/漏洞搜索

## 核心原则

| 原则 | 说明 |
|------|------|
| **PoC || GTFO** | 无法利用则不报告,零误报承诺 |
| **框架知识优先** | 不了解框架就无法发现框架层面的漏洞 |
| **版本是关键** | 同样的代码在不同版本可能有完全不同的安全风险 |
| **静态分析先行** | 智能合约必须先用 Slither 扫描 |
| **网络搜索辅助** | 框架漏洞可通过网络搜索发现最新CVE |

## 验证环境选择

| 技术栈 | 推荐环境/工具 | 用途 |
|--------|---------------|------|
| **Solidity智能合约** | Slither + Foundry (forge/cast/anvil) | 静态分析 + 测试/交互/本地节点 |
| **React/Next.js** | Docker + 网络搜索CVE | 运行环境 + 框架漏洞查询 |
| **Web应用 (PHP/Python/Node)** | Docker容器 | 隔离运行环境 |
| **Java应用** | Maven/Gradle + TestContainers | 依赖管理,集成测试 |

## 框架漏洞网络搜索

对于 React, Next.js, Laravel 等框架,审计时必须:

1. **确认精确版本**: 查看 package.json / composer.json
2. **搜索框架CVE**: 使用网络搜索 `"{框架名} {版本} vulnerability CVE"`
3. **检查依赖漏洞**: `npm audit` / `yarn audit` / `composer audit`

**搜索示例**:
```
"Next.js 14 vulnerability"
"React 18 XSS CVE"
"Laravel 10 security advisory"
```

## 团队模式

审计大型项目(>10万行代码)时启动团队模式:

| 角色 | 职责 | 输出 |
|------|------|------|
| **研究员** | 框架学习,CVE搜索,历史漏洞调研 | 安全报告,CVE清单 |
| **审计员** | 代码审查,漏洞识别 | 疑似漏洞列表 |
| **验证员** | PoC开发,漏洞验证 | 可复现PoC |
| **报告员** | 报告编写,修复建议 | 审计报告 |

## 参考文件

| 文件 | 用途 |
|------|------|
| [references/smart-contract-audit.md](references/smart-contract-audit.md) | 智能合约审计 (Slither, Foundry, 重入攻击, DeFi漏洞) |
| [references/framework-audit.md](references/framework-audit.md) | 框架审计方法论 (准备阶段, 网络搜索CVE, 业务逻辑审计) |
| [references/vuln-taxonomy.md](references/vuln-taxonomy.md) | 漏洞分类体系 (前后端交互, 认证授权, 数据层) |
| [references/verification-guide.md](references/verification-guide.md) | 漏洞验证方法论 (验证原则, 环境选择, 验证流程) |
| [references/poc-template.md](references/poc-template.md) | PoC编写规范 (核心要素, 设计原则, 模板) |

## 案例分析模板

```markdown
## 案例: [CVE编号] - [漏洞名称]

### 基本信息
- **发现平台**:
- **影响组件**:
- **漏洞类型**:

### 技术细节
- **根本原因**:
- **攻击向量**:
- **利用条件**:

### AI发现方法
- **威胁建模**: AI如何生成攻击假设
- **代码分析**: 哪些代码路径被追踪
- **验证过程**: 如何确认漏洞可利用

### 修复建议
- 官方修复方案
- 预防此类漏洞的最佳实践
```

## 注意事项

- AI发现漏洞强调"理解意图"而非"匹配模式"
- 零误报是通过强制PoC验证实现的,非静态分析
- 框架本身可能存在漏洞,必须通过网络搜索验证
- 智能合约审计必须先用 Slither 静态分析
