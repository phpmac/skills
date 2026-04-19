# 智能合约安全审计插件

## 规则

- 审计方法遵循 security.md 规范: 禁止编造PoC/未验证标severity/区分未验证vs确认可利用
- 触发 agent/skill 前必须检查工具依赖(foundry/cast/slither等), 缺失则停止报告
