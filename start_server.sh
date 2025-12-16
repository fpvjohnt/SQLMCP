#!/bin/bash
# SQL Server MCP Server Startup Script

echo "================================================================"
echo "SQL Server Database Administration MCP Server"
echo "================================================================"
echo ""
echo "Starting server..."
echo "Server: sndm.nordstrom.net"
echo "Database: ServiceNow"
echo "Host: http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================================"
echo ""

cd "$(dirname "$0")"
./venv/Scripts/python.exe sql_mcp_server.py
