---
name: warn-eth-private-key
enabled: true
event: file
action: warn
conditions:
  - field: content
    operator: regex_match
    pattern: (private[_-]?key|eth[_-]?key|wallet[_-]?key).{0,10}0x[a-fA-F0-9]{64}|0x[a-fA-F0-9]{64}
---

**检测到可能的以太坊私钥!**

代码中存在疑似 ETH 私钥的内容:
- 私钥不应硬编码在代码中
- 使用环境变量或密钥管理器存储
- 确保私钥文件已加入 .gitignore
- 如已泄露, 立即转移资产并更换私钥
