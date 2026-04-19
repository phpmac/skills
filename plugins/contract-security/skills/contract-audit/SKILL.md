---
name: contract-audit
description: 当用户要求 "审计智能合约", "合约安全审计", "安全检查" 时应使用此技能. 引导用户选择审计 Agent, 生成含边界审计的审计方案, 然后执行审计
metadata: {"clawdbot":{"emoji":"shield","os":["darwin","linux"],"requires":{"bins":["forge","solc"]},"install":[{"id":"solc","kind":"brew","formula":"solidity","bins":["solc"],"label":"安装 solc (Slither/Mythril 基础依赖)"},{"id":"slither","kind":"bash","raw":"uv tool install slither-analyzer","bins":["slither"],"label":"安装 Slither 静态分析"},{"id":"halmos","kind":"bash","raw":"uv tool install --python 3.12 halmos","bins":["halmos"],"label":"安装 Halmos 符号测试"},{"id":"echidna","kind":"brew","formula":"echidna","bins":["echidna"],"label":"安装 Echidna 模糊测试"},{"id":"medusa","kind":"brew","formula":"medusa","bins":["medusa"],"label":"安装 Medusa 模糊测试"},{"id":"mythril","kind":"bash","raw":"uv python install 3.12 && uv venv --python 3.12 --clear .venv && uv pip install --python .venv/bin/python mythril 'setuptools<67'","bins":["myth"],"label":"安装 Mythril 符号执行 (Python 3.12 venv)"},{"id":"forge","kind":"bash","raw":"curl -L https://foundry.paradigm.xyz | bash && foundryup","bins":["forge"],"label":"安装 Foundry (forge/cast)"}]}}
---

# 合约审计

你正在帮助用户对智能合约进行安全审计. 遵循以下四阶段流程.

## 核心原则

- **工具预检**: 执行前必须检测 agent 需要的工具是否已安装且配置正确, 否则禁止执行后续操作, 安装方法在 agent 里面有说明,没有的话根据当前系统环境结合mcp工具查阅安装方法
- **边界全覆盖**: 审计目标不能只看单个合约, 必须递归分析所有交互合约 (如 Pair, Router, Factory, Proxy 等)
- **深度代码阅读**: 发现问题时必须仔细阅读该方法的完整内部实现及所有关联调用链, 禁止仅凭函数签名或表面逻辑下结论
- **先规划后执行**: 必须先输出审计方案并获得用户确认, 才能启动 agent 执行
- **使用 TaskCreate**: 全程跟踪审计进度

---

## 阶段 0: 工具预检

**目标**: 确保本次审计所需的所有工具已安装, 有任何一个缺失则立即停止

**行动**:

1. 读取用户选择的 agent 文件, 提取其依赖的工具列表
2. 逐个执行 `which <tool>` + `<tool> --version` 检测是否已安装
3. 输出检测结果表格:

```
| 工具 | 状态 | 版本 |
|------|------|------|
| forge | 已安装 | v1.5.1 |
| mythril | **未安装** | - |
```

4. **有任何一个未安装 -> 立即停止全部后续操作**, 输出:
   - 缺失工具名称
   - 对应的安装命令 (从 agent 的 metadata.install 或网络查询获取)
   - 等待用户安装完成确认后再继续
5. **禁止**: 在工具缺失时继续执行任何后续阶段 (读合约/生成方案/启动 agent 均禁止)

---

## 阶段 1: Agent 选择

**目标**: 让用户选择本次审计使用的 agent

**行动**:

1. 读取 `${CLAUDE_PLUGIN_ROOT}/agents/` 目录, 列出所有安全相关 agent:

| Agent | 触发关键词 | 职责 |
|-------|-----------|------|
| **contract-scanner** | Slither, Mythril, 工具扫描 | 静态分析/符号执行/fuzzing |
| **smart-contract-vuln** | DeFi 漏洞, 攻击模式 | 漏洞知识库 + 代码逐项审计 |
| **vuln-discovery-orchestrator** | 综合审计, 全面审计 | 协调多个 agent 分配任务并汇总 |
| **vuln-taxonomy-researcher** | 漏洞分类, 检查清单 | 生成针对性检查清单 |
| **poc-verifier** | PoC, 漏洞验证 | 将疑似漏洞转化为可复现 PoC |
| **framework-auditor** | Web 框架, CVE | 前后端框架安全 (非合约) |

2. 使用 AskUserQuestion 让用户选择要使用的 agent (multiSelect), 默认推荐 `vuln-discovery-orchestrator` (综合审计)
3. 如果用户选择单个 agent, 直接使用; 选择 orchestrator 则由它自动委派

---

## 阶段 2: 审计方案

**目标**: 生成详细审计方案, 包含边界分析, 获得用户确认

**行动**:

### 2.1 项目扫描

1. 确定审计目标路径 (用户指定或当前目录)
2. 扫描所有 Solidity 文件, 识别:
   - 主合约列表 (名称, 类型, 文件路径)
   - 继承关系 (is, inherits)
   - 外部依赖 (import, interface)
   - 已部署合约地址 (如果用户提供)
3. 递归追踪合约交互链, 例如:
   - Token -> Pair (sync/skim 边界)
   - Router -> Pair (流动性操作边界)
   - Factory -> Pair (创建逻辑边界)
   - Proxy -> Implementation (代理模式边界)
   - MasterChef -> RewardToken (奖励分发边界)
   - LendingPool -> InterestRate (利率模型边界)

### 2.2 生成审计方案

输出格式参考 `references/audit-plan-template.md`, 包含审计范围/审计维度(常规漏洞+边界+业务逻辑)/执行计划.

3. 使用 AskUserQuestion 让用户确认方案, 或提出修改意见
4. 用户确认后进入阶段 3

---

## 阶段 3: 执行审计

**目标**: 调用选定的 agent 执行审计方案

**行动**:

1. 根据用户选择的 agent, 构造 agent 提示:
   - 包含完整的审计方案内容
   - 指明审计目标路径和合约范围
   - 包含边界审计的具体检查项
   - **强调深度阅读**: agent 必须完整阅读每个可疑函数的内部实现代码, 包括其调用的所有内部方法和外部合约方法, 追踪完整的数据流和状态变更, 禁止仅看函数签名或注释就下结论
   - **强调流程审计**: agent 必须先梳理每个业务功能的完整流程链路(管道式), 再分析不同流程间的交叉影响(交叉式), 禁止跳过流程理解直接逐函数审计
   - **搜索工具策略**: 告知 agent 漏洞案例搜索使用 x-search, GitHub 仓库爬取使用 firecrawl
   - 要求 agent 返回结构化的审计报告

2. 对于 `vuln-discovery-orchestrator`:
   - 直接传入完整审计方案, 让它自动分配子任务
   - 等待完成后汇总所有子 agent 结果

3. 对于单个 agent:
   - 传入审计方案中的对应维度
   - 如果需要多个维度, 可并行启动多个 agent 实例

4. 汇总所有 agent 结果, 按 `references/audit-report-template.md` 格式输出最终审计报告

5. 标记所有 TaskCreate 完成

---

## 注意事项

- 审计报告中的影响评级必须基于实际可攻击性, 禁止理论推断
- 如果 agent 报告工具未安装, 立即停止并报告给用户 (阶段 0 已前置检查, 此条为兜底)
- 边界审计中如果发现新的关联合约, 需要追加到审计范围并告知用户
- 所有回复和注释使用中文, 标点符号使用英文标点
