# 框架特定审计方法论

## 审计准备阶段

**核心原则**: 不了解框架就无法发现框架层面的漏洞

| 准备项 | 目的 | 关键问题 |
|--------|------|----------|
| **框架文档学习** | 理解标准用法和最佳实践 | 框架推荐的安全写法是什么? |
| **验证环境搭建** | 确保测试环境可复现 | 该技术栈用什么工具验证最合适? |
| **网络搜索CVE** | 发现框架本身的安全问题 | 该版本有哪些已知漏洞? |
| **依赖漏洞扫描** | 检查第三方组件安全 | 依赖是否存在已知CVE? |

## 强制要求: 网络搜索框架漏洞

**框架本身可能存在漏洞,必须通过网络搜索验证版本安全性.**

### 搜索流程

1. **确认精确版本**:
   - React/Next.js: 查看 `package.json`
   - Laravel: 查看 `composer.json`
   - ThinkPHP: 查看 `composer.json` 或 `version.php`

2. **搜索框架CVE**:
   ```
   "{框架名} {版本} vulnerability CVE"
   "{框架名} {版本} security advisory"
   "{框架名} {版本} exploit"
   ```

3. **检查官方安全公告**:
   - React: https://react.dev/blog (搜索 "security")
   - Next.js: https://github.com/vercel/next.js/security/advisories
   - Laravel: https://laravel.com/docs/releases
   - Express: https://expressjs.com/en/advanced/security-updates.html

### 各框架搜索示例

**React**:
```
"React 18 vulnerability"
"React 18 XSS CVE"
"react-dom security issue"
```

**Next.js**:
```
"Next.js 14 vulnerability CVE"
"Next.js server-side request forgery"
"Next.js middleware bypass"
```

**Laravel**:
```
"Laravel 10 CVE"
"Laravel security advisory 2024"
"Laravel validation bypass"
```

**ThinkPHP**:
```
"ThinkPHP 6 vulnerability"
"ThinkPHP RCE exploit"
"ThinkPHP SQL injection"
```

**FastAPI**:
```
"FastAPI security vulnerability"
"FastAPI dependency injection exploit"
"pydantic security issue"
```

### 依赖漏洞扫描

```bash
# Node.js 项目
npm audit
npm audit fix
yarn audit

# PHP 项目
composer audit
composer outdated

# Python 项目
pip-audit
safety check
```

## 框架审计核心思路

### 第一层: 框架知识储备

审计任何框架前,必须理解:
- **请求生命周期**: 请求如何进入,如何处理,如何响应
- **核心组件**: 路由,控制器,模型,中间件的工作机制
- **安全机制**: 框架提供的认证,授权,输入验证机制
- **标准写法**: 官方推荐的安全编码规范

### 第二层: 框架特定风险点

不同框架有不同的"危险区域":

| 框架类型 | 典型风险点 | 审计关注点 |
|----------|------------|------------|
| **React/Next.js** | SSR,API路由,客户端状态 | XSS,SSRF,hydration攻击 |
| **MVC框架(Laravel/ThinkPHP)** | 模型层数据操作,模板渲染 | ORM注入,模板注入,反序列化 |
| **异步框架(FastAPI/Express)** | 依赖注入,异步执行流,文件操作 | 参数污染,路径遍历,类型混淆 |

### 第三层: 历史漏洞模式

**必须检查的内容**:
- 当前使用的框架版本是否存在已知CVE (网络搜索)
- 项目是否应用了官方安全补丁
- 危险函数/方法的使用方式
- 框架特定的漏洞模式

**框架常见漏洞模式**:

| 框架 | 常见漏洞类型 | 检查方法 |
|------|--------------|----------|
| **React** | XSS (dangerouslySetInnerHTML) | 搜索 `dangerouslySetInnerHTML` |
| **Next.js** | SSRF, 信息泄露 | 检查 API 路由,Server Component |
| **Laravel** | 反序列化,SQL注入 | 检查 `unserialize`, 原始SQL |
| **ThinkPHP** | RCE,模板注入 | 检查版本CVE,模板语法 |
| **Express** | 原型污染,路径遍历 | 检查对象合并,路径拼接 |

## 业务逻辑漏洞审计思路

**核心方法: 对比标准写法与实际写法**

1. **识别业务场景**: 定位涉及资金,权限,数据变更的关键业务
2. **查找标准实现**: 框架官方文档推荐的安全实现方式
3. **对比实际代码**: 项目中的实现与标准实现的差异点
4. **分析差异风险**: 差异是否引入了安全漏洞

**典型业务风险点**:

| 业务场景 | 审计思路 | 常见漏洞 |
|----------|----------|----------|
| **资金操作** | 检查金额验证逻辑 | 负数金额,精度丢失,并发竞争 |
| **权限控制** | 检查鉴权粒度 | 水平越权,垂直越权,未授权访问 |
| **数据操作** | 检查输入验证 | 类型混淆,格式绕过,注入攻击 |
| **批量操作** | 检查限制机制 | 批量越权,资源耗尽,条件竞争 |

**数据库结构审计**:
- 字段类型是否与业务逻辑匹配(如金额字段类型)
- 约束条件是否完整(外键,唯一性,非空)
- 索引是否合理(影响查询性能和拖库风险)

## 框架版本与漏洞关系

**关键原则**: 框架版本决定漏洞是否存在

审计时必须:
1. **确认精确版本**: 不能只知道是大版本(如Next.js 14),必须知道小版本(如14.1.0)
2. **网络搜索CVE**: 使用搜索工具查询该版本的已知漏洞
3. **验证漏洞修复**: 项目是否应用了补丁或规避了漏洞
4. **检查依赖传递**: 框架依赖的组件版本是否安全

## 前端框架特殊审计点

### React 审计

```javascript
// 危险: 直接插入 HTML
<div dangerouslySetInnerHTML={{__html: userInput}} />

// 危险: 使用用户输入作为 href
<a href={userInput}>Link</a>  // 可能导致 javascript: 协议攻击

// 危险: 使用用户输入作为样式
<div style={userStyle} />  // 可能导致 CSS 注入
```

**检查清单**:
- [ ] 搜索所有 `dangerouslySetInnerHTML`
- [ ] 检查 `href` 是否验证协议
- [ ] 检查是否使用过时的生命周期方法

### Next.js 审计

```javascript
// 危险: Server Component 中直接使用用户输入
export default async function Page({ searchParams }) {
    const url = searchParams.url;  // 用户可控
    const data = await fetch(url);  // SSRF
}

// 危险: API 路由缺少鉴权
export default function handler(req, res) {
    // 缺少权限检查
    res.json(sensitiveData);
}
```

**检查清单**:
- [ ] 检查所有 API 路由是否有鉴权
- [ ] 检查 Server Component 是否有 SSRF 风险
- [ ] 检查环境变量是否泄露到客户端
- [ ] 搜索该 Next.js 版本的已知 CVE

## 审计流程 (强制顺序)

```
+----------------------------------+
| 1. 版本确认与网络搜索 (必须)     |
|    - 确认框架精确版本            |
|    - 网络搜索该版本 CVE          |
|    - 运行依赖扫描 (npm audit)    |
+---------------+------------------+
                |
                v
+----------------------------------+
| 2. 框架文档学习                  |
|    - 理解标准安全写法            |
|    - 了解框架安全机制            |
+---------------+------------------+
                |
                v
+----------------------------------+
| 3. 代码差异分析                  |
|    - 对比标准写法与实际写法      |
|    - 识别业务逻辑漏洞点          |
+---------------+------------------+
                |
                v
+----------------------------------+
| 4. 漏洞验证                      |
|    - 搭建测试环境                |
|    - 编写 PoC 验证               |
+---------------+------------------+
                |
                v
+----------------------------------+
| 5. 报告与修复验证                |
|    - 输出漏洞详情和修复建议      |
|    - 验证修复有效性              |
+----------------------------------+
```

**重要**: 框架版本搜索是强制步骤,跳过可能导致遗漏框架本身的漏洞.
