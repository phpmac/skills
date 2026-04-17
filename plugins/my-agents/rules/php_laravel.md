---
paths:
  - "**/*.php"
  - "**/composer.json"
  - "**/artisan"
---

# PHP/Laravel 规范

- 统一顶部使用 use
- 如果是国际化一定要注意多语言国际化对齐不要遗漏
- 禁止使用 `vendor/bin/sail` 应该使用 `php` 替换
- 优先使用 `throw_if` 和 `throw_unless` 而不是 `throw`
- 自定义异常类必须包含参数和消息,这样异常才能丰富记录错误详情
- 后台管理使用的是 laravel nova 框架, 所以需要遵循 laravel nova 的规范
- Nova Resource 字段必须使用 Panel 分组展示, 禁止平铺所有字段. 参考: 余额/收益归一个Panel, 业绩归一个Panel, 状态/权限归一个Panel
- nova-components 本地包必须包含 `version` 字段, 否则 Composer 无法正确引用
- 非Laravel框架格式化使用 `vendor/bin/pint` 命令; Laravel框架使用 `bun run a` 格式化, 提交代码和commit之前必须执行
- 创建/修改 Nova Resource 后必须同步更新 NovaServiceProvider 的菜单配置, 禁止只创建 Resource 而不配置菜单
- 创建 Nova Resource 时必须同时创建对应的 Policy (make:policy --model=Xxx), 否则资源在后台不显示; 且禁止删除 Dashboard 引用否则首页 404
- Nova Action 设计原则: 互斥操作(启用/禁用, 冻结/解冻)必须合并为一个 Action 切换状态, 禁止拆成2个独立 Action.
- 创建 Nova Resource 时必须同时处理 Factory 和 Seeder, 确保后台有初始配置数据(如提现配置), 禁止只建空表
- Spatie Health 集成使用 `spatie-laravel-health` Skill, 规则详见该 Skill
