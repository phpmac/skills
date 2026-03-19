---
name: ls-sb-uploader
description: Use when 用户要求上传文件到 ls.sb. 使用 curl -T 命令上传文件到 ls.sb 服务.
---

# ls.sb 上传工具

## 概述

将文件上传到 ls.sb 存储服务.

## 上传命令

```bash
curl -T <文件> https://ls.sb
```

## 使用方式

### 单文件上传

```bash
curl -T a.zip https://ls.sb
```

### 示例

```bash
# 上传 zip 文件
curl -T project.zip https://ls.sb

# 上传任意文件
curl -T anyfile.tar.gz https://ls.sb
```

## 返回

上传成功后会返回文件访问链接.
