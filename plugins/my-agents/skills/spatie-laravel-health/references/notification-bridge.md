# 通知渠道替换 (复用 guanguans/laravel-exception-notify)

`spatie/laravel-health` 的 `CheckFailedNotification` 只原生实现了 `toMail()` 和 `toSlack()`, 没有 `toDiscord()`.
若项目已集成 `guanguans/laravel-exception-notify`, 最佳方案是:

1. 新建自定义 Notification 继承 `CheckFailedNotification`:

```php
<?php

namespace App\Notifications;

use Guanguans\LaravelExceptionNotify\Facades\ExceptionNotify;
use Spatie\Health\Checks\Result;
use Spatie\Health\Notifications\CheckFailedNotification;

class HealthCheckFailedDiscordNotification extends CheckFailedNotification
{
    public function via(): array
    {
        ExceptionNotify::reportContent($this->buildContent());
        return [];
    }

    private function buildContent(): string
    {
        $lines = ['**健康检查告警**', '应用: '.config('app.name').' ('.app()->environment().')', '-----------------------------------'];
        foreach ($this->results as $result) {
            /** @var Result $result */
            $lines[] = sprintf('**[%s] %s**', strtoupper((string) $result->status->value), $result->check->getLabel());
            if ($result->getNotificationMessage()) { $lines[] = $result->getNotificationMessage(); }
            if ($result->shortSummary) { $lines[] = '摘要: '.$result->shortSummary; }
            $lines[] = '';
        }
        return implode("\n", $lines);
    }
}
```

2. 修改 `config/health.php`:

```php
'notifications' => [
    \App\Notifications\HealthCheckFailedDiscordNotification::class => [],
],
```

## 要点

- 保留 `shouldSend()` 的 `enabled` 开关和 throttle 限流逻辑
- `via()` 中直接调用 `ExceptionNotify::reportContent()`, **不要**写死 `->driver('discord')`, 让它跟随 exception-notify 的默认通知配置
- 返回 `[]` 阻止 Laravel 继续调用 `toMail()` / `toSlack()`
