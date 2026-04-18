# duckdb

DuckDB 数据库 MCP 插件, 通过 `duckdb_mcp` 社区扩展提供 SQL 查询能力.

## 工具列表

| 工具 | 功能 |
|------|------|
| `query` | 执行只读 SQL 查询 (支持 json/jsonl/csv/markdown) |
| `describe` | 获取表或查询的 schema 信息 |
| `list_tables` | 列出所有表 (可选包含视图) |
| `export` | 导出查询结果 (json/jsonl/csv/markdown) |
| `database_info` | 获取数据库完整信息 (表/视图/扩展) |

## 特性

- 支持 Parquet, CSV, JSON 等多种格式直接查询
- 支持远程数据源 (S3, HTTP)
- 只读模式, 安全无副作用

## 安装

需要安装 DuckDB 并加载 `duckdb_mcp` 扩展:

```sql
INSTALL duckdb_mcp FROM community;
LOAD duckdb_mcp;
```

插件通过 `.mcp.json` 配置, 使用 DuckDB 内置 MCP 服务器.
