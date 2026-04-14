# API控制器设计详细规范

## 路由注册

路由定义在 `routes/api.php`, 使用 RESTful 风格:

```php
Route::middleware(['auth:sanctum'])->group(function () {
    Route::apiResource('synthesis-orders', SynthesisOrderController::class);
});
```

## 表单验证

使用 Form Request 类, 禁止在 Controller 中内联验证.

`php artisan make:model --all` 已自动创建 Form Request, 规则定义在 `rules()` 方法中:

```php
public function rules(): array
{
    return [
        'multiple' => ['required', 'integer', 'min:1'],
        'amount' => ['required', 'numeric', 'gt:0'],
    ];
}
```

检查项目中现有 Form Request 使用 array 还是 string 格式的验证规则, 保持一致.

## Controller 组织

### 标准方法

```
index()    - 列表 (分页/筛选/排序)
store()    - 创建
show()     - 详情
update()   - 更新
destroy()  - 删除
```

### 资金操作方法

涉及资金变动的方法必须:
1. 使用 `DB::transaction()` 包裹
2. 使用 `lockForUpdate()` 防止并发
3. 记录 before/after 余额
4. 写入 Trade 流水
5. 在 `data` 中记录完整业务上下文

参考 `User::recharge()` 和 `User::withdraw()` 的实现模式.

## Eloquent Resource

API 响应使用 Eloquent Resource 格式化:

```php
return ModelNameResource::collection($items);
```

## 响应格式

统一使用项目已有的响应格式, 检查项目中是否有全局响应辅助函数.

## 权限控制

检查项目中现有的认证/授权模式:
- `auth:sanctum` 中间件用于 API 认证
- Policy 类控制资源权限
- 检查 `$this->authorize()` 在 Controller 中的使用方式
