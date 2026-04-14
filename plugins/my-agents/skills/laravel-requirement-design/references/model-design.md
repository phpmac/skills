# 模型/数据库设计详细规范

## 表命名规范

- 表名使用复数蛇形命名: `synthesis_orders`, `stake_orders`
- 多词用下划线连接
- 关联表使用字母顺序: `announcement_tag`

## 字段命名规范

- 使用蛇形命名: `released_amount`, `daily_release`
- 布尔字段以 `is_` 开头: `is_admin`, `is_enabled`
- 日期字段以 `_at` 结尾: `start_at`, `end_at`, `signed_at`
- 日期字段(不含时间)以 `_date` 结尾: `release_date`
- 外键以 `_id` 结尾: `user_id`, `order_id`

## 必备字段

每张业务表必须包含:

```
id            bigint PK          主键
data          json nullable      元数据
timestamps                       created_at, updated_at
```

## 字段类型严谨性

### 金额/余额

- `decimal(20, 8)`: 应用层用 `bccomp()` 校验不允许为负数
- 必须有 `default(0)`: 余额类字段不允许 NULL
- 禁止 `nullable`: 余额为 0 不等于 NULL

### 数量/计数

- `unsignedInteger` / `unsignedBigInteger`: nft_count, direct_count 等计数字段
- 必须 `default(0)`

### 外键

- `foreignId()` 或 `unsignedBigInteger`: 与关联表 id 类型一致
- `constrained()` + `onDelete('cascade'/'set null')`: 必须声明删除策略

### 布尔

- `boolean`: 只有 true/false
- 禁止 `nullable`, 必须有明确 `default(true)` 或 `default(false)`

### 枚举

```php
// 正确: enum 列类型 + enum class
$table->enum('status', array_column(OrderStatus::cases(), 'value'))
    ->default(OrderStatus::ACTIVE->value)
    ->comment('状态');

// 禁止: string 存储枚举值
$table->string('status')->default('active');
```

## 索引设计

### 复合索引 (WHERE + ORDER BY)

```php
$table->index(['user_id', 'status', 'created_at'], 'trades_user_status_idx');
$table->index(['trade_type', 'created_at'], 'trades_type_created_idx');
```

索引命名: `{表名}_{字段组合}_idx`

### 唯一约束 (防重复)

```php
// 用户唯一标识
$table->string('address')->unique()->nullable();
$table->string('invite_code')->unique()->nullable();

// 防业务重复: 释放日志每天每订单只一条
$table->unique(['order_type', 'order_id', 'release_date'], 'release_unique');

// 配置唯一: 每种资产一条配置
$table->enum('asset_type', ...)->unique();

// Tree: 一个用户只有一条记录
$table->foreignId('user_id')->unique();
```

### 并发防重复唯一约束

涉及用户操作的业务表, 必须用 `(user_id + 类型字段 + created_at)` 做 unique 防止并发重复:

```php
// 交易记录: 防止同一用户同一资产同一类型同一秒重复
$table->unique(
    ['user_id', 'asset_type', 'trade_type', 'created_at'],
    'trades_concurrent_unique'
);

// 释放日志: 防止同一天重复释放
$table->unique(
    ['order_type', 'order_id', 'release_date'],
    'release_unique'
);
```

核心原则: 凡是可能被并发请求触发的写操作, 表级别必须有 unique 约束兜底.

## data 元数据追踪规范

涉及资金变动/状态变更/外部系统交互的表必须包含 `data` JSON 字段.

### 命名规则

- 关联ID: `stake_order_id`, `from_user_id`, `original_trade_id`
- 计算参数: `*_rate`, `base_amount`, `*_profit`
- 时间维度: `date`, `depth`, `release_date`
- 链上交互: `tx_hash`, `block_number`, `nonce`, `signature`, `deadline`

### Model 声明嵌套字段

```php
protected $fillable = [
    'data',
    'data->stake_order_id',
    'data->nonce',
];
```

## 枚举设计规范

```bash
php artisan make:enum OrderStatus
```

```php
enum OrderStatus: string
{
    case ACTIVE = 'active';
    case COMPLETED = 'completed';

    public function name(): string
    {
        return match ($this) {
            self::ACTIVE => (string) __('active'),
            self::COMPLETED => (string) __('completed'),
        };
    }
}
```

枚举必须有 `name()` 方法, 使用 `__()` 多语言.

## 关联关系

```php
public function user(): BelongsTo
{
    return $this->belongsTo(User::class);
}
```

## 迁移示例

```php
Schema::create('trades', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained()->onDelete('cascade');
    $table->enum('asset_type', array_column(AssetType::cases(), 'value'))->comment('资产类型');
    $table->enum('trade_type', array_column(TradeType::cases(), 'value'))->comment('交易类型');
    $table->decimal('amount', 20, 8)->comment('交易金额');
    $table->decimal('fee', 20, 8)->default(0)->comment('手续费');
    $table->decimal('before', 20, 8)->nullable()->comment('交易前余额');
    $table->decimal('after', 20, 8)->nullable()->comment('交易后余额');
    $table->enum('status', array_column(TradeStatus::cases(), 'value'))
        ->default(TradeStatus::SUCCESS->value)->comment('状态');
    $table->string('remark')->nullable()->comment('备注');
    $table->json('data')->nullable()->comment('元数据');
    $table->timestamps();

    $table->index(['user_id', 'status', 'created_at'], 'trades_user_status_idx');
    $table->index(['trade_type', 'created_at'], 'trades_type_created_idx');
});
```

## 创建后验证

每个模型创建完成后, 必须逐项检查:

- [ ] `User` 模型中注册了新关联 (`hasMany`/`belongsTo` 等)
- [ ] `Factory definition()` 已补充字段 (`make:model --all` 生成的是空的)
- [ ] `Factory` 顶部 `use` 去重 (`make:model --all` 已知Bug会导致重复)
- [ ] `Seeder` 补充初始数据 (配置表必须)
- [ ] `DatabaseSeeder` 中调用了新 Seeder
- [ ] Migration 字段与 Model `$fillable` 一一对应
- [ ] 金额字段 `decimal(20, 8)` + `default(0)` + 禁止 `nullable`
- [ ] 余额字段数据库层禁止为负数 (使用 `unsigned` 或应用层 `bccomp()` 校验)
