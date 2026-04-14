# 前端设计详细规范

## 目录结构

```
resources/js/
  types/           # 共享类型定义
    asset.ts       # 资产相关类型
    trade.ts       # 交易相关类型
  constants/       # 共享常量/mock数据
    assets.ts      # 资产注册表 (颜色/图标/名称)
  components/
    {feature}/     # 功能模块组件
      *.tsx
  pages/
    {feature}/     # Inertia页面
      *.tsx
  layouts/
    {feature}/     # 布局组件
      *-layout.tsx
```

## 组件拆分原则

- **页面组件** (`pages/`): 只做数据获取和布局组合, 不含业务逻辑
- **展示组件** (`components/`): 只接收 props, 不含 mock 数据
- **共享数据**: 抽取到 `constants/` 或 `types/`, 多组件引用同一数据源

## Mock 数据规范

mock 数据集中定义在一个文件, 多组件引用同一数据源, 禁止在多个组件中重复定义相同的 mock 数据数组.

```typescript
// constants/assets.ts - 唯一数据源
export const ASSETS = [
  { symbol: 'CY1173', name: 'CY1173', color: 'bg-amber-500', ... },
  { symbol: 'TOKEN', name: '1173', color: 'bg-purple-500', ... },
] as const;
```

```typescript
// components/wallet/asset-list.tsx - 引用
import { ASSETS } from '@/constants/assets';
```

## Inertia 页面规范

### 页面结构

```typescript
// pages/wallet/page-name.tsx
import WalletLayout from '@/layouts/wallet-layout';
import { Head } from '@inertiajs/react';

export default function PageName() {
    return (
        <>
            <Head title="页面标题 - 1173融合生态" />
            {/* 页面内容 */}
        </>
    );
}

PageName.layout = (page: React.ReactNode) => <WalletLayout>{page}</WalletLayout>;
```

### Props 类型

页面 props 必须定义接口, 与后端 Inertia::render() 传递的数据对齐:

```typescript
interface PageProps {
    symbol: string;
    balance: string;
}
export default function PageName({ symbol, balance }: PageProps) { ... }
```

## 类型定义

共享类型定义在 `resources/js/types/` 目录:

```typescript
// types/asset.ts
export interface AssetInfo {
    symbol: string;
    name: string;
    color: string;
    balance: string;
    value: string;
}
```

## CSS主题切换

使用 CSS class 切换主题, 禁止通过 JS 操作 `document.documentElement.style`:

```typescript
// 正确: 使用CSS class
useEffect(() => {
    document.documentElement.classList.add('cyberpunk-theme');
    return () => document.documentElement.classList.remove('cyberpunk-theme');
}, []);

// 禁止: 通过JS逐个设置CSS变量
// root.style.setProperty('--background', '...');
```

CSS 中定义主题变量:

```css
.cyberpunk-theme {
    --background: oklch(0.12 0.06 280);
    /* ... */
}
```

## 禁止事项

- 禁止多个文件重复定义相同的 mock 数据数组
- 禁止通过 JS 操作 CSS 变量 (应使用 CSS class)
- 禁止页面组件内嵌大量 mock 数据 (应抽取到 constants/)
- 禁止 `getAssetIcon()` 等工具函数内部每次创建新对象 (应提升为模块级常量)
- 禁止 `<Link>` 不加 `className="block"` 就使用 `space-y-*` 布局 (Link 渲染为 inline `<a>`)
