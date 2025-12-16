# Network Setup Guide

## Connecting from a Different Machine

If you're running the MCP server on Windows and connecting from a Mac (or any other machine), you need to configure the server to accept network connections.

## Host Configuration

### Option 1: Accept All Network Connections (Default)
```env
MCP_HOST=0.0.0.0
```
- **Use Case:** Mac connecting to Windows VM
- **Security:** Less secure - server accepts connections from any machine
- **Requirement:** Firewall must allow port 8000

### Option 2: Local Only (More Secure)
```env
MCP_HOST=127.0.0.1
```
- **Use Case:** Claude Desktop running on the same Windows machine
- **Security:** More secure - only accepts local connections
- **Requirement:** Client must be on the same machine

## Current Configuration

Your server is now configured for **Option 1** (0.0.0.0), which allows your Mac to connect to the Windows VM.

## Steps to Connect from Mac to Windows VM

### 1. Start Server on Windows VM

```cmd
cd c:\Users\NRJS\mcp
venv\Scripts\python.exe sql_mcp_server.py
```

You should see:
```
Server URL: http://0.0.0.0:8000/sse
Uvicorn running on http://0.0.0.0:8000
```

### 2. Find Windows VM IP Address

On Windows, open Command Prompt and run:
```cmd
ipconfig
```

Look for your network adapter's IPv4 address, e.g., `192.168.1.100`

### 3. Test Connection from Mac

On your Mac, test the connection:
```bash
curl http://WINDOWS_VM_IP:8000
```

Replace `WINDOWS_VM_IP` with the actual IP address from step 2.

Example:
```bash
curl http://192.168.1.100:8000
```

### 4. Configure Claude Desktop on Mac

Edit Claude Desktop config on your Mac:

**File:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Content:**
```json
{
  "mcpServers": {
    "sql-server-dba": {
      "command": "curl",
      "args": [
        "-N",
        "-H", "Accept: text/event-stream",
        "http://WINDOWS_VM_IP:8000/sse"
      ]
    }
  }
}
```

Replace `WINDOWS_VM_IP` with your Windows VM's IP address.

### 5. Restart Claude Desktop

Close and reopen Claude Desktop on your Mac.

## Firewall Configuration

### Windows Firewall

You may need to allow incoming connections on port 8000:

1. Open **Windows Defender Firewall with Advanced Security**
2. Click **Inbound Rules** → **New Rule**
3. Select **Port** → Click **Next**
4. Select **TCP** and enter port **8000** → Click **Next**
5. Select **Allow the connection** → Click **Next**
6. Select all profiles (Domain, Private, Public) → Click **Next**
7. Name it "MCP Server" → Click **Finish**

**Or via Command Prompt (as Administrator):**
```cmd
netsh advfirewall firewall add rule name="MCP Server" dir=in action=allow protocol=TCP localport=8000
```

### Testing Firewall

From your Mac, test if port is open:
```bash
nc -zv WINDOWS_VM_IP 8000
```

Should show: `Connection to WINDOWS_VM_IP port 8000 [tcp/*] succeeded!`

## Troubleshooting

### Can't Connect from Mac

**Check 1: Server is Running**
On Windows, verify the server shows:
```
Uvicorn running on http://0.0.0.0:8000
```

**Check 2: Firewall Allows Port 8000**
```cmd
netsh advfirewall firewall show rule name="MCP Server"
```

**Check 3: Can Ping Windows VM**
From Mac:
```bash
ping WINDOWS_VM_IP
```

**Check 4: Port is Listening**
On Windows:
```cmd
netstat -an | findstr :8000
```

Should show:
```
TCP    0.0.0.0:8000    0.0.0.0:0    LISTENING
```

### Connection Refused

- Verify `.env` has `MCP_HOST=0.0.0.0`
- Restart the server after changing `.env`
- Check Windows Firewall settings

### Connection Times Out

- Check network connectivity between Mac and Windows
- Verify both are on the same network
- Check for VPN or network isolation

## Security Considerations

### Production Deployment

For production use, consider:

1. **Use HTTPS/TLS** - Encrypt traffic between machines
2. **Authentication** - Add API key or OAuth authentication
3. **IP Restrictions** - Only allow specific IPs to connect
4. **VPN** - Use a VPN for secure connections
5. **Monitoring** - Log all connection attempts

### Current Security Status

Your current setup:
- ✓ SQL injection protection enabled
- ✓ Query validation active
- ✓ Environment-based credentials
- ⚠ No encryption (HTTP only)
- ⚠ No authentication on MCP server
- ⚠ Accepts connections from any IP

**Recommendation:** Only use this on trusted networks (home network, corporate network with firewall).

## Network Diagram

```
┌─────────────────┐         Network         ┌──────────────────┐
│                 │    (192.168.1.x)        │                  │
│  Mac (Client)   │◄────────────────────────┤  Windows VM      │
│                 │                         │  (Server)        │
│  Claude Desktop │      Port 8000/TCP      │  MCP Server      │
│                 │                         │  0.0.0.0:8000    │
└─────────────────┘                         └──────────────────┘
                                                     │
                                                     │
                                            ┌────────▼────────┐
                                            │                 │
                                            │  SQL Server     │
                                            │  sndm.nordstrom │
                                            │  .net           │
                                            │                 │
                                            └─────────────────┘
```

## Quick Reference

| Configuration | Host Value | Use Case | Security |
|--------------|------------|----------|----------|
| Local Only | 127.0.0.1 | Same machine | High |
| Network Access | 0.0.0.0 | Different machines | Medium |
| Specific IP | 192.168.x.x | Bind to one interface | Medium |

## Your Current Setup

- **Windows VM:** Running MCP server on 0.0.0.0:8000
- **Mac:** Connecting via network to Windows VM IP
- **SQL Server:** sndm.nordstrom.net (ServiceNow database)

The server is now configured to accept connections from your Mac!
