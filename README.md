# skills

自己的技能库

## claude code 安装使用方法

```bash
# 本地安装,会自己安装插件和skills
/plugin marketplace add ~/Downloads/skills

/plugin marketplace add anthropics/claude-plugins-official
/plugin install discord@claude-plugins-official


# 待配置
mkdir -p ~/.claude/channels/discord && echo "DISCORD_BOT_TOKEN=xxxx" > ~/.claude/channels/discord/.env
mkdir -p ~/.claude/channels/x-search && echo 'XAI_API_KEY=xxx' > ~/.claude/channels/x-search/.env
mkdir -p ~/.claude/arl && echo 'ARL_URL=http://45.82.121.205:5002
ARL_TOKEN=xxx' > ~/.claude/arl/.env
mkdir -p ~/.claude/channels/discord && rm -f ~/.claude/channels/discord/access.json && ln -s ~/Downloads/skills/plugins/my-agents/discord/access.json ~/.claude/channels/discord/access.json
mkdir -p ~/.claude/hacker-tools && echo 'FOFA_KEY=xxx
SHODAN_API_KEY=xxx
ZOOMEYE_API_KEY=xxx
DNSDUMPSTER_API_KEY=xxx
VIRUSTOTAL_API_KEY=xxx
CENSYS_ORGANIZATION_ID=xxx
CENSYS_TOKEN=xxx
VULDB_API_KEY=xxx
HUNTER_HOW_API_KEY=xxx
CVE_API_KEY=xxx
ST_API=xxx' > ~/.claude/hacker-tools/.env

bunx skills add OpenZeppelin/openzeppelin-skills

rm -rf ~/.codex
rm -rf ~/.agents

rm -rf $HOME/.claude/cache/*
rm -rf ~/.claude/agents ~/.claude/skills
rm -rf ~/.claude/rules && ln -sf ~/Downloads/skills/plugins/my-agents/rules ~/.claude/rules
mkdir -p ~/.cursor && rm -f ~/.cursor/mcp.json && ln -s $HOME/.claude.json ~/.cursor/mcp.json
cd /Users/a/Downloads/skills/plugins/hookify/examples; ln -sf (pwd)/hookify.*.local.md ~/.claude/
rm -rf ~/.claude/CLAUDE.md && ln -s ~/Downloads/skills/plugins/my-agents/CLAUDE.md ~/.claude/CLAUDE.md
rm -rf ~/.claude/settings.json && ln -s ~/Downloads/skills/plugins/my-agents/settings.json ~/.claude/settings.json


# 安装最新稳定版
curl -fsSL https://claude.ai/install.sh | bash -s stable


# 移除 MCP
claude mcp remove firecrawl -s user
claude mcp remove context7 -s user
claude mcp remove notion -s user
claude mcp remove exa -s user
claude mcp remove chrome-devtools -s user
claude mcp remove flare-api -s user


```


## 参考资源

[借鉴了 claode code 官方应用市场](https://github.com/anthropics/claude-code)
