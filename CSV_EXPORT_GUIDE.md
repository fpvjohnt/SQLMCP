# CSV Export Guide - Bypass Claude Desktop Limits

## Problem Solved

When querying large datasets through Claude Desktop, the response gets truncated or compacted because of display/context limitations. This new `export_to_csv` tool writes query results directly to disk, completely bypassing Claude Desktop's display limits.

## New Tool: export_to_csv

### What It Does
- Executes your SQL query on the server
- Writes results directly to a CSV file on your Windows VM
- Handles unlimited rows (or specify a max)
- No data passes through Claude Desktop's display
- Perfect for large exports (millions of rows)

### Parameters

**sql** (required)
- Your SELECT query
- Same validation as `query_sql`
- SELECT only (no INSERT/UPDATE/DELETE)

**file_path** (required)
- Full path where CSV should be saved
- Windows format: `C:\\Users\\NRJS\\exports\\data.csv`
- Creates directories automatically if they don't exist

**max_rows** (optional)
- Maximum rows to export
- Default: `None` (exports all rows)
- Use for testing: `max_rows=1000`

### Returns

Success response:
```json
{
  "success": true,
  "file_path": "C:\\Users\\NRJS\\exports\\data.csv",
  "rows_exported": 150000,
  "file_size_bytes": 45000000,
  "file_size_mb": 42.91,
  "columns": ["col1", "col2", "col3"],
  "timestamp": "2025-12-11T15:30:00.000000"
}
```

## Usage Examples

### Example 1: Export All Records

**In Claude Desktop, simply say:**
> "Export all active users to C:\\Users\\NRJS\\exports\\users.csv"

Claude will use the tool like this:
```
export_to_csv(
  sql="SELECT * FROM sys_user WHERE active = 1",
  file_path="C:\\Users\\NRJS\\exports\\users.csv"
)
```

### Example 2: Export with Limit (for testing)

> "Export the first 5000 incident records to C:\\Users\\NRJS\\exports\\incidents.csv"

```
export_to_csv(
  sql="SELECT * FROM incident ORDER BY sys_created_on DESC",
  file_path="C:\\Users\\NRJS\\exports\\incidents.csv",
  max_rows=5000
)
```

### Example 3: Export with Filters

> "Export all incidents from 2024 to CSV"

```
export_to_csv(
  sql="SELECT * FROM incident WHERE YEAR(sys_created_on) = 2024",
  file_path="C:\\Users\\NRJS\\exports\\incidents_2024.csv"
)
```

### Example 4: Export Specific Columns

> "Export user ID, name, and email to CSV"

```
export_to_csv(
  sql="SELECT user_id, name, email FROM sys_user WHERE active = 1",
  file_path="C:\\Users\\NRJS\\exports\\user_emails.csv"
)
```

## Best Practices

### 1. Use Specific Export Directory

Create a dedicated exports folder:
```
C:\Users\NRJS\exports\
```

All your CSV files will go here, making them easy to find.

### 2. Use Descriptive Filenames

Good:
- `C:\\Users\\NRJS\\exports\\active_users_2025-12-11.csv`
- `C:\\Users\\NRJS\\exports\\incidents_high_priority.csv`

Bad:
- `C:\\Users\\NRJS\\data.csv`
- `C:\\Users\\NRJS\\output.csv`

### 3. Test with Small Queries First

Before exporting millions of rows:
```
export_to_csv(
  sql="SELECT TOP 100 * FROM large_table",
  file_path="C:\\Users\\NRJS\\exports\\test.csv"
)
```

### 4. Use Meaningful Column Selection

Instead of `SELECT *`, specify needed columns:
```sql
SELECT
    incident_number,
    short_description,
    priority,
    state,
    assigned_to,
    sys_created_on
FROM incident
```

This makes smaller, faster files.

### 5. Add Filters to Reduce Size

```sql
-- Instead of all records
SELECT * FROM incident

-- Filter to what you need
SELECT * FROM incident
WHERE state = 'Open'
  AND priority <= 3
  AND sys_created_on >= '2024-01-01'
```

## Performance Tips

### Large Exports (100K+ rows)

1. **Use ORDER BY for consistency:**
   ```sql
   SELECT * FROM table ORDER BY id
   ```

2. **Consider splitting into chunks:**
   - Export by date range
   - Export by category
   - Multiple smaller files are easier to work with

3. **Monitor during export:**
   - Watch log file: `mcp_server.log`
   - CSV appears immediately, grows as query runs

### Very Large Exports (1M+ rows)

1. **Add WHERE clauses to partition:**
   ```sql
   -- Export 2024 Q1
   export_to_csv(..., "WHERE sys_created_on >= '2024-01-01' AND sys_created_on < '2024-04-01'")

   -- Export 2024 Q2
   export_to_csv(..., "WHERE sys_created_on >= '2024-04-01' AND sys_created_on < '2024-07-01'")
   ```

2. **Check available disk space first**

3. **Consider using max_rows for initial test**

## Common Scenarios

### Scenario 1: Export for Excel Analysis

> "Export the last 10,000 incidents to CSV for Excel analysis"

Result: CSV opens directly in Excel with all data intact.

### Scenario 2: Export for Python Processing

> "Export all user data to CSV"

Result: CSV ready for pandas, data science workflows, etc.

### Scenario 3: Export for Reporting

> "Export monthly summary data to CSV"

Result: CSV ready for Power BI, Tableau, or reporting tools.

### Scenario 4: Export for Backup

> "Export all configuration items to CSV as backup"

Result: Full data backup in CSV format.

## Automation Ideas

### Schedule Regular Exports

You could create a Python script:
```python
import requests
import schedule
import time

def daily_export():
    # Call your MCP export_to_csv tool
    # Save with date in filename
    filename = f"C:\\exports\\daily_backup_{datetime.now():%Y%m%d}.csv"
    # ... export logic

schedule.every().day.at("02:00").do(daily_export)
```

### Batch Multiple Exports

In Claude Desktop:
> "Export these three datasets to separate CSV files:
> 1. All active users
> 2. All open incidents
> 3. All high-priority tasks"

Claude will call export_to_csv three times automatically.

## Troubleshooting

### Error: "Invalid file path"

**Cause:** Directory doesn't exist or invalid path format.

**Solution:**
- Use double backslashes: `C:\\Users\\NRJS\\exports\\file.csv`
- Or forward slashes: `C:/Users/NRJS/exports/file.csv`
- Directory will be created automatically if parent exists

### Error: "File I/O error: Permission denied"

**Cause:** File is open in Excel or another program.

**Solution:** Close the file and try again.

### Export is Slow

**Cause:** Very large dataset.

**Solutions:**
- Add WHERE clause to reduce rows
- Export in chunks by date/category
- Check network if database is remote

### CSV Opens Incorrectly in Excel

**Cause:** Special characters or encoding issues.

**Solution:**
- In Excel: Data → From Text/CSV → UTF-8
- CSV is UTF-8 encoded by default

## File Location Tips

### Default Locations

```
C:\Users\NRJS\exports\           ← Your exports
C:\Users\NRJS\Desktop\           ← Quick access
C:\Users\NRJS\Documents\data\    ← Organized
```

### Network Shares (if accessible)

```
\\networkshare\exports\data.csv
```

Just ensure the MCP server has write permissions.

## Comparison: Old Way vs. New Way

### Old Way (query_sql)
```
❌ Limited to 1000 rows (config default)
❌ All data passes through Claude Desktop display
❌ Large results get truncated
❌ Manual copy-paste to Excel
❌ Can't handle millions of rows
```

### New Way (export_to_csv)
```
✅ Unlimited rows (or specify max)
✅ Data writes directly to disk
✅ No truncation
✅ Opens directly in Excel/tools
✅ Can handle millions of rows
✅ Automated and fast
```

## Security Notes

- Same SQL injection protection as `query_sql`
- SELECT queries only (no data modification)
- Query validation applied
- File paths validated
- All operations logged

## Example Workflow

1. **Ask Claude to explore:**
   > "How many records are in the incident table?"

2. **Ask for a sample:**
   > "Show me 10 sample incident records"

3. **Export the full dataset:**
   > "Export all incidents from 2024 to C:\\Users\\NRJS\\exports\\incidents_2024.csv"

4. **Verify:**
   Claude confirms: "✅ Exported 45,230 rows (12.5 MB)"

5. **Use the file:**
   Open `C:\Users\NRJS\exports\incidents_2024.csv` in Excel

## Summary

The `export_to_csv` tool solves the "compacting/truncation" problem by:

1. Running query on the server (Windows VM)
2. Writing results directly to CSV file
3. Bypassing Claude Desktop entirely for data transfer
4. Returning only a summary to Claude

**Perfect for:**
- Large datasets (10K+ rows)
- Excel analysis
- Data science workflows
- Backup exports
- Automated reporting
- Any scenario where Claude's display is limiting you

**Just tell Claude:** "Export [your query description] to C:\\Users\\NRJS\\exports\\[filename].csv"

That's it! No more truncation or compacting issues.
