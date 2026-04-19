# 常见陷阱

- 注册了 Check 但忘记调度 `health:check`, 页面永远显示 No checks have run yet.
- `Result::ok()` 静态调用触发 IDE 警告 PHP1413.
- 汉化时直接用 `$result->status` 做键名匹配失败, 因为首字母大写, 必须用 `strtolower()`.
- 自定义 Check 修改后没有清 view cache, 页面不生效.
- 在 Nova 中为 vendor 模型的 `HealthCheckResultHistoryItem` 创建 Resource 时, 如果直接写 `DateTime` 字段会炸, 切记改用 `Text`.
- `list-cli.blade.php` 中的 `$result->status` 在 CLI 模式下可能是字符串而非对象, 访问 `->value` 会报错. 兼容写法:
  ```php
  @php($statusValue = is_object($result->status) ? $result->status->value : $result->status)
  ```
- `->label()` 只影响视图/通知展示, 存入 `check_name` 字段的是 `getName()`. 若要在 Nova 后台也显示中文, 请用 `->name('中文名')` 而不是 `->label('中文名')`.
