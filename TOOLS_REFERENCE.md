# SQL Server MCP Tools Reference

Quick reference guide for all available tools, organized by category.

## Query & Data Manipulation

### query_sql
Execute SELECT queries with validation and result formatting.

**Parameters:**
- `sql` (str) - The SQL SELECT query
- `max_rows` (int, optional) - Max rows to return (default: 1000)

**Returns:**
- columns, rows, row_count, truncated flag, timestamp

**Example:**
```
query_sql("SELECT TOP 10 * FROM sys_user ORDER BY sys_created_on DESC")
```

---

### execute_dml
Execute INSERT, UPDATE, or DELETE statements with transaction support.

**Parameters:**
- `sql` (str) - The DML statement

**Returns:**
- success, rows_affected, timestamp

**Example:**
```
execute_dml("UPDATE sys_user SET active = 0 WHERE user_name = 'test.user'")
```

---

## Schema Exploration

### list_tables
List all tables with row counts and space usage.

**Parameters:**
- `schema` (str, optional) - Schema filter (e.g., 'dbo')

**Returns:**
- schema_name, table_name, row_count, total_space_mb

**Example:**
```
list_tables()
list_tables(schema="dbo")
```

---

### describe_table
Get detailed table structure including columns, types, and constraints.

**Parameters:**
- `table_name` (str) - Name of the table
- `schema` (str) - Schema name (default: 'dbo')

**Returns:**
- column_name, data_type, max_length, precision, scale, is_nullable, is_identity, default_value, is_primary_key, is_foreign_key

**Example:**
```
describe_table("sys_user")
describe_table("sys_user", schema="dbo")
```

---

### get_table_sample
Preview sample rows from a table.

**Parameters:**
- `table_name` (str) - Name of the table
- `schema` (str) - Schema name (default: 'dbo')
- `limit` (int) - Number of rows (default: 10)

**Returns:**
- Sample data with all columns

**Example:**
```
get_table_sample("sys_user", limit=5)
```

---

## Index Management

### list_indexes
View all indexes with size and column information.

**Parameters:**
- `table_name` (str, optional) - Filter by table
- `schema` (str) - Schema name (default: 'dbo')

**Returns:**
- schema_name, table_name, index_name, index_type, is_unique, is_primary_key, index_columns, index_size_mb, row_count

**Example:**
```
list_indexes()
list_indexes(table_name="sys_user")
```

---

### get_index_fragmentation
Analyze index fragmentation and get maintenance recommendations.

**Parameters:**
- `table_name` (str, optional) - Filter by table
- `schema` (str) - Schema name (default: 'dbo')

**Returns:**
- schema_name, table_name, index_name, index_type_desc, avg_fragmentation_in_percent, page_count, recommendation (REBUILD/REORGANIZE/OK)

**Example:**
```
get_index_fragmentation()
get_index_fragmentation(table_name="sys_user")
```

**Recommendations:**
- >30% fragmentation: REBUILD
- 10-30% fragmentation: REORGANIZE
- <10% fragmentation: OK

---

## Performance Monitoring

### get_table_statistics
Comprehensive table statistics including space usage.

**Parameters:**
None

**Returns:**
- schema_name, table_name, row_count, total_space_mb, used_space_mb, unused_space_mb, last_stats_update

**Example:**
```
get_table_statistics()
```

---

### get_active_sessions
View active database connections and running queries.

**Parameters:**
None

**Returns:**
- session_id, login_name, host_name, program_name, status, cpu_time, memory_usage, total_elapsed_time, last_request_start_time, last_request_end_time, command, wait_type, wait_time, database_name, executing_query

**Example:**
```
get_active_sessions()
```

---

### get_long_running_queries
Find queries exceeding a duration threshold.

**Parameters:**
- `min_duration_seconds` (int) - Minimum duration (default: 10)

**Returns:**
- session_id, login_name, host_name, database_name, status, command, cpu_time, elapsed_seconds, wait_type, wait_time, blocking_session_id, query_text

**Example:**
```
get_long_running_queries()
get_long_running_queries(min_duration_seconds=30)
```

---

### get_blocking_sessions
Identify blocking chains and deadlock situations.

**Parameters:**
None

**Returns:**
- blocking_session_id, blocking_login, blocking_host, blocked_session_id, blocked_login, blocked_host, wait_type, wait_seconds, blocking_query, blocked_query

**Example:**
```
get_blocking_sessions()
```

---

### get_wait_statistics
Analyze wait types to identify performance bottlenecks.

**Parameters:**
None

**Returns:**
- wait_type, wait_time_seconds, waiting_tasks_count, avg_wait_time_seconds, max_wait_time_seconds, signal_wait_time_seconds

**Example:**
```
get_wait_statistics()
```

**Common Wait Types:**
- PAGEIOLATCH_*: Disk I/O bottleneck
- CXPACKET: Parallelism issues
- LCK_M_*: Locking/blocking
- WRITELOG: Transaction log bottleneck
- SOS_SCHEDULER_YIELD: CPU pressure

---

## Database Maintenance

### get_database_info
Database properties, size, and configuration.

**Parameters:**
None

**Returns:**
- database_name, database_id, compatibility_level, collation_name, state, recovery_model, page_verify, is_auto_close_on, is_auto_shrink_on, is_auto_create_stats_on, is_auto_update_stats_on, snapshot_isolation_state_desc, is_read_committed_snapshot_on, create_date, data_size_mb, log_size_mb

**Example:**
```
get_database_info()
```

---

### get_backup_history
View backup history with timing and size information.

**Parameters:**
- `days` (int) - Days to look back (default: 7)

**Returns:**
- database_name, backup_start_date, backup_finish_date, duration_seconds, backup_type, backup_type_desc, backup_size_mb, compressed_size_mb, physical_device_name, user_name, is_copy_only

**Example:**
```
get_backup_history()
get_backup_history(days=30)
```

**Backup Types:**
- D: Full backup
- I: Differential backup
- L: Transaction log backup

---

### get_database_files
File information including size and growth settings.

**Parameters:**
None

**Returns:**
- file_name, file_type, physical_name, size_mb, max_size, max_size_desc, growth, growth_desc, state

**Example:**
```
get_database_files()
```

---

## MCP Resources

### schema://tables
Resource endpoint listing all database tables in formatted text.

**Usage:**
Access via MCP resource protocol from Claude or other MCP clients.

---

### database://info
Resource endpoint with database information in formatted text.

**Usage:**
Access via MCP resource protocol from Claude or other MCP clients.

---

## MCP Prompts

### sql_query_helper
Assistance generating SQL queries from natural language.

**Parameters:**
- `query_description` (str) - Description of what you want to query

**Usage:**
Helps generate optimized SQL Server queries from plain English descriptions.

---

### performance_troubleshooting
Systematic performance troubleshooting guide.

**Parameters:**
None

**Usage:**
Provides step-by-step approach to diagnosing database performance issues.

---

### index_maintenance_plan
Index maintenance strategy and planning.

**Parameters:**
None

**Usage:**
Guides through creating a comprehensive index maintenance plan.

---

## Common DBA Workflows

### Daily Health Check
```
1. get_database_info() - Check database status
2. get_active_sessions() - Review active connections
3. get_blocking_sessions() - Look for blocking
4. get_backup_history(days=1) - Verify recent backups
```

### Performance Investigation
```
1. get_active_sessions() - See current activity
2. get_long_running_queries(min_duration_seconds=10) - Find slow queries
3. get_wait_statistics() - Identify bottlenecks
4. get_blocking_sessions() - Check for blocking
```

### Index Maintenance
```
1. get_index_fragmentation() - Check all indexes
2. Filter results where recommendation = 'REBUILD' or 'REORGANIZE'
3. Plan maintenance window
4. Execute maintenance (use execute_dml carefully)
```

### Space Management
```
1. get_table_statistics() - Review table sizes
2. get_database_files() - Check file growth
3. list_tables() - See space usage per table
```

### Schema Exploration
```
1. list_tables() - See all tables
2. describe_table("table_name") - Get structure
3. get_table_sample("table_name") - Preview data
4. list_indexes(table_name="table_name") - View indexes
```

---

## Security & Validation

### Allowed Operations
- SELECT (via query_sql)
- INSERT, UPDATE, DELETE (via execute_dml)
- Read-only system views and DMVs

### Blocked Operations
- DROP DATABASE
- DROP TABLE
- TRUNCATE
- xp_cmdshell (command execution)
- sp_executesql (dynamic SQL)
- SQL injection patterns
- Comment injection (--)

### Query Limits
- Default max rows: 1000 (configurable)
- Query timeout: 30 seconds (configurable)
- Connection timeout: 30 seconds (configurable)

---

## Return Format

All tools return structured dictionaries:

### Success Response
```json
{
  "columns": ["col1", "col2"],
  "rows": [[val1, val2], [val3, val4]],
  "row_count": 2,
  "truncated": false,
  "timestamp": "2025-12-11T13:30:00"
}
```

### Error Response
```json
{
  "error": "Error message here",
  "timestamp": "2025-12-11T13:30:00"
}
```

### DML Response
```json
{
  "success": true,
  "rows_affected": 5,
  "timestamp": "2025-12-11T13:30:00"
}
```

---

## Tips for Using Tools

1. **Start with read-only tools** - Use query_sql and schema tools first
2. **Check permissions** - Ensure you have necessary database permissions
3. **Review results** - Check row_count and truncated flag
4. **Monitor performance** - Use wait statistics for bottlenecks
5. **Plan maintenance** - Use fragmentation data for index maintenance
6. **Verify backups** - Regular backup history checks
7. **Watch for blocking** - Monitor active and blocking sessions
8. **Understand wait types** - Different waits indicate different problems

---

## Quick Reference by Use Case

### "I need to query data"
→ `query_sql()`

### "I need to modify data"
→ `execute_dml()`

### "What tables exist?"
→ `list_tables()`

### "What's in this table?"
→ `describe_table()` and `get_table_sample()`

### "Why is the database slow?"
→ `get_wait_statistics()`, `get_long_running_queries()`, `get_blocking_sessions()`

### "Which indexes need maintenance?"
→ `get_index_fragmentation()`

### "Are my backups running?"
→ `get_backup_history()`

### "What's using the most space?"
→ `get_table_statistics()`

### "Who's connected?"
→ `get_active_sessions()`

### "What's blocking what?"
→ `get_blocking_sessions()`
