# skills

自己的技能库

## 安装使用方法

```bash
# 本地安装,会自己安装插件和skills
/plugin marketplace add ~/Downloads/skills
# 本地安装,会自己安装插件和skills
/plugin marketplace add ~/Downloads/skills

# 一键复制 hookify 规则到 ~/.claude/ 目录下

bunx skills add OpenZeppelin/openzeppelin-skills

rm -rf ~/.codex
rm -rf ~/.agents

rm -rf $HOME/.claude/cache/*
rm -rf ~/.claude/agents ~/.claude/skills
rm -rf ~/.cursor/mcp.json && ln -s $HOME/.claude.json ~/.cursor/mcp.json
rm -rf ~/.claude/hookify.* && ln -sf "$PWD"/plugins/hookify/examples/* ~/.claude/
rm -rf ~/.claude/rules && ln -sf ~/Downloads/skills/plugins/my-agents/rules ~/.claude/rules
rm -rf ~/.claude/CLAUDE.md && ln -s ~/Downloads/skills/plugins/my-agents/CLAUDE.md ~/.claude/CLAUDE.md
rm -rf ~/.claude/settings.json && ln -s ~/Downloads/skills/plugins/my-agents/settings.json ~/.claude/settings.json


# 安装最新稳定版
curl -fsSL https://claude.ai/install.sh | bash -s stable


# 添加全局mcp
claude mcp add firecrawl --scope user -e FIRECRAWL_API_KEY=fc-80cea7731f86442e8471cab13deca196 -- bunx -y firecrawl-mcp
claude mcp add --scope user context7 -- bunx -y @upstash/context7-mcp --api-key ctx7sk-86b4a09c-599d-4460-9854-d3ce26edd3e0
claude mcp add --scope user supermemory --transport sse https://mcp.supermemory.ai/mcp
claude mcp add --transport http notion --scope user https://mcp.notion.com/mcp
claude mcp add --scope user duckdb --transport stdio ~/Downloads/skills/plugins/my-agents/duckdb-mcp-server.sh
claude mcp add --transport http exa --scope user https://mcp.exa.ai/mcp


claude mcp add --scope user chrome-devtools -- bunx chrome-devtools-mcp@latest --autoConnect --channel=beta


duckdb -c "
INSTALL duckdb_mcp FROM community;
INSTALL duck_tails FROM community;
INSTALL hostfs FROM community;
INSTALL read_lines FROM community;
INSTALL crawler FROM community;
INSTALL mongo FROM community;
INSTALL crypto FROM community;
"

claude mcp remove exa
claude mcp remove exa -s user

claude mcp add cloudflare-api --transport http --scope user https://mcp.cloudflare.com/mcp
claude mcp add -s user zai-mcp-server --env Z_AI_API_KEY=dbbcb136a5714cfb829e0b074a3e43aa.kfw0nT1CqXLzESs0 Z_AI_MODE=ZAI -- bunx -y "@z_ai/mcp-server"
claude mcp add --transport http exa --scope user "https://mcp.exa.ai/mcp?tools=web_search_exa,get_code_context_exa,crawling_exa,company_research_exa,linkedin_search_exa,deep_researcher_start,deep_researcher_check&exaApiKey=b0de283e-7daf-4745-bc4d-a1e0b530c17c"


```

## 注意事项

- 修改插件需要卸载重新安装

## 参考

[借鉴了官方应用市场](https://github.com/anthropics/claude-code)