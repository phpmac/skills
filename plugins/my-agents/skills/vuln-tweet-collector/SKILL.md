---
name: vuln-tweet-collector
description: 当用户发送X/Twitter漏洞推文链接, 需要研究漏洞, 收集整理到安全知识库时应使用此技能
metadata: {"clawdbot":{"emoji":"fire","os":["darwin","linux"],"requires":{"bins":["cast"]},"install":[{"id":"forge","kind":"bash","raw":"curl -L https://foundry.paradigm.xyz | bash && foundryup","bins":["forge","cast"],"label":"安装 Foundry (forge/cast)"}]}}
---

# 漏洞推文收集器

用户发送漏洞推文链接时, 自动研究漏洞并整理到安全知识库.

## 核心原则

- **只研究不猜测**: 所有漏洞数据必须来自实际链上调用或推文分析, 禁止编造
- **分类优先**: 先确定漏洞类型再整理, 错误分类比缺失更糟
- **增量更新**: 已有同类漏洞资源文件则追加案例, 无则新建
- **工具预检**: 执行前必须检查 cast 等工具是否已安装, 缺失则停止
- **全中文**: 所有输出和注释使用中文, 标点符号使用英文标点

---

## 步骤 1: 工具预检

| 工具 | 用途 | 检测命令 |
|------|------|----------|
| cast | 链上交易分析 | `which cast` |
| x-search | 推特漏洞研究 | MCP工具 |

- 任何工具缺失 -> 立即停止, 报告用户安装后再继续
- 禁止在工具缺失时继续执行后续步骤

---

## 步骤 2: 读取推文

使用 x-read-tweet 工具读取推文内容, 提取:
- 漏洞描述
- 攻击者地址
- 攻击TX hash
- 目标合约地址
- 损失金额
- 攻击链/流程

如果推文信息不足, 使用 x-search 搜索相关分析推文补充.

---

## 步骤 3: 链上验证

对推文中提到的攻击TX, 使用 cast 获取详细信息:

```bash
# 获取交易详情
cast tx <txHash> --rpc-url https://bsc-dataseed.binance.org

# 获取交易回执(状态/日志)
cast receipt <txHash> --rpc-url https://bsc-dataseed.binance.org

# 获取内部交易(如果需要)
cast run <txHash> --rpc-url https://bsc-dataseed.binance.org
```

记录: 实际调用的函数选择器/参数/返回值/事件日志.

---

## 步骤 4: 漏洞分类

根据漏洞特征判断类型, 参考 `CLAUDE_PLUGIN_ROOT/agents/smart-contract-vuln/resources/CLAUDE.md` 中的分类体系:

| 分类关键词 | 对应资源文件 | 典型特征 |
|-----------|-------------|---------|
| 0xdead, whitelist-bypass, transfer-bypass | dead-address-whitelist-bypass.md | 硬编码魔法地址绕过检查 |
| reward-manipulation, denominator, dividend, timing | reward-manipulation.md | 奖励计算分母操纵/会计时序 |
| arithmetic, overflow, underflow | arithmetic-vulns.md | 整数溢出/精度丢失 |
| reentrancy | (需新建或搜索) | 重入攻击 |
| flash-loan, price-manipulation | risk-free-arbitrage.md | 闪电贷价格操纵 |
| negative-amount | negative-amount-vulns.md | 负数金额绕过 |

**分类判断规则**:
- 不能确定分类 -> 使用 x-search 搜索更多分析后决定
- 同时涉及多个类型 -> 按主因分类, 在其他文件中交叉引用
- 新类型(无对应资源文件) -> 新建资源文件

---

## 步骤 5: 整理到知识库

### 5.1 确定目标文件

```
CLAUDE_PLUGIN_ROOT/agents/smart-contract-vuln/resources/<漏洞类型>.md
```

- 已存在 -> 读取现有内容, 追加案例到"真实案例"表格
- 不存在 -> 按资源文件格式规范(CLAUDE.md)创建新文件

### 5.2 资源文件格式

按 `resources/CLAUDE.md` 定义的格式:

```
# [漏洞类型中文名]

**关键词**: 英文关键词, 逗号分隔

**来源URL**:
- 来源名称: URL

**适用范围**: 描述

## 漏洞原理
(核心概念 + 有漏洞的代码片段 + 触发条件)

## 变种与衍生
(变种表格)

## 审计检查清单
(# | 检查项 | 风险等级 表格)

## 检测方法
(Grep/Slither/Foundry 方法)

## 真实案例
(事件|日期|损失|根因|攻击链 表格)
```

### 5.3 追加案例规则

- 真实案例表格追加新行, 禁止覆盖已有案例
- 来源URL追加新链接
- 如果新案例暴露了新的变种, 需同步更新"变种与衍生"和"审计检查清单"

---

## 步骤 6: 输出总结

向用户输出处理结果:

```
## 漏洞推文处理完成

| 项目 | 内容 |
|------|------|
| 推文来源 | @author/status/xxx |
| 漏洞类型 | <分类> |
| 资源文件 | resources/<文件>.md (新建/追加) |
| 链上验证 | cast tx/receipt 已执行/未执行(原因) |
```