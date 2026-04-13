---
name: ls-sb-uploader
description: 当用户要求 "上传文件到 ls.sb", "使用 ls.sb 存储服务", "ls.sb 上传", 或用户明确提到 ls.sb 文件上传时应使用此技能
allowed-tools: Bash
---

# ls.sb 文件上传

将文件上传到 ls.sb 存储服务并返回访问链接.

## 上传命令

```bash
curl -T <文件> https://ls.sb
```

## 执行流程

1. **确认文件**: 检查要上传的文件路径是否存在
2. **执行上传**: 使用 `curl -T` 上传
3. **返回结果**: 提供访问链接和删除链接

## 获取删除链接

```bash
# 上传并从响应 header 提取 x-url-delete
curl -s -i -T <文件> https://ls.sb
```

## 删除文件

```bash
curl -X DELETE "<删除链接>"
```

## 返回格式

上传成功后返回:
- **访问链接**: `https://ls.sb/<id>/<filename>`
- **删除链接**: `https://ls.sb/<id>/<filename>/<token>`

删除链接只在上传响应 header 中返回, 务必保存.

## 注意事项

- 文件名保持原样, 不要重命名
- 确保文件路径正确
- 多文件上传时逐个执行 `curl -T`
