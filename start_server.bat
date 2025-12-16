@echo off
REM SQL Server MCP Server Startup Script

echo ================================================================
echo SQL Server Database Administration MCP Server
echo ================================================================
echo.
echo Starting server...
echo Server: sndm.nordstrom.net
echo Database: ServiceNow
echo Host: http://0.0.0.0:8000 (Accessible from network)
echo.
echo IMPORTANT: Server accepts connections from ANY machine
echo Make sure your firewall allows port 8000
echo.
echo Press Ctrl+C to stop the server
echo ================================================================
echo.

cd /d "%~dp0"
venv\Scripts\python.exe sql_mcp_server.py

pause
