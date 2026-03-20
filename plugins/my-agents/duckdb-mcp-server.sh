#!/bin/bash
# DuckDB MCP Server wrapper
exec duckdb -c "
LOAD duckdb_mcp;
SELECT mcp_server_start('stdio');
"
