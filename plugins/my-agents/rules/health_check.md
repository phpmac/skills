# 系统/健康检查/自检/回归检查规范

## 数据一致性自检

- 涉及资金/余额/库存等数值字段, 数据库层(migration)必须用 unsigned/CHECK 约束防止负数, 应用层必须有定时校验任务
- 核心业务表必须配置定期自检: 孤儿记录/金额汇总不匹配/外键完整性/状态机合法性
- 自检频率分层: 关键数据(余额/状态)每小时, 业务数据(订单对账)每日, 全量扫描每周低峰期
- 自检发现异常必须记录: 检测时间/影响范围/异常数据快照/修复动作/修复前后对比
- 自检任务必须接入告警(邮件/Slack/Discord), 检测到 Critical 级别问题必须即时通知

## 已修复问题回归

- 每个 bugfix 必须附带回归断言或测试用例, 纳入 CI/CD 管道或定时自检任务
- 安全漏洞修复后必须编写 PoC 测试用例, 验证漏洞触发条件已被阻断, 且每次发布自动运行
- 回归测试需与原始问题关联(工单号/CVE编号), 便于追溯
- 回归测试按风险分级: Critical/High 级别每次发布必跑, Medium/Low 可按变更范围选择性运行

## 业务不变量断言

- 关键业务流程必须定义不变量规则(invariant), 例如: 已发货订单必须已付款/活跃订阅必须有支付方式/提现金额不超过可用余额
- 不变量检查实现为独立的 Check 类(Laravel 用 spatie/laravel-health)或定时任务, 不嵌入业务逻辑中
- 新增业务流程时必须同步定义对应的不变量检查, 禁止事后补加

## 部署后冒烟测试

- 核心接口(认证/支付/关键读写)必须有 post-deploy smoke test, 部署失败自动回滚
- smoke test 必须是只读/幂等的, 不产生脏数据
- 非 K8s 环境: 部署脚本中集成 smoke test 步骤; K8s 环境: 配置 readiness probe + smoke test job
- smoke test 失败必须阻断发布流程, 禁止人工跳过

## Laravel 项目额外要求 (基于 spatie/laravel-health)

- 使用 spatie/laravel-health 包, 在 ServiceProvider 中通过 `Health::checks([...])` 注册
- 必须注册的内置检查: DatabaseCheck/CacheCheck/ScheduleCheck/QueueCheck
- 自定义 Check 类放在 `app/Health/Checks/` 目录, 继承 `Spatie\Health\Checks\Check`, 实现 `run(): Result`
- Result 三态: `Result::ok()` / `Result::warning()` / `Result::failed()`, 传入字符串才会触发通知, 不传字符串只记录不通知
- 每个检查独立控制频率: `->daily()` / `->dailyAt('02:00')` / `->hourly()` / `->timezone('Asia/Shanghai')`, 按数据重要性分层
- 结果存储使用 EloquentHealthResultStore, 配置 `keep_history_for_days` 控制保留天数(默认5天)
- 通知节流: 配置 `throttle_notifications_for_minutes` 防止频繁告警轰炸
- 健康检查端点必须配置认证中间件或 Secret Token, 禁止裸露内部状态
