# PoC编写规范

## 核心要素

PoC应包含以下核心要素:

| 要素 | 描述 | 示例 |
|------|------|------|
| **漏洞描述** | 什么漏洞,如何触发,影响范围 | SQL注入,通过id参数触发,影响user表 |
| **环境要求** | 运行PoC所需的环境和工具 | Docker,Python 3.9,requests库 |
| **检测方法** | 如何判断目标是否存在漏洞 | 响应包含特定错误信息或数据 |
| **利用逻辑** | 如何构造请求/数据触发漏洞 | 构造union select语句 |
| **结果验证** | 如何确认漏洞被成功利用 | 断言返回数据包含预期记录 |
| **修复验证** | 如何验证漏洞已修复 | 相同payload不再触发漏洞 |

## 设计原则

### 确定性
同一环境下多次执行结果一致

```python
# 好的做法: 使用固定种子和确定性断言
def test_sqli():
    payload = "1' UNION SELECT 1,2,3--"
    response = requests.get(url, params={"id": payload})
    assert "admin" in response.text  # 确定性断言
```

### 可复现
任何人在相同环境下都能复现

```python
# 好的做法: 完整的环境说明和依赖固定
# requirements.txt
requests==2.28.0
pytest==7.0.0

# docker-compose.yml
version: '3'
services:
  target:
    image: vulnerable-app:1.0
    ports:
      - "8080:80"
```

### 安全性
不对非目标系统造成影响

```python
# 好的做法: 限制影响范围
def test_idor():
    # 仅访问测试账户,不影响真实用户
    test_user_id = "test_user_123"
    response = requests.get(f"{base_url}/users/{test_user_id}")
```

### 最小化
仅包含触发漏洞的最小必要代码

```python
# 好的做法: 最小化payload
payload = "' OR 1=1--"  # 足够触发,不需要复杂构造

# 不好的做法: 过度复杂
payload = "' UNION SELECT username,password,email,phone,address,city FROM users WHERE admin=1 AND status='active' ORDER BY created_at DESC LIMIT 10--"
```

## PoC模板

### Web应用漏洞模板

```python
"""
漏洞: [漏洞名称]
目标: [目标URL/组件]
类型: [SQL注入/XSS/IDOR等]
"""

import requests
import pytest

BASE_URL = "http://localhost:8080"

class TestVulnerability:
    """漏洞验证测试"""

    def test_trigger_vulnerability(self):
        """触发漏洞"""
        # 1. 准备payload
        payload = "[payload内容]"

        # 2. 发送请求
        response = requests.get(
            f"{BASE_URL}/api/endpoint",
            params={"param": payload}
        )

        # 3. 验证漏洞触发
        assert response.status_code == 200
        assert "[预期特征]" in response.text

    def test_verify_impact(self):
        """验证影响"""
        # 证明漏洞的实际安全影响
        pass

    def test_fixed(self):
        """验证修复后不可利用"""
        # 在修复后的版本运行此测试应失败
        pass
```

### Solidity智能合约模板

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/VulnerableContract.sol";

contract VulnerabilityTest is Test {
    VulnerableContract target;

    function setUp() public {
        target = new VulnerableContract();
    }

    function testExploit() public {
        // 1. 记录初始状态
        uint256 initialBalance = address(target).balance;

        // 2. 执行攻击
        // ... 攻击逻辑 ...

        // 3. 验证漏洞利用成功
        assertGt(address(this).balance, initialBalance);
    }

    receive() external payable {} // 接收ETH
}
```

## 常见问题

### PoC不稳定
- 使用固定的测试数据
- 避免依赖网络请求
- 添加适当的等待和重试

### 环境差异
- 使用Docker固定环境
- 锁定依赖版本
- 记录完整的环境配置

### 难以验证
- 使用明确的断言条件
- 记录完整的响应数据
- 添加日志输出便于调试
