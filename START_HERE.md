# START HERE - Quick Setup for Mac to Windows VM

## Current Configuration

Your server is configured to accept connections from your Mac to the Windows VM.

## Step 1: Start Server on Windows VM

Open Command Prompt on Windows and run:

```cmd
cd c:\Users\NRJS\mcp
venv\Scripts\python.exe sql_mcp_server.py
```

**Expected Output:**
```
Starting SQL Server DBA MCP Server
Database: ServiceNow on sndm.nordstrom.net
Host: 0.0.0.0:8000

Server URL: http://0.0.0.0:8000/sse  ← Should say 0.0.0.0, NOT 127.0.0.1
Uvicorn running on http://0.0.0.0:8000
```

✅ If you see `0.0.0.0` - You're ready to connect from Mac!
❌ If you see `127.0.0.1` - Server is local-only, Mac cannot connect

## Step 2: Find Windows VM IP Address

In Windows Command Prompt:
```cmd
ipconfig
```

Look for your IPv4 address, example: `192.168.1.100`

## Step 3: Test from Mac

On your Mac, open Terminal and test:
```bash
curl http://YOUR_WINDOWS_IP:8000
```

Example:
```bash
curl http://192.168.1.100:8000
```

If this works, you'll see a response. If it fails, see troubleshooting below.

## Step 4: Configure Firewall (If Needed)

If Step 3 fails, you may need to open the firewall on Windows.

**Quick Fix (Run as Administrator in Windows):**
```cmd
netsh advfirewall firewall add rule name="MCP Server" dir=in action=allow protocol=TCP localport=8000
```

## Step 5: Configure Claude Desktop on Mac

Edit this file on your Mac:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

Use the MCP server URL with your Windows IP:
```json
{
  "mcpServers": {
    "sql-server-dba": {
      "url": "http://YOUR_WINDOWS_IP:8000/sse"
    }
  }
}
```

Replace `YOUR_WINDOWS_IP` with the IP from Step 2.

## Step 6: Restart Claude Desktop

Close and reopen Claude Desktop on your Mac.

## Troubleshooting

### Server Shows 127.0.0.1 Instead of 0.0.0.0

Edit `.env` file and change:
```
MCP_HOST=0.0.0.0
```

Then restart the server.

### Connection Refused from Mac

1. Check Windows Firewall (Step 4)
2. Verify both machines are on same network
3. Try pinging Windows VM from Mac:
   ```bash
   ping YOUR_WINDOWS_IP
   ```

### Can't Find Windows IP

On Windows:
```cmd
ipconfig | findstr IPv4
```

### Still Not Working?

See the full guide: [NETWORK_SETUP.md](NETWORK_SETUP.md)

## Files Reference

- **Configuration:** `.env` (MCP_HOST=0.0.0.0)
- **Network Guide:** [NETWORK_SETUP.md](NETWORK_SETUP.md)
- **Full Docs:** [README.md](README.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

## Current Status

✅ Server configured for network access (0.0.0.0)
✅ All MCP tools returning JSON strings (v2.0.0 fix)
✅ 20+ database admin tools ready
✅ Ready to connect from Mac

**Next:** Start the server on Windows VM and configure Claude Desktop on Mac!
