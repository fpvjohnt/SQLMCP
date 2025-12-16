# Changelog

## Version 2.1.0 - 2025-12-11

### Added: CSV Export Tool - Bypass Claude Desktop Limits

**Feature:** New `export_to_csv` tool that writes query results directly to disk, completely bypassing Claude Desktop's display limitations.

**Problem Solved:** Large query results were getting truncated/compacted in Claude Desktop, preventing CSV export.

#### New Tool: export_to_csv

**Parameters:**
- `sql` - SELECT query to execute
- `file_path` - Where to save CSV (e.g., C:\\Users\\NRJS\\exports\\data.csv)
- `max_rows` - Optional limit (default: unlimited)

**Features:**
- Handles unlimited rows (millions+)
- Direct disk write (no display in Claude)
- Auto-creates directories
- UTF-8 encoding
- Full logging and error handling
- Returns file size and row count

**Usage Examples:**
```
"Export all active users to C:\\Users\\NRJS\\exports\\users.csv"
"Export incidents from 2024 to CSV"
"Export 50000 records to C:\\exports\\data.csv"
```

**Benefits:**
- No more truncation issues
- Export datasets of any size
- Perfect for Excel, Python, reporting tools
- Automated and fast
- Same security as query_sql

See [CSV_EXPORT_GUIDE.md](CSV_EXPORT_GUIDE.md) for complete documentation.

---

## Version 2.0.1 - 2025-12-11

### Fixed: Network Binding for Remote Connections

**Issue:** Server was binding to 127.0.0.1 (localhost only), preventing Mac from connecting to Windows VM.

**Solution:** Changed default host binding to 0.0.0.0 to accept connections from any network interface.

#### Changes Made:

1. **Updated .env Configuration**
   - Changed `MCP_HOST=127.0.0.1` to `MCP_HOST=0.0.0.0`
   - Server now accepts connections from other machines

2. **Updated .env.example**
   - Added comments explaining host options
   - Documents both 0.0.0.0 (network) and 127.0.0.1 (local only)

3. **Created Network Setup Guide**
   - New file: NETWORK_SETUP.md
   - Complete guide for Mac-to-Windows VM setup
   - Firewall configuration instructions
   - Troubleshooting steps
   - Security considerations

### Server Binding

**Before:**
```
Server URL: http://127.0.0.1:8000/sse  ← Local only
```

**After:**
```
Server URL: http://0.0.0.0:8000/sse  ← All network interfaces
```

---

## Version 2.0.0 - 2025-12-11

### Fixed: MCP Output Validation

**Issue:** MCP tools were returning Python dictionaries instead of strings, causing validation errors.

**Solution:** Updated all tools to return JSON-formatted strings.

#### Changes Made:

1. **Added JSON Support**
   - Imported `json` module
   - Removed unused `Dict` and `Any` from typing imports

2. **Updated Return Types**
   - Changed all tool signatures from `-> Dict[str, Any]` to `-> str`
   - Updated docstrings to reflect JSON string returns

3. **Modified format_query_result()**
   - Now returns JSON string instead of dictionary
   - Uses `json.dumps(result, default=str, indent=2)` for proper formatting
   - The `default=str` parameter handles datetime and other non-serializable types

4. **Updated All Tool Functions (20+ tools)**
   - `query_sql()` - Returns JSON string
   - `execute_dml()` - Returns JSON string
   - `list_tables()` - Returns JSON string
   - `describe_table()` - Returns JSON string
   - `get_table_sample()` - Returns JSON string
   - `list_indexes()` - Returns JSON string
   - `get_index_fragmentation()` - Returns JSON string
   - `get_table_statistics()` - Returns JSON string
   - `get_active_sessions()` - Returns JSON string
   - `get_long_running_queries()` - Returns JSON string
   - `get_blocking_sessions()` - Returns JSON string
   - `get_wait_statistics()` - Returns JSON string
   - `get_database_info()` - Returns JSON string
   - `get_backup_history()` - Returns JSON string
   - `get_database_files()` - Returns JSON string

5. **Updated Error Returns**
   - All error returns now use `json.dumps()` for consistency
   - Format: `json.dumps({"error": error_msg, "timestamp": ...}, indent=2)`

6. **Fixed MCP Resources**
   - `resource_tables()` - Now parses JSON string from `list_tables()`
   - `resource_database_info()` - Now parses JSON string from `get_database_info()`

### Technical Details

**Before:**
```python
def query_sql(sql: str) -> Dict[str, Any]:
    # ...
    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows)
    }
```

**After:**
```python
def query_sql(sql: str) -> str:
    # ...
    result = {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows)
    }
    return json.dumps(result, default=str, indent=2)
```

### Benefits

1. **MCP Compliance:** All tools now return strings as required by MCP protocol
2. **Better Serialization:** The `default=str` parameter ensures datetime and decimal types serialize correctly
3. **Readable Output:** The `indent=2` parameter makes JSON output human-readable
4. **Consistent Format:** All tools follow the same return pattern

### Example Output

**Tool Response:**
```json
{
  "columns": [
    "schema_name",
    "table_name",
    "row_count",
    "total_space_mb"
  ],
  "rows": [
    ["dbo", "sys_user", 1500, 2.45],
    ["dbo", "incident", 8200, 15.32]
  ],
  "row_count": 2,
  "truncated": false,
  "timestamp": "2025-12-11T13:58:00.000000"
}
```

### Backward Compatibility

- Client code parsing responses will need to use `json.loads()` first
- MCP resources handle this automatically
- All functionality remains the same, only the return format changed

### Testing

Server successfully restarted with all changes:
- Process ID: 13592
- URL: http://127.0.0.1:8000/sse
- All 20+ tools validated
- Resources updated and tested

---

## Version 1.0.0 - 2025-12-11

Initial release with comprehensive SQL Server DBA features:
- 20+ database administration tools
- Security improvements (SQL injection protection, environment config)
- Comprehensive error handling and logging
- MCP resources and prompts
- Full documentation
