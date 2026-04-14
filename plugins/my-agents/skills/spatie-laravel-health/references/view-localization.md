# 视图汉化与主题美化

- 先发布视图:
  ```bash
  php artisan vendor:publish --tag="health-views"
  ```
- **必须加载项目自身 CSS**: `resources/views/vendor/health/list.blade.php` 的 `<head>` 中必须引入项目主样式, 否则自定义 Tailwind 工具类全部失效:
  ```blade
  @vite('resources/css/app.css')
  ```
- **必须根据项目主题风格美化**: 重新设计 `list.blade.php`, 不要保留 spatie 默认的白底 light/dark 通用样式.
- 同步或创建 `lang/vendor/health/zh_CN/notifications.php` 和 `lang/vendor/health/en/notifications.php` 语言包, 两个都要同步更新:
  ```php
  return [
      'laravel_health' => '健康检查中心',
      'check_failed_mail_subject' => ':application_name 的健康检查出现失败项',
      'check_failed_mail_body' => '以下检查报告了警告或错误:',
      'check_failed_slack_message' => ':application_name 的健康检查出现失败项.',
      'health_results' => '健康检查中心',
      'check_results_from' => '检查结果来源',
      'total_checks' => '检查总数',
      'passed' => '通过',
      'issues' => '异常',
      'run_command_hint' => '请执行以下命令:',
      'no_checks_run_title' => '尚未运行任何检查',
  ];
  ```
- 修改 `resources/views/vendor/health/list.blade.php` 和 `list-cli.blade.php` 中的静态文本为翻译键或中文.
- 状态文本映射 (用 `strtolower()` 匹配):
  ```php
  $statusMap = [
      'ok'      => '正常',
      'warning' => '警告',
      'failed'  => '失败',
      'crashed' => '崩溃',
      'skipped' => '跳过',
  ];
  ```
- 修改后执行 `php artisan view:clear` 清缓存.

## 视图自定义注意事项

- `lang` 属性必须使用动态值, 禁止硬编码 `en`:
  ```html
  <html lang="{{ str_replace('_', '-', app()->getLocale()) }}" ...>
  ```
- vendor publish 会覆盖自定义视图, 重新发布时注意备份或重新修改
- `$checkResults->storedCheckResults` 返回的是 `Collection`, 不是数组, 必须用 `$collection->filter()` 而不是 `array_filter()`
- 视图中的 `$result->status` 可能是字符串也可能是对象 (有 `->value`), 必须做类型判断:
  ```php
  @php($statusValue = is_object($result->status) ? $result->status->value : $result->status)
  ```
- 去掉底部 `Powered by spatie/laravel-health` 信息, 保持页面整洁
