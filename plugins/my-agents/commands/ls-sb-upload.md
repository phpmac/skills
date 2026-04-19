---
description: 上传文件到 ls.sb 存储服务, 返回访问链接和删除链接
allowed-tools: Bash
---

## 规范

- 文件名保持原样, 不要重命名
- 确保文件路径正确
- 多文件上传时逐个执行

## 任务

1. 确认文件路径存在
2. 执行 `curl -s -i -T <文件> https://ls.sb`, 从响应 header 提取访问链接和 x-url-delete 删除链接
3. 输出访问链接和删除链接
