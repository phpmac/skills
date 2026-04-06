---
name: unit-test
description: 当用户要求 "编写单元测试", "补充测试", "写个测试" 时应使用此技能. 自动检测框架, 合约项目选择对应 agent, 非合约项目查阅官方规范后编写测试
---

# 单元测试编写

帮助用户为代码编写单元测试. 遵循以下流程.

## 核心规则

- **先检测后执行**: 必须先识别项目框架和版本, 再决定执行路径
- **合约项目走 agent**: 使用专用测试 agent, 交互选择
- **非合约项目必须先查规范**: 禁止凭记忆编写, 必须先用 Context7 查阅对应版本的官方测试 API
- **Hardhat 必须区分版本**: v2 和 v3 测试 API 完全不同, 确认版本后再选 agent
- **JS/TS 默认 Bun**: 测试工具默认使用 `bun test`, 仅当项目明确使用其他工具时才切换
- **Python 默认 pytest**: 配合 uv 管理时用 `uv run pytest` 执行

---

## 阶段 1: 框架检测

扫描项目文件, 识别测试框架:

| 检测文件 | 语言 | 默认测试工具 |
|---------|------|-------------|
| `foundry.toml` | Solidity | Foundry |
| `hardhat.config.*` | Solidity | Hardhat (需确认版本) |
| `bun.lockb` / `bunfig.toml` / `package.json` | JS/TS | Bun |
| `pyproject.toml` / `uv.lock` | Python | pytest |
| `go.mod` | Go | go test |
| `composer.json` / `phpunit.xml` | PHP | PHPUnit / Pest |

多框架或未识别时, 使用 AskUserQuestion 让用户指定.

---

## 阶段 2A: 合约项目 -> Agent 选择

1. 读取 `${CLAUDE_PLUGIN_ROOT}/agents/` 目录, 列出所有测试相关 agent
2. Foundry 项目: 展示匹配的 agent, 使用 AskUserQuestion 让用户选择 (multiSelect)
3. Hardhat 项目:
   - 读取 `package.json` 确认 Hardhat 版本 (v2 / v3)
   - 仅展示对应版本的 agent
   - 如果版本无法确定, 使用 AskUserQuestion 让用户确认

---

## 阶段 2B: 非合约项目 -> 查阅官方规范

1. 使用 Context7 查阅框架的测试规范:
   - `resolve-library-id` 获取库 ID
   - `query-docs` 查询测试 API 和最佳实践
2. 如果 Context7 无法覆盖, 使用 WebSearch 搜索官方文档
3. 展示查阅到的关键 API, 使用 AskUserQuestion 确认测试策略
4. 根据规范编写测试文件

---

## 阶段 3: 执行与验证

1. 展示生成的测试文件内容
2. 使用 AskUserQuestion 确认是否符合预期
3. 询问是否运行测试, 确认后执行

---

## 注意事项

- 如果工具未安装, 立即停止并报告给用户
