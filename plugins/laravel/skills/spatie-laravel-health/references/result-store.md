# 结果存储选择

- **EloquentHealthResultStore** (默认): 需要迁移表 `health_check_result_history_items`, 支持历史记录.
- **JsonFileHealthResultStore**: 不需要数据库, 适合无 DB 场景.
- 在 `config/health.php` 的 `result_stores` 中配置.
