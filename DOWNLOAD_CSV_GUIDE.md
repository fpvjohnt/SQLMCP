# Download CSV Directly to Your Mac - Quick Guide

## The Solution You Need

New `query_to_csv` tool that returns CSV data directly to Claude Desktop, which can then offer it as a download to your Mac. **No file needs to be saved on Windows VM first.**

## How It Works

```
Your Mac (Claude Desktop)
    ↓ Request data as CSV
Windows VM (MCP Server)
    ↓ Query database
    ↓ Generate CSV in memory
    ↓ Return CSV text to Claude
Claude Desktop
    ↓ Present as downloadable file
Your Mac Downloads folder ✅
```

## How to Use

### Simple - Just Ask Claude

**You say:**
> "Download the APTech 2025 incidents as CSV"

**Claude will:**
1. Call `query_to_csv` with your query
2. Get the CSV data back
3. Present it as a downloadable file
4. You click to save it to your Mac

### With Row Limit

> "Download the first 5000 incident records as CSV"

Claude will use:
```
query_to_csv(
  sql="SELECT * FROM incident...",
  max_rows=5000
)
```

### Specific Query

> "Download all active users with ID, name, and email as CSV"

Claude will:
```
query_to_csv(
  sql="SELECT user_id, name, email FROM sys_user WHERE active = 1",
  max_rows=10000
)
```

## Default Limits

**Default max_rows: 10,000**

Why? To prevent browser/Claude Desktop from hanging on massive datasets.

For larger datasets:
- **Option 1:** Use `export_to_csv` (saves to Windows VM, unlimited rows)
- **Option 2:** Download in chunks (see below)

## Examples

### Example 1: Download All Active Users
```
"Download all active users as CSV (limit 10000 rows)"
```

Result: CSV downloads directly to your Mac's Downloads folder

### Example 2: Download with Higher Limit
```
"Download 50,000 incident records as CSV"
```

```
query_to_csv(
  sql="SELECT * FROM incident ORDER BY sys_created_on DESC",
  max_rows=50000
)
```

### Example 3: Download Specific Columns
```
"Download user IDs and emails as CSV"
```

Result: Small, focused CSV with just the columns you need

## Comparison: Two CSV Tools

### query_to_csv (New - For Downloads)
```
✅ Downloads directly to your Mac
✅ Works through Claude Desktop
✅ No Windows file needed
✅ Perfect for datasets up to ~50K rows
✅ Immediate download
❌ Not ideal for millions of rows (browser limits)
```

### export_to_csv (For Large Exports)
```
✅ Handles unlimited rows (millions+)
✅ No browser/memory limits
✅ Saves to Windows VM
❌ Requires file transfer to Mac afterward
❌ Extra step to access file
```

## When to Use Which

| Scenario | Use This Tool | Why |
|----------|---------------|-----|
| Small to medium data (<50K rows) | `query_to_csv` | Direct download to Mac |
| Need it on Mac immediately | `query_to_csv` | No file transfer needed |
| Very large dataset (>50K rows) | `export_to_csv` | No browser limits |
| Automated daily exports | `export_to_csv` | Better for scripts |
| Ad-hoc analysis | `query_to_csv` | Quick and easy |

## Downloading Large Datasets in Chunks

For datasets larger than 50K rows, download in chunks:

**Chunk 1:**
```
"Download incidents 1-10000 as CSV WHERE incident_id BETWEEN 1 AND 10000"
```

**Chunk 2:**
```
"Download incidents 10001-20000 as CSV WHERE incident_id BETWEEN 10001 AND 20000"
```

Or by date:
```
"Download January 2025 incidents as CSV"
"Download February 2025 incidents as CSV"
```

Then combine the CSV files on your Mac.

## What You Get

When Claude calls `query_to_csv`, you get:

```json
{
  "success": true,
  "csv_content": "col1,col2,col3\nval1,val2,val3\n...",
  "rows": 5423,
  "columns": 12,
  "truncated": false,
  "instructions": "Claude Desktop can save this as a downloadable CSV file"
}
```

Claude will then:
1. Extract the `csv_content`
2. Present it as a downloadable file
3. You save it to your Mac

## Tips

### 1. Start Small
Test with small queries first:
```
"Download 100 sample incident records as CSV"
```

### 2. Use Filters
Reduce data size with WHERE clauses:
```
"Download 2024 high-priority incidents as CSV"
```

### 3. Select Specific Columns
Don't use `SELECT *` for large tables:
```
"Download incident number, description, and status as CSV"
```

### 4. Check Row Count First
Before downloading:
```
"How many records match my query?"
```

Then decide on row limit.

## Troubleshooting

### "Browser becomes unresponsive"
**Cause:** Too many rows
**Solution:** Reduce `max_rows` or use `export_to_csv`

### "CSV is truncated"
**Cause:** Hit the max_rows limit
**Solution:**
- Increase max_rows: `query_to_csv(..., max_rows=50000)`
- Or download in chunks
- Or use `export_to_csv` for unlimited

### "Takes too long"
**Cause:** Large query
**Solution:**
- Add WHERE clause to filter
- Use indexed columns in WHERE
- Reduce max_rows

## Quick Reference

### Download to Mac (up to ~50K rows)
```
"Download [data description] as CSV"
```
Tool used: `query_to_csv`

### Export to Windows VM (unlimited rows)
```
"Export [data description] to C:\\Users\\NRJS\\exports\\file.csv"
```
Tool used: `export_to_csv`

## Summary

**For your use case (download to Mac):**

1. **Restart MCP server** (to load new tool)
2. **Tell Claude:** "Download APTech 2025 incidents as CSV"
3. **Claude will:**
   - Query the database
   - Generate CSV
   - Present download button
4. **You click download** → File saves to your Mac

**No more "file not found" errors!** The CSV comes directly through Claude Desktop to your Mac.

## Try It Now

Restart your MCP server, then in Claude Desktop:

```
"Download the first 1000 incident records as CSV"
```

You should see Claude present a downloadable CSV file. Click it and it saves directly to your Mac's Downloads folder!
