---
name: laravel-requirement-design
description: 当用户要求 "设计需求", "开发新功能", "新建模型", "设计数据库", "创建API", "设计Nova后台", "拿到需求", "功能开发", 或需要将产品需求转化为Laravel技术方案时应使用此技能. 指导从需求分析到模型/API/Nova/前端/验证的完整设计流程.
---

# Laravel 需求设计流程

拿到新需求后, 按以下阶段依次设计, 每个阶段输出方案经人工确认后再进入下一阶段.

## 设计阶段

```
需求分析 -> 模型/数据库设计 -> API控制器设计 -> Nova后台设计 -> 前端设计 -> 完成验证
```

## 阶段一: 需求分析

明确以下内容后再进入设计:

1. **输入/输出**: 接收什么数据, 返回什么结果
2. **边界条件**: 数值范围, 状态流转, 异常场景
3. **验收标准**: 怎样算完成

### 安全检查清单

需求分析时必须逐项评估:

- [ ] 用户输入验证: 所有外部输入是否有类型/长度/范围校验
- [ ] 权限控制: 操作是否需要登录/管理员权限
- [ ] 敏感数据保护: 密钥/密码/私钥是否避免明文存储和日志输出
- [ ] 注入攻击防护: SQL/ XSS/ 命令注入防护措施
- [ ] 并发防重复: 高频操作是否有幂等/唯一约束保护
- [ ] 测试环境保护: 涉及资金操作是否有环境判断禁止测试环境执行

## 阶段二: 模型/数据库设计

详见 `references/model-design.md`.

### 创建命令

使用 Laravel artisan 命令创建文件, 禁止手动新建:

```bash
# 创建模型 (自动生成 migration/factory/seeder/policy/controller/form-request)
php artisan make:model --all ModelName

# 创建枚举
php artisan make:enum EnumName

# 修改现有表
php artisan make:migration add_fields_to_tablename_table
```

### 交付物

- 数据库字段表 (字段名/类型/默认值/说明)
- 枚举定义 (Case/Value/说明)
- 模型关系图
- data JSON 元数据字段规范

## 阶段三: API控制器设计

详见 `references/api-design.md`.

### 创建命令

```bash
# 创建表单验证 (make:model --all 已自动创建)
# 如需单独创建:
php artisan make:request StoreModelName
php artisan make:request UpdateModelName

# 创建API资源
php artisan make:resource ModelNameResource
```

### 交付物

- API路由表 (Method/Path/Controller@method)
- 表单验证规则
- 请求/响应示例
- 权限控制说明

## 阶段四: Nova后台设计

详见 `references/nova-design.md`.

### 创建命令

```bash
# 创建Nova Resource
php artisan nova:resource ModelName

# 创建Nova Action
php artisan nova:action ActionName

# 创建Nova Filter
php artisan nova:filter FilterName
```

### 交付物

- Resource字段配置
- 筛选器/动作
- 状态Badge配置
- 权限控制

## 阶段五: 前端设计

详见 `references/frontend-design.md`.

### 交付物

- 页面/组件文件列表
- 共享数据类型定义
- Mock数据集中管理方案

## 阶段六: 完成验证

每个阶段完成后进入此验证, 确保不遗漏.

### 交叉验证清单

- [ ] **模型 vs Migration**: 字段一一对应, 无遗漏
- [ ] **模型注册**: 新模型在 User 等关联模型中注册了关联关系
- [ ] **Nova完整**: Resource + Policy + 菜单 + Dashboard 四件套齐全
- [ ] **路由注册**: 新路由已添加到 routes/ 对应文件
- [ ] **格式化通过**: `pint --dirty` + `bun run a` 无报错
- [ ] **测试通过**: `php artisan test --compact` 核心路径无失败

## 关键原则

1. **逐阶段确认**: 每个阶段输出方案, 经人工确认后再执行下一步
2. **artisan优先**: 所有文件使用 artisan 命令创建, 禁止手动新建
3. **data元数据**: 涉及资金变动/状态变更的表必须包含 `data` JSON 字段
4. **枚举统一**: 状态/类型等固定取值字段必须用枚举, 禁止字符串硬编码
5. **参考同类**: 设计前先搜索项目中同类实现, 确保风格统一
6. **完成后自检**: 所有阶段完成后必须执行交叉验证清单

## 附加资源

### 参考文件

有关各阶段的详细规范, 请参阅:
- **`references/model-design.md`** - 模型/数据库设计详细规范
- **`references/api-design.md`** - API控制器设计详细规范
- **`references/nova-design.md`** - Nova后台设计详细规范
- **`references/frontend-design.md`** - 前端设计详细规范
