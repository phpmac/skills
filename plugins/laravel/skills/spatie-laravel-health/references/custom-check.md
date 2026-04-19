# 自定义 Check 规范

- 放置目录: `app/Health/Checks/`
- 继承: `Spatie\Health\Checks\Check`
- 返回类型: `Spatie\Health\Checks\Result`
- **禁止**静态调用 `Result::ok()` 或 `Result::failed()`, 应使用:
  - `Result::make('message')` (默认 ok)
  - `Result::make()->failed('message')`
- 检查项中文名称通过 `->label('中文名称')` 设置.
