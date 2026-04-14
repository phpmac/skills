# 基础集成流程

- 安装包后必须先发布迁移 (若使用 EloquentHealthResultStore):
  ```bash
  php artisan vendor:publish --tag="health-migrations"
  php artisan migrate
  ```
- 创建独立的 `app/Providers/HealthServiceProvider.php` 注册检查, 不要直接改 `AppServiceProvider`.
- 在 `bootstrap/providers.php` 注册 `HealthServiceProvider`.
- 在 `routes/console.php` 调度 `health:check` 命令 (只注册 Check 不会自动执行).
- 在 `routes/web.php` 注册 `/health` 页面路由 (包不会自动注册), 并视情况挂载 `RequiresSecretToken` 中间件:
  ```php
  use Spatie\Health\Http\Controllers\HealthCheckResultsController;
  use Spatie\Health\Http\Middleware\RequiresSecretToken;

  Route::get('/health', HealthCheckResultsController::class)
      ->middleware(RequiresSecretToken::class)
      ->name('health');
  ```

## HealthServiceProvider 示例

```php
<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Spatie\Health\Checks\Checks\CacheCheck;
use Spatie\Health\Checks\Checks\DatabaseCheck;
use Spatie\Health\Checks\Checks\DebugModeCheck;
use Spatie\Health\Checks\Checks\QueueCheck;
use Spatie\Health\Checks\Checks\ScheduleCheck;
use Spatie\Health\Checks\Checks\UsedDiskSpaceCheck;
use Spatie\Health\Facades\Health;

class HealthServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        Health::checks([
            DatabaseCheck::new()->label('数据库连接')->hourly(),
            CacheCheck::new()->label('缓存服务')->hourly(),
            ScheduleCheck::new()->label('定时任务调度')->hourly(),
            QueueCheck::new()->label('队列服务')->hourly(),
            UsedDiskSpaceCheck::new()
                ->label('磁盘空间')
                ->warnWhenUsedSpaceIsAbovePercentage(70)
                ->failWhenUsedSpaceIsAbovePercentage(90)
                ->daily(),
            DebugModeCheck::new()->label('调试模式'),
        ]);
    }
}
```
