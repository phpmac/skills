---
name: block-server-startup
enabled: true
event: bash
pattern: (npm|yarn|pnpm|bun)\s+(run\s+)?(dev|start)|(next|vite|vue-cli-service)\s+(dev|serve)|php\s+(-S\s+|artisan\s+serve)|python\d?\s+(-m\s+http\.server| -m\s+SimpleHTTPServer)|flask\s+run|django-admin\s+runserver|uvicorn\s+|gunicorn\s+|rails\s+s|go\s+run\s+main\.go
action: block
---

**禁止直接启动开发服务器**

以下命令需要用户明确确认才能执行:
- npm/yarn/pnpm/bun run dev|start
- next dev, vite, rails s
- php -S, php artisan serve
- python -m http.server
- flask run, django-admin runserver

**必须获得用户明确同意后才能执行此类命令**
