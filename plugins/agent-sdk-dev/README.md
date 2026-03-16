# Agent SDK 开发插件

用于创建和验证 Python 和 TypeScript Claude Agent SDK 应用的综合插件.

## 概述

Agent SDK 开发插件简化了构建 Agent SDK 应用的整个生命周期,从初始脚手架到最佳实践验证. 它帮助你快速启动新项目并使用最新 SDK 版本,确保应用遵循官方文档模式.

## 功能

### 命令: `/new-sdk-app`

交互式命令,引导你创建新的 Claude Agent SDK 应用.

**功能:**
- 询问项目相关问题 (语言, 名称, Agent 类型, 起点模板)
- 检查并安装最新 SDK 版本
- 创建所有必要的项目文件和配置
- 设置环境文件 (.env.example, .gitignore)
- 提供针对你用例的工作示例
- 运行类型检查 (TypeScript) 或语法验证 (Python)
- 使用适当的验证 Agent 自动验证设置

**用法:**
```bash
/new-sdk-app my-project-name
```

或直接:
```bash
/new-sdk-app
```

命令将交互式询问:
1. 语言选择 (TypeScript 或 Python)
2. 项目名称 (如果未提供)
3. Agent 类型 (coding, business, custom)
4. 起点模板 (minimal, basic, 或特定示例)
5. 工具偏好 (npm/yarn/pnpm 或 pip/poetry)

**示例:**
```bash
/new-sdk-app customer-support-agent
# -> 创建客服 Agent 的新 Agent SDK 项目
# -> 设置 TypeScript 或 Python 环境
# -> 安装最新 SDK 版本
# -> 自动验证设置
```

### Agent: `agent-sdk-verifier-py`

彻底验证 Python Agent SDK 应用的正确配置和最佳实践.

**验证检查项:**
- SDK 安装和版本
- Python 环境设置 (requirements.txt, pyproject.toml)
- 正确的 SDK 用法和模式
- Agent 初始化和配置
- 环境和安全 (.env, API 密钥)
- 错误处理和功能
- 文档完整性

**使用场景:**
- 创建新 Python SDK 项目后
- 修改现有 Python SDK 应用后
- 部署 Python SDK 应用前

**用法:**
该 Agent 在 `/new-sdk-app` 创建 Python 项目后自动运行,或通过以下方式触发:
```
"验证我的 Python Agent SDK 应用"
"检查我的 SDK 应用是否遵循最佳实践"
```

**输出:**
提供包含以下内容的综合报告:
- 整体状态 (PASS / PASS WITH WARNINGS / FAIL)
- 阻碍功能的关键问题
- 次优模式警告
- 通过的检查项列表
- 带 SDK 文档参考的具体建议

### Agent: `agent-sdk-verifier-ts`

彻底验证 TypeScript Agent SDK 应用的正确配置和最佳实践.

**验证检查项:**
- SDK 安装和版本
- TypeScript 配置 (tsconfig.json)
- 正确的 SDK 用法和模式
- 类型安全和导入
- Agent 初始化和配置
- 环境和安全 (.env, API 密钥)
- 错误处理和功能
- 文档完整性

**使用场景:**
- 创建新 TypeScript SDK 项目后
- 修改现有 TypeScript SDK 应用后
- 部署 TypeScript SDK 应用前

**用法:**
该 Agent 在 `/new-sdk-app` 创建 TypeScript 项目后自动运行,或通过以下方式触发:
```
"验证我的 TypeScript Agent SDK 应用"
"检查我的 SDK 应用是否遵循最佳实践"
```

**输出:**
提供包含以下内容的综合报告:
- 整体状态 (PASS / PASS WITH WARNINGS / FAIL)
- 阻碍功能的关键问题
- 次优模式警告
- 通过的检查项列表
- 带 SDK 文档参考的具体建议

## 工作流示例

使用此插件的典型工作流:

1. **创建新项目:**
```bash
/new-sdk-app code-reviewer-agent
```

2. **回答交互式问题:**
```
语言: TypeScript
Agent 类型: 编码 Agent (代码审查)
起点模板: 带常用功能的基础 Agent
```

3. **自动验证:**
命令自动运行 `agent-sdk-verifier-ts` 确保一切正确设置.

4. **开始开发:**
```bash
# 设置 API 密钥
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# 运行 Agent
npm start
```

5. **修改后验证:**
```
"验证我的 SDK 应用"
```

## 安装

此插件包含在 Claude Code 仓库中. 使用方法:

1. 确保已安装 Claude Code
2. 插件命令和 Agent 自动可用

## 最佳实践

- **始终使用最新 SDK 版本**: `/new-sdk-app` 检查并安装最新版本
- **部署前验证**: 部署到生产环境前运行验证 Agent
- **保护 API 密钥安全**: 永远不要提交 `.env` 文件或硬编码 API 密钥
- **遵循 SDK 文档**: 验证 Agent 检查是否符合官方模式
- **类型检查 TypeScript 项目**: 定期运行 `npx tsc --noEmit`
- **测试你的 Agent**: 为 Agent 功能创建测试用例

## 资源

- [Agent SDK 概述](https://docs.claude.com/en/api/agent-sdk/overview)
- [TypeScript SDK 参考](https://docs.claude.com/en/api/agent-sdk/typescript)
- [Python SDK 参考](https://docs.claude.com/en/api/agent-sdk/python)
- [Agent SDK 示例](https://docs.claude.com/en/api/agent-sdk/examples)

## 故障排除

### TypeScript 项目类型错误

**问题**: 创建后 TypeScript 项目有类型错误

**解决方案**:
- `/new-sdk-app` 命令自动运行类型检查
- 如果错误持续,检查是否使用最新 SDK 版本
- 验证 `tsconfig.json` 符合 SDK 要求

### Python 导入错误

**问题**: 无法从 `claude_agent_sdk` 导入

**解决方案**:
- 确保已安装依赖: `pip install -r requirements.txt`
- 如果使用虚拟环境,请激活它
- 检查 SDK 是否已安装: `pip show claude-agent-sdk`

### 验证失败但有警告

**问题**: 验证 Agent 报告警告

**解决方案**:
- 查看报告中的具体警告
- 检查提供的 SDK 文档参考
- 警告不会阻碍功能,但指示可改进的地方

## 作者

Ashwin Bhat (ashwin@anthropic.com)

## 版本

1.0.0
