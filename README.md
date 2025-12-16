# SQL Server DBA MCP Server

A comprehensive Model Context Protocol (MCP) server for SQL Server database administration and querying. This server provides AI assistants with powerful tools to interact with SQL Server databases, perform administrative tasks, monitor performance, and manage database operations.

## Features

### Query Tools
- **query_sql** - Execute SELECT queries with validation and result formatting
- **execute_dml** - Execute INSERT, UPDATE, DELETE statements with transaction support

### Schema Exploration
- **list_tables** - List all tables with row counts and space usage
- **describe_table** - Get detailed table structure including columns, types, and constraints
- **get_table_sample** - Preview sample data from any table

### Index Management
- **list_indexes** - View all indexes with size and column information
- **get_index_fragmentation** - Analyze fragmentation and get maintenance recommendations

### Performance Monitoring
- **get_table_statistics** - Comprehensive table statistics including space usage
- **get_active_sessions** - View active database connections and running queries
- **get_long_running_queries** - Identify queries exceeding duration thresholds
- **get_blocking_sessions** - Find blocking chains and deadlock situations
- **get_wait_statistics** - Analyze wait types to identify performance bottlenecks

### Database Maintenance
- **get_database_info** - Database properties, size, and configuration settings
- **get_backup_history** - View backup history with timing and size information
- **get_database_files** - File information including size and growth settings
- **get_wait_statistics** - System-level wait analysis

### MCP Resources
- **schema://tables** - Resource endpoint listing all database tables
- **database://info** - Resource endpoint with database information

### MCP Prompts
- **sql_query_helper** - Assistance generating SQL queries from natural language
- **performance_troubleshooting** - Systematic performance troubleshooting guide
- **index_maintenance_plan** - Index maintenance strategy and planning

## Installation

### Prerequisites
- Python 3.8 or higher
- SQL Server with ODBC Driver 17 or higher
- Database access credentials

### Setup

1. Clone or download this repository:
```bash
cd c:\Users\NRJS\mcp
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file from the example:
```bash
copy .env.example .env
```

6. Edit `.env` with your database credentials:
```env
DB_SERVER=your_server_name
DB_DATABASE=your_database_name
DB_TRUSTED_CONNECTION=yes

# Or use SQL authentication
# DB_USERNAME=your_username
# DB_PASSWORD=your_password

MCP_HOST=127.0.0.1
MCP_PORT=8000
```

## Configuration

All configuration is managed through environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_DRIVER` | ODBC driver name | ODBC Driver 17 for SQL Server |
| `DB_SERVER` | SQL Server hostname | sndm.nordstrom.net |
| `DB_DATABASE` | Database name | ServiceNow |
| `DB_TRUSTED_CONNECTION` | Use Windows authentication | yes |
| `DB_USERNAME` | SQL Server username | - |
| `DB_PASSWORD` | SQL Server password | - |
| `MCP_HOST` | Server host address | 127.0.0.1 |
| `MCP_PORT` | Server port | 8000 |
| `MAX_ROWS` | Maximum rows to return | 1000 |
| `QUERY_TIMEOUT` | Query timeout in seconds | 30 |
| `LOG_LEVEL` | Logging level | INFO |
| `LOG_FILE` | Log file path | mcp_server.log |

## Usage

### Starting the Server

Run the MCP server:
```bash
python sql_mcp_server.py
```

The server will start on `http://127.0.0.1:8000` (or your configured host/port).

### Connecting from Claude Desktop

Add to your Claude Desktop configuration file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

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

### Example Queries

Once connected, you can ask Claude to perform database operations:

**Schema Exploration:**
```
"List all tables in the database"
"Describe the structure of the Users table"
"Show me a sample of data from the Orders table"
```

**Performance Monitoring:**
```
"Show me active database sessions"
"Find all queries running longer than 30 seconds"
"Check for blocking sessions"
"What are the top wait types?"
```

**Index Management:**
```
"List all indexes on the Products table"
"Check index fragmentation across all tables"
"Which indexes need maintenance?"
```

**Database Administration:**
```
"Show database configuration and size"
"What backups have been taken in the last 7 days?"
"Show me database file growth settings"
```

## Security Features

### SQL Injection Protection
- Query validation blocks dangerous patterns
- Prevents DROP DATABASE, TRUNCATE, and other destructive operations
- Blocks SQL injection attempts (comments, dynamic SQL)
- Separates read (SELECT) and write (DML) operations

### Connection Security
- Environment-based configuration (no hardcoded credentials)
- Local-only binding by default (127.0.0.1)
- Query timeout limits
- Proper connection cleanup with context managers

### Query Restrictions
- SELECT queries limited to `query_sql` tool
- DML operations (INSERT/UPDATE/DELETE) require `execute_dml` tool
- DDL operations (CREATE/ALTER/DROP) are blocked
- System stored procedures are blocked

## Database Administrator Features

This server is designed with DBA tasks in mind:

### Daily Operations
- Monitor active sessions and identify blocking
- Check backup status and history
- Review database file growth and space usage
- Identify long-running queries

### Performance Tuning
- Analyze wait statistics to find bottlenecks
- Review index fragmentation
- Monitor table statistics and space usage
- Track query execution patterns

### Maintenance Planning
- Index fragmentation analysis with recommendations
- Backup history and scheduling verification
- Database file growth monitoring
- Statistics update tracking

### Troubleshooting
- Identify blocking chains
- Find resource-intensive queries
- Analyze wait types and contention
- Review session activity

## Logging

All operations are logged to both console and file:
- Connection events
- Query executions
- Error conditions
- Security violations

Logs are written to `mcp_server.log` by default.

## Error Handling

The server provides comprehensive error handling:
- Database connection errors
- SQL execution errors
- Validation failures
- Timeout conditions

All errors are logged and returned in structured format with timestamps.

## Architecture

### Technology Stack
- **FastMCP**: MCP server framework
- **pyodbc**: SQL Server connectivity
- **python-dotenv**: Environment configuration
- **logging**: Comprehensive logging

### Design Patterns
- Context managers for resource cleanup
- Environment-based configuration
- Structured error responses
- Query validation layer
- Result formatting utilities

## Development

### Project Structure
```
mcp/
├── sql_mcp_server.py      # Main server file
├── .env                   # Configuration (not in git)
├── .env.example          # Configuration template
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── venv/                # Virtual environment
```

### Adding New Tools

To add a new tool, use the `@mcp.tool()` decorator:

```python
@mcp.tool()
def my_new_tool(param: str) -> Dict[str, Any]:
    """
    Tool description that will appear in MCP

    Args:
        param: Parameter description

    Returns:
        Dictionary with results
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Your logic here
            return {"result": "success"}
    except pyodbc.Error as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}
```

### Adding Resources

Add MCP resources for static information:

```python
@mcp.resource("myresource://endpoint")
def my_resource() -> str:
    """Resource description"""
    return "Resource content"
```

### Adding Prompts

Add prompts to help guide AI interactions:

```python
@mcp.prompt()
def my_prompt(context: str) -> str:
    """Prompt description"""
    return f"Prompt template with {context}"
```

## Troubleshooting

### Server Won't Start
- Check `.env` file exists and has correct values
- Verify database server is accessible
- Check ODBC driver is installed
- Review logs in `mcp_server.log`

### Connection Errors
- Verify server name and database name
- Check authentication method (Windows vs SQL)
- Ensure network connectivity to database
- Verify firewall allows SQL Server connections

### Query Validation Errors
- Review blocked patterns in `validate_sql_query()`
- Check for SQL injection attempts
- Ensure using correct tool (query_sql vs execute_dml)

## Limitations

- Read operations limited to MAX_ROWS (default 1000)
- Query timeout enforced (default 30 seconds)
- DDL operations are blocked for safety
- No support for running stored procedures directly
- Single database connection per query (no connection pooling yet)

## Future Enhancements

Potential improvements for future versions:
- Connection pooling for better performance
- Stored procedure execution support
- Query plan analysis tools
- Extended event monitoring
- Database comparison tools
- Schema migration helpers
- Query performance advisor
- Automated index tuning recommendations

## License

This project is provided as-is for database administration purposes.

## Contributing

To contribute improvements:
1. Test changes thoroughly
2. Update documentation
3. Follow existing code style
4. Add logging for new features
5. Include error handling

## Support

For issues or questions:
1. Check the logs in `mcp_server.log`
2. Review the troubleshooting section
3. Verify configuration in `.env`
4. Test database connectivity separately

## Version History

### Version 1.0.0 (Current)
- Initial release with comprehensive DBA tools
- 20+ database administration and monitoring tools
- SQL injection protection
- Environment-based configuration
- MCP resources and prompts
- Full logging support
- Performance monitoring capabilities
- Index management features
- Backup and maintenance tools
