# Nova后台设计详细规范

## Resource 完整创建清单

创建 Nova Resource 时必须一次性处理以下全部内容:

```
□ php artisan nova:resource ModelName
□ php artisan make:policy ModelNamePolicy --model=ModelName
□ NovaServiceProvider::mainMenu() 添加菜单项
□ Dashboard 保留 Main::class (禁止删除, 否则首页 404)
□ Policy: viewAny/view/update => $user->is_admin, create/delete/restore/forceDelete => false
□ Factory definition() 补充字段 (make:model --all 生成的是空的)
□ Seeder 补充初始数据 (配置表必须 seed)
□ DatabaseSeeder 中调用新 Seeder
□ Factory 去重重复 use (make:model --all 已知 Bug)
```

## 标准结构

```php
class SynthesisOrder extends Resource
{
    public static $model = \App\Models\SynthesisOrder::class;
    public static function label(): string { return '合成订单'; }
    public static function singularLabel(): string { return '合成订单'; }
    public static $title = 'id';
    public static $search = ['id'];
    public static $sort = ['id' => 'desc'];
    // ... fields, cards, filters, actions
}
```

## Panel 分组规范

字段必须使用 Panel 分组, 禁止平铺:

```
订单类 Resource:
- 基本信息 (BelongsTo user, Badge status, Select status, 核心字段)
- 投入/收益信息 (金额/产出/释放相关)
- 时间信息 (start_at, end_at, created_at, updated_at, DateTime Y-m-d H:i:s)
- 元数据 (Code::make('data')->json())
- 关联记录 (HasMany releaseLogs 等)

配置类 Resource:
- 基本信息 (核心配置字段)
- 费用设置 (费率/限额)
- 元数据 + 时间信息
```

## 字段配置

- 金额: `Number::make()->step(0.00000001)->readonly()`
- 状态(index): `Badge::make()` + map/labels + `->filterable()` + `->onlyOnIndex()`
- 状态(detail): `Select::make()` + enum options + `->filterable()` + `->hideFromIndex()`
- 用户关联: `BelongsTo::make('用户', 'user', User::class)->searchable()->sortable()->filterable()->readonly()`
- JSON元数据: `Code::make('data')->json()->hideFromIndex()`
- 时间: `DateTime::make()->displayUsing(fn($v) => $v?->format('Y-m-d H:i:s'))`
- **所有枚举/状态/类型字段必须加 `->filterable()`**, 禁止遗漏

## 状态 Badge

```php
Badge::make('状态', 'status')
    ->map([
        OrderStatus::ACTIVE->value => 'success',
        OrderStatus::COMPLETED->value => 'info',
        OrderStatus::CANCELLED->value => 'danger',
    ])
    ->labels([
        OrderStatus::ACTIVE->value => OrderStatus::ACTIVE->name(),
        OrderStatus::COMPLETED->value => OrderStatus::COMPLETED->name(),
    ])
    ->sortable()
    ->onlyOnIndex(),
```

## 统计卡片(Metrics)设计

**原则: 首页放总览, 资源页面放细分, 禁止重复.**

首页 Dashboard:
- 用户统计: 用户总数, 新增用户趋势
- 资产总览: 6种资产余额 (基于 asset_snapshots 最新日)
- 订单总览: 合成总产出, 质押总金额, 提现总金额

资源页面卡片示例:
- SynthesisOrder: 已释放总量, 进行中/已完成订单数
- StakeOrder: 180天/360天质押总额, 已释放收益
- WithdrawOrder: 待处理笔数, 手续费总收入, 按资产分类提现额
- Trade: 交易总笔数, 按类型金额统计
- ReleaseLog: 释放总金额, 今日释放额, 按类型分类

## Action 设计

互斥操作(启用/禁用, 冻结/解冻)必须合并为一个 Action, 通过 Select 切换目标状态, 禁止拆成两个独立 Action.

参考 `ChangeUserStatus`: 一个 Action + Select 字段选择目标状态.

### 挂载到 Resource

```php
// app/Nova/User.php
public function actions(NovaRequest $request): array
{
    $actions = [
        new Actions\ChangeUserStatus,
    ];

    // 非生产环境才允许手动调整余额
    if (! app()->isProduction()) {
        $actions[] = new Actions\AdjustUserBalance;
    }

    return $actions;
}
```

### AdjustUserBalance 安全守卫

- Action 内部必须 `throw_if(app()->isProduction(), '生产环境禁止手动调整余额')`
- Resource 挂载时也要用 `app()->isProduction()` 控制是否显示
- 双重保护: 生产环境 Action 不显示 + 即使绕过前端也无法执行

## 调度命令规范

`routes/console.php` 中每个调度必须:
- 中文注释说明用途
- `appendOutputTo()` 输出到独立日志文件
- `withoutOverlapping()` + `onOneServer()`

```php
// 合成矿机每日释放
Schedule::command('release:synthesis')
    ->dailyAt('00:05')
    ->withoutOverlapping()
    ->onOneServer()
    ->appendOutputTo(storage_path('logs/release_synthesis.log'));
```

## 禁止事项

- 禁止删除 Dashboard 的 Main::class 引用 (首页 404)
- 禁止 Policy viewAny 返回 false (资源不显示)
- 禁止只创建 Resource 不创建 Policy/不更新菜单
- 禁止订单类资源允许后台 create (Policy create = false)
- 禁止首页与资源页面统计卡片重复
- 禁止字段不使用 Panel 分组直接平铺
- 禁止枚举/状态/类型字段不加 `->filterable()` (用字段自带 filterable, 不需要新建 Filter 类)

## 创建后验证

每个 Nova Resource 创建完成后, 必须逐项检查:

- [ ] `NovaServiceProvider` 顶部 `use` 导入已添加
- [ ] `NovaServiceProvider::mainMenu()` 菜单项已添加到对应分组
- [ ] `Policy` 文件已创建 (`php artisan make:policy --model=Xxx`)
- [ ] Policy 权限正确: 日志类 `update=false`, 订单类 `create/delete=false`
- [ ] 后台访问该资源不报 403/404
- [ ] 现有 Dashboard 引用未被删除
- [ ] 所有枚举/状态/类型字段有 `->filterable()`
- [ ] `php artisan nova:check` 无报错 (如可用)
