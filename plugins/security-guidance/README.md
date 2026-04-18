# security-guidance

安全提醒 Hook 插件, 在编辑文件时自动检测并警告潜在的安全问题.

## 功能

通过 `PreToolUse` Hook 在文件编辑操作前检查:

- 命令注入 (Command Injection)
- XSS (Cross-Site Scripting)
- 不安全的代码模式
- 其他 OWASP Top 10 安全风险

## 工作原理

当检测到编辑操作 (`Write`/`Edit` 工具) 时, Hook 脚本分析文件内容, 发现安全隐患时输出警告.

## 安装

插件通过 `hooks/hooks.json` 自动注册, 无需额外配置.

## 作者

David Dworken (dworken@anthropic.com)
