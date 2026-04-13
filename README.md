# skills

自己的技能库

## claude code 安装使用方法

```bash
# 本地安装,会自己安装插件和skills
/plugin marketplace add ~/Downloads/skills

/plugin marketplace add anthropics/claude-plugins-official
/plugin install discord@claude-plugins-official
mkdir -p ~/.claude/channels/discord && echo "DISCORD_BOT_TOKEN=xxxx" > ~/.claude/channels/discord/.env
mkdir -p ~/.claude/channels/x-search && echo 'XAI_API_KEY=xxx' > ~/.claude/channels/x-search/.env
mkdir -p ~/.claude/channels/discord && rm -f ~/.claude/channels/discord/access.json && ln -s ~/Downloads/skills/plugins/my-agents/discord/access.json ~/.claude/channels/discord/access.json

bunx skills add OpenZeppelin/openzeppelin-skills

rm -rf ~/.codex
rm -rf ~/.agents

rm -rf $HOME/.claude/cache/*
rm -rf ~/.claude/agents ~/.claude/skills
mkdir -p ~/.cursor && rm -f ~/.cursor/mcp.json && ln -s $HOME/.claude.json ~/.cursor/mcp.json
rm -rf ~/.claude/hookify.* && ln -sf "$PWD"/plugins/hookify/examples/* ~/.claude/
rm -rf ~/.claude/rules && ln -sf ~/Downloads/skills/plugins/my-agents/rules ~/.claude/rules
rm -rf ~/.claude/CLAUDE.md && ln -s ~/Downloads/skills/plugins/my-agents/CLAUDE.md ~/.claude/CLAUDE.md
rm -rf ~/.claude/settings.json && ln -s ~/Downloads/skills/plugins/my-agents/settings.json ~/.claude/settings.json


# 安装最新稳定版
curl -fsSL https://claude.ai/install.sh | bash -s stable


# 添加全局mcp
claude mcp add firecrawl --scope user -e FIRECRAWL_API_KEY=fc-80cea7731f86442e8471cab13deca196 -- bunx -y firecrawl-mcp
claude mcp add --scope user context7 -- bunx -y @upstash/context7-mcp --api-key ctx7sk-86b4a09c-599d-4460-9854-d3ce26edd3e0
claude mcp add --transport http notion --scope user https://mcp.notion.com/mcp
claude mcp add --transport http exa --scope user https://mcp.exa.ai/mcp

# 暂时不用
claude mcp add --scope user chrome-devtools -- bunx chrome-devtools-mcp@latest --autoConnect --channel=beta

# 移除 MCP
claude mcp remove chrome-devtools
claude mcp remove chrome-devtools -s user

# 暂时不用
claude mcp add cloudflare-api --transport http --scope user https://mcp.cloudflare.com/mcp
claude mcp add -s user zai-mcp-server --env Z_AI_API_KEY=dbbcb136a5714cfb829e0b074a3e43aa.kfw0nT1CqXLzESs0 Z_AI_MODE=ZAI -- bunx -y "@z_ai/mcp-server"
claude mcp add --transport http exa --scope user "https://mcp.exa.ai/mcp?tools=web_search_exa,get_code_context_exa,crawling_exa,company_research_exa,linkedin_search_exa,deep_researcher_start,deep_researcher_check&exaApiKey=b0de283e-7daf-4745-bc4d-a1e0b530c17c"


```


## codex 安装使用方法

```sh
# 配置文件
mkdir -p ~/.codex && rm -f ~/.codex/config.toml && ln -s ~/Downloads/skills/.codex/config.toml ~/.codex/config.toml
rm -rf ~/.codex/AGENTS.md && ln -s ~/Downloads/skills/plugins/my-agents/CLAUDE.md ~/.codex/AGENTS.md
# 启用记忆功能
codex features enable memories
rm -rf ~/.codex/memories && ln -sf ~/Downloads/skills/plugins/my-agents/rules ~/.codex/memories


# 添加全局 MCP
codex mcp add firecrawl --env FIRECRAWL_API_KEY=fc-80cea7731f86442e8471cab13deca196 -- bunx -y firecrawl-mcp
codex mcp add context7 -- bunx -y @upstash/context7-mcp --api-key ctx7sk-86b4a09c-599d-4460-9854-d3ce26edd3e0
codex mcp add notion --url https://mcp.notion.com/mcp
codex mcp add exa --url "https://mcp.exa.ai/mcp?tools=web_search_exa,get_code_context_exa,crawling_exa,company_research_exa,linkedin_search_exa,deep_researcher_start,deep_researcher_check&exaApiKey=b0de283e-7daf-4745-bc4d-a1e0b530c17c"


# 移除 MCP
codex mcp remove chrome-devtools


# 暂时不用
codex mcp add chrome-devtools -- bunx chrome-devtools-mcp@latest --autoConnect --channel=beta
codex mcp add cloudflare-api --url https://mcp.cloudflare.com/mcp
codex mcp add zai-mcp-server --env Z_AI_API_KEY=dbbcb136a5714cfb829e0b074a3e43aa.kfw0nT1CqXLzESs0 Z_AI_MODE=ZAI -- bunx -y "@z_ai/mcp-server"


```


## 参考资源

[借鉴了 claode code 官方应用市场](https://github.com/anthropics/claude-code)