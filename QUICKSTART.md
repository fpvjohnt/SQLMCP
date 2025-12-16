# Quick Start Guide

## 1. Verify Configuration

Your `.env` file is already set up with:
- Server: sndm.nordstrom.net
- Database: ServiceNow
- Authentication: Windows Trusted Connection
- Host: 127.0.0.1:8000

## 2. Start the Server

```bash
cd c:\Users\NRJS\mcp
venv\Scripts\python.exe sql_mcp_server.py
```

You should see:
```
INFO - Starting SQL Server DBA MCP Server
INFO - Database: ServiceNow on sndm.nordstrom.net
INFO - Host: 127.0.0.1:8000
```

## 3. Test the Server

Open another terminal and test with curl:

```bash
curl http://127.0.0.1:8000
```

## 4. Connect from Claude Desktop

Edit your Claude Desktop config:

**File Location:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Add this configuration:**

```json
{
  "mcpServers": {
    "sql-server-dba": {
      "command": "python",
      "args": ["c:\\Users\\NRJS\\mcp\\sql_mcp_server.py"],
      "env": {
        "PYTHONPATH": "c:\\Users\\NRJS\\mcp"
      }
    }
  }
}
```

## 5. Restart Claude Desktop

After saving the config file, restart Claude Desktop to load the MCP server.

## 6. Try Some Commands

Once connected, try these in Claude:

**Basic queries:**
```
"List all tables in the database"
"Show me the top 10 largest tables"
"Describe the structure of the sys_user table"
```

**Performance monitoring:**
```
"Show me active database sessions"
"Are there any blocking sessions?"
"What are the current wait statistics?"
```

**Index analysis:**
```
"Check index fragmentation"
"Which indexes need maintenance?"
```

**Database info:**
```
"Show database configuration"
"What backups have been taken this week?"
```

## Available Tools

### Query & Data
- `query_sql` - Run SELECT queries
- `execute_dml` - Run INSERT/UPDATE/DELETE
- `get_table_sample` - Preview table data

### Schema
- `list_tables` - List all tables
- `describe_table` - Table structure
- `list_indexes` - Index information

### Performance
- `get_active_sessions` - Active connections
- `get_long_running_queries` - Slow queries
- `get_blocking_sessions` - Blocking chains
- `get_wait_statistics` - Wait analysis
- `get_table_statistics` - Table stats
- `get_index_fragmentation` - Index health

### Maintenance
- `get_database_info` - Database config
- `get_backup_history` - Backup status
- `get_database_files` - File information

## Troubleshooting

**Server won't start:**
- Check database server is accessible
- Verify ODBC Driver 17 is installed
- Check credentials in `.env`

**Connection refused:**
- Ensure server is running
- Check firewall isn't blocking port 8000
- Verify host/port in `.env`

**Query errors:**
- Check database permissions
- Review query validation rules
- Check logs in `mcp_server.log`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review the available tools and their parameters
- Explore MCP resources and prompts
- Customize configuration in `.env` for your needs
