# skills

自己的技能库

## 安装使用方法

```bash
# 插件
/plugin marketplace add ~/Downloads/skills

# 技能
bunx skills add ~/Downloads/skills/skills

# 通用,禁止安装第三方未知技能,防止后门
bunx skills add https://github.com/anthropics/skills --skill skill-creator
bunx skills add https://github.com/vercel-labs/agent-skills --skill vercel-react-best-practices
bunx skills add https://github.com/vercel-labs/agent-skills --skill web-design-guidelines

# APP通用
bunx skills add expo/skills

bunx skills add vercel-labs/agent-skills
```
