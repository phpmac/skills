# Nova 展示结果

- 存储模型: `Spatie\Health\Models\HealthCheckResultHistoryItem` (由 `EloquentHealthResultStore` 写入)
- 该模型 **没有** 将 `ended_at` / `created_at` cast 为 `datetime`, 因此 Nova 的 `DateTime` 字段会报错: `DateTime field must cast to 'datetime' in Eloquent model.`
- **解决方案**: 使用 `Text` 字段 + `displayUsing(fn ($value) => $value ? Carbon::parse($value)->format('Y-m-d H:i:s') : '-')` 来展示时间
- 使用 `Badge` 展示 `status`, 配合 `map` + `labels` 做中文和颜色映射
- 字段上加 `->filterable()` 即可启用列级筛选, 无需额外创建 Filter 类
- Nova Resource 的 `label()` 建议命名为 **"系统自检"**, 而不是 "健康检查结果"
- 菜单挂载时, 分组名称用 **"健康检查"**, 保持简洁
- 由于 `MenuItem::resource()` 不支持 `->icon()`, 若需要图标, 必须用 `MenuSection::make('健康检查', [MenuItem::resource(...)])->icon('heart')->collapsable()` 包装
- 该模型来自 vendor, **无需**单独创建 Policy, 由 Nova 的 `viewNova` gate 统一控制后台访问权限即可
