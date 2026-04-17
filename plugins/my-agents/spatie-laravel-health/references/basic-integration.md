# 基础集成流程

- 安装包后必须先发布迁移 (若使用 EloquentHealthResultStore):
  ```bash
  php artisan vendor:publish --tag="health-migrations"
  php artisan migrate
  ```
- 创建独立的 `app/Providers/HealthServiceProvider.php` 注册检查, 不要直接改 `AppServiceProvider`.
- 在 `bootstrap/providers.php` 注册 `HealthServiceProvider`.
- 在 `routes/web.php` 注册 `/health` 页面路由 (包不会自动注册), 并挂载 `RequiresSecretToken` 中间件:
  ```php
  use Spatie\Health\Http\Controllers\HealthCheckResultsController;
  use Spatie\Health\Http\Middleware\RequiresSecretToken;

  Route::get('/health', HealthCheckResultsController::class)
      ->middleware(RequiresSecretToken::class)
      ->name('health');
  ```
- 在 `routes/console.php` 调度以下命令 (只注册 Check 不会自动执行):
  ```php
  // 调度器心跳(供 ScheduleCheck 读取)
  Schedule::command('health:schedule-check-heartbeat')
      ->everyMinute()
      ->withoutOverlapping()
      ->onOneServer()
      ->appendOutputTo(storage_path('logs/health_schedule_heartbeat.log'));

  // 队列心跳(供 QueueCheck 读取, 需要异步队列 worker 消费)
  Schedule::command('health:queue-check-heartbeat')
      ->everyMinute()
      ->withoutOverlapping()
      ->onOneServer()
      ->appendOutputTo(storage_path('logs/health_queue_heartbeat.log'));

  // 系统健康检查
  Schedule::command('health:check')
      ->everyMinute()
      ->withoutOverlapping()
      ->onOneServer()
      ->appendOutputTo(storage_path('logs/health_check.log'));
  ```
- **所有 Schedule 调度必须加 `withoutOverlapping()` 和 `onOneServer()`**, 防止多实例重复执行.

## HealthServiceProvider 示例

```php
<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Spatie\Health\Checks\Checks\CacheCheck;
use Spatie\Health\Checks\Checks\DatabaseCheck;
use Spatie\Health\Checks\Checks\QueueCheck;
use Spatie\Health\Checks\Checks\ScheduleCheck;
use Spatie\Health\Checks\Checks\UsedDiskSpaceCheck;
use Spatie\Health\Facades\Health;

class HealthServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        Health::checks([
            DatabaseCheck::new()->label('数据库连接'),
            CacheCheck::new()->label('缓存服务'),
            ScheduleCheck::new()->label('定时任务调度'),
            QueueCheck::new()->label('队列服务'),
            UsedDiskSpaceCheck::new()
                ->label('磁盘空间')
                ->warnWhenUsedSpaceIsAbovePercentage(70)
                ->failWhenUsedSpaceIsAbovePercentage(90)
                ->daily(),
        ]);
    }
}
```
