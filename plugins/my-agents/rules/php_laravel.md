# PHP/Laravel 规范

- 统一顶部使用 use
- 自定义异常类必须包含参数和消息
- 优先使用 `throw_if` 和 `throw_unless` 而不是 `throw`
- nova-components 本地包必须包含 `version` 字段, 否则 Composer 无法正确引用
