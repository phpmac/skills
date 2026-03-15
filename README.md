# skills

自己的技能库

## 安装使用方法

```bash
# 本地安装,会自己安装插件和skills
/plugin marketplace add ~/skills
/plugin marketplace add ~/Downloads/skills

/plugin marketplace add anthropics/claude-code

# 一键复制 hookify 规则到 ~/.claude/ 目录下
rm -f ~/.claude/hookify.* && cp plugins/hookify/examples/* ~/.claude/

bunx skills add OpenZeppelin/openzeppelin-skills

rm -rf ~/.codex
rm -rf ~/.agents
rm -rf ~/.claude/agents/* ~/.claude/skills/*

# 自动映射 agents/skills

# linux
ln -s ~/skills/.claude/agents ~/.claude/agents
ln -s ~/skills/.claude/skills ~/.claude/skills

# mac
ln -s ~/Downloads/skills/.claude/agents ~/.claude/agents
ln -s ~/Downloads/skills/.claude/skills ~/.claude/skills

# 最后都可以执行这个
ln -s ~/.claude/skills ~/.cursor/skills
ln -s ~/.claude/skills ~/.agents/skills



```

[借鉴了官方应用市场](https://github.com/anthropics/claude-code)