# skills

自己的技能库

## 安装使用方法

```bash
# 本地安装,会自己安装插件和skills
/plugin marketplace add ~/Downloads/skills

# 一键复制 hookify 规则到 ~/.claude/ 目录下
rm -rf ~/.claude/hookify.* && cp plugins/hookify/examples/* ~/.claude/

bunx skills add OpenZeppelin/openzeppelin-skills

rm -rf ~/.codex
rm -rf ~/.agents
rm -rf ~/.claude/agents ~/.claude/skills

```

## 注意事项

- 修改插件需要卸载重新安装


## 参考

[借鉴了官方应用市场](https://github.com/anthropics/claude-code)