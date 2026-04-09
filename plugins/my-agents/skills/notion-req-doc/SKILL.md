---
name: notion-req-doc
description: 当用户要求 "整理需求到Notion", "编写技术需求文档", "格式化产品需求到Notion页面", "Notion文档排版", "整理到Notion", "格式化需求", 或用户提到需求文档/PRD/Notion格式化时应使用此技能. 将原始需求整理为结构化的Notion技术开发需求文档
---

# Notion 技术需求文档整理

将原始需求/会议纪要/零散信息整理为结构化的 Notion 技术开发需求文档.

## 文档模板

参考 `references/req-doc-template.md` 中的排版结构示例.

**重要**: 模板只是结构参考, 实际使用时根据项目需求自行组织:
- 章节数量和标题根据实际项目调整
- 模块内容根据实际业务逻辑填充
- 不需要的章节直接删除, 缺少的章节自行补充
- 表格列数/折叠块数量/流程图复杂度根据实际情况决定

## 排版规则

### 标题
- 使用 `## 数字. 标题` 编号格式
- 不使用一级标题 `#`, 从二级 `##` 开始

### 信息提示
- 使用引用块 `>` 表示提示/说明信息
- **禁止使用** `<callout>` 标签

### 流程图
- **禁止使用 Mermaid** (```mermaid)
- 使用代码块 `` ```text `` 包裹 ASCII 字符流程图
- 简单流程: `A ──> B ──> C`
- 带分支流程:
```
              ┌── 选项A ──┐
起点 ────┤            ├──> 结果
              └── 选项B ──┘
```
- 系统架构用 ASCII 框图

### 表格
- 使用 Notion `<table>` 标签, 不用 Markdown 表格语法
- 设置 `header-row="true"`
- **禁止使用** `fit-page-width="true"` -- 会导致列宽不均匀
- 必须使用 `<colgroup>` + `<col width="数值">` 手动设置每列宽度
- 需要颜色区分的单元格用 `<td color="颜色">`
- 表格内加粗用 `**文字**`

### 折叠内容
- 使用 `<details>` + `<summary>` 实现折叠块
- `<summary>` 内为折叠标题
- 子内容必须用 tab 缩进

### 其他规则
- 项目总览用简洁列表 `- **标签**: 内容`
- 分隔线使用 `---` 分隔主要章节
- 待确认/待办事项使用 checkbox `- [ ]` 格式
- 状态类单元格用颜色: `<td color="green">是</td>`, `<td color="gray">否</td>`

## 禁止使用

- `<table_of_contents/>` -- 不需要目录

## 工作流程

1. **获取原始信息**: fetch Notion 页面或读取用户提供的内容
2. **分析需求**: 识别代币/资产体系, 业务流程, 技术要求
3. **识别缺失**: 列出需求中的模糊点和待确认问题
4. **按模板格式化**: 使用排版规则写入 Notion
5. **写入 Notion**: 使用 notion-update-page 的 replace_content 命令
6. **验证**: fetch 页面确认格式正确

## 关键注意事项

- Notion `<table>` 标签内行和列必须用 tab 缩进
- `<details>` 子内容必须用 tab 缩进才能正确折叠
- Notion 会自动把 `` ``` `` 识别为 mermaid, 必须明确写 `` ```text ``
- 不要尝试写入 `<meeting-notes>` 块, 它是 Notion 会议功能的特殊块, AI 不可编辑 transcript
- 写入前先 fetch 获取 Notion enhanced-markdown-spec 确认语法
- **replace_content 前必须检查页面是否有 meeting-notes 块, 如果有必须在 new_str 末尾保留原始 meeting-notes 块 (包含 readOnlyViewMeetingNoteUrl), 否则会永久删除录音转写数据, 不可恢复**
- 不确定原始 meeting-notes 内容时, 先 fetch 获取完整内容再拼接进 new_str

## 附加资源

文档排版模板详见 `references/req-doc-template.md`.
