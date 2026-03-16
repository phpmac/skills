---
description: 创建和设置新的 Claude Agent SDK 应用
argument-hint: [project-name]
---

你的任务是帮助用户创建新的 Claude Agent SDK 应用. 请仔细按照以下步骤操作:

## 参考文档

开始前, 查阅官方文档以确保提供准确和最新的指导. 使用 WebFetch 阅读这些页面:

1. **从概述开始**: https://docs.claude.com/en/api/agent-sdk/overview
2. **根据用户语言选择, 阅读相应的 SDK 参考**:
   - TypeScript: https://docs.claude.com/en/api/agent-sdk/typescript
   - Python: https://docs.claude.com/en/api/agent-sdk/python
3. **阅读概述中提到的相关指南** 如:
   - 流式 vs 单次模式
   - 权限
   - 自定义工具
   - MCP 集成
   - 子 Agent
   - 会话
   - 基于用户需求的其他相关指南

**重要**: 始终检查并使用最新版本的包. 安装前使用 WebSearch 或 WebFetch 验证当前版本.

## 收集需求

重要: 一次只问一个问题. 等待用户回答后再问下一个问题. 这样用户更容易回答.

按此顺序提问 (跳过用户已通过参数提供的问题):

1. **语言** (首先问): "你想使用 TypeScript 还是 Python?"

   - 等待回答后再继续

2. **项目名称** (第二个问): "你想给项目起什么名字?"

   - 如果提供了 $ARGUMENTS, 使用它作为项目名称并跳过此问题
   - 等待回答后再继续

3. **Agent 类型** (第三个问, 但如果 #2 足够详细则跳过): "你正在构建什么类型的 Agent? 一些示例:

   - 编码 Agent (SRE, 安全审查, 代码审查)
   - 业务 Agent (客服支持, 内容创作)
   - 自定义 Agent (描述你的用例)"
   - 等待回答后再继续

4. **起点模板** (第四个问): "你想要:

   - 一个最小的 'Hello World' 示例开始
   - 一个带常用功能的基础 Agent
   - 基于你用例的特定示例"
   - 等待回答后再继续

5. **工具选择** (第五个问): 告知用户你将使用什么工具, 并与用户确认这些是他们想要使用的工具 (例如, 他们可能更喜欢 pnpm 或 bun 而不是 npm). 执行需求时尊重用户的偏好.

所有问题回答后, 继续创建设置计划.

## 设置计划

根据用户的回答, 创建包含以下内容的计划:

1. **项目初始化**:

   - 创建项目目录 (如不存在)
   - 初始化包管理器:
     - TypeScript: `npm init -y` 并设置 `package.json` 的 type: "module" 和 scripts (包含 "typecheck" 脚本)
     - Python: 创建 `requirements.txt` 或使用 `poetry init`
   - 添加必要的配置文件:
     - TypeScript: 创建 `tsconfig.json` 并设置适合 SDK 的配置
     - Python: 可选创建配置文件 (如需要)

2. **检查最新版本**:

   - 安装前, 使用 WebSearch 或检查 npm/PyPI 查找最新版本
   - TypeScript: 检查 https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk
   - Python: 检查 https://pypi.org/project/claude-agent-sdk/
   - 告知用户你要安装的版本

3. **SDK 安装**:

   - TypeScript: `npm install @anthropic-ai/claude-agent-sdk@latest` (或指定最新版本)
   - Python: `pip install claude-agent-sdk` (pip 默认安装最新版)
   - 安装后, 验证安装的版本:
     - TypeScript: 检查 package.json 或运行 `npm list @anthropic-ai/claude-agent-sdk`
     - Python: 运行 `pip show claude-agent-sdk`

4. **创建启动文件**:

   - TypeScript: 创建 `index.ts` 或 `src/index.ts` 包含基本查询示例
   - Python: 创建 `main.py` 包含基本查询示例
   - 包含正确的导入和基本错误处理
   - 使用最新 SDK 版本的现代语法和模式

5. **环境设置**:

   - 创建 `.env.example` 文件, 包含 `ANTHROPIC_API_KEY=your_api_key_here`
   - 将 `.env` 添加到 `.gitignore`
   - 解释如何从 https://console.anthropic.com/ 获取 API 密钥

6. **可选: 创建 .claude 目录结构**:
   - 提议创建 `.claude/` 目录用于 Agent, 命令和设置
   - 询问是否需要示例子 Agent 或斜杠命令

## 实现

收集需求并获得用户对计划的确认后:

1. 使用 WebSearch 或 WebFetch 检查最新包版本
2. 执行设置步骤
3. 创建所有必要的文件
4. 安装依赖 (始终使用最新稳定版本)
5. 验证安装的版本并告知用户
6. 根据其 Agent 类型创建工作示例
7. 在代码中添加有帮助的注释解释每部分的作用
8. **完成前验证代码可工作**:
   - TypeScript:
     - 运行 `npx tsc --noEmit` 检查类型错误
     - 修复所有类型错误直到类型检查完全通过
     - 确保导入和类型正确
     - 仅在类型检查无错误通过时继续
   - Python:
     - 验证导入正确
     - 检查基本语法错误
   - **代码验证成功前不要认为设置完成**

## 验证

所有文件创建完成且依赖安装后, 使用适当的验证 Agent 验证 Agent SDK 应用配置正确且可使用:

1. **TypeScript 项目**: 启动 **agent-sdk-verifier-ts** Agent 验证设置
2. **Python 项目**: 启动 **agent-sdk-verifier-py** Agent 验证设置
3. Agent 将检查 SDK 使用, 配置, 功能和对官方文档的遵循
4. 审查验证报告并解决任何问题

## 入门指南

设置完成并验证后, 为用户提供:

1. **后续步骤**:

   - 如何设置 API 密钥
   - 如何运行 Agent:
     - TypeScript: `npm start` 或 `node --loader ts-node/esm index.ts`
     - Python: `python main.py`

2. **有用资源**:

   - TypeScript SDK 参考链接: https://docs.claude.com/en/api/agent-sdk/typescript
   - Python SDK 参考链接: https://docs.claude.com/en/api/agent-sdk/python
   - 解释关键概念: 系统提示, 权限, 工具, MCP 服务器

3. **常见后续步骤**:
   - 如何自定义系统提示
   - 如何通过 MCP 添加自定义工具
   - 如何配置权限
   - 如何创建子 Agent

## 重要说明

- **始终使用最新版本**: 安装任何包前, 使用 WebSearch 或直接检查 npm/PyPI 获取最新版本
- **验证代码正确运行**:
  - TypeScript: 运行 `npx tsc --noEmit` 并在完成前修复所有类型错误
  - Python: 验证语法和导入正确
  - 代码通过验证前不要认为任务完成
- 安装后验证安装的版本并告知用户
- 检查官方文档了解任何版本特定要求 (Node.js 版本, Python 版本等)
- 创建前始终检查目录/文件是否已存在
- 使用用户偏好的包管理器 (TypeScript 用 npm, yarn, pnpm; Python 用 pip, poetry)
- 确保所有代码示例功能正常并包含适当的错误处理
- 使用与最新 SDK 版本兼容的现代语法和模式
- 使体验具有交互性和教育性
- **一次只问一个问题** - 不要在单个响应中问多个问题

从仅询问第一个需求问题开始. 等待用户回答后再继续下一个问题.
