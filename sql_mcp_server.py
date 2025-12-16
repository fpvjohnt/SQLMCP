"""
SQL Server Database Administration MCP Server

This MCP server provides comprehensive SQL Server database administration
and querying capabilities, including schema exploration, performance monitoring,
index management, and maintenance operations.
"""

import os
import re
import json
import csv
import io
import logging
from typing import List, Optional
from datetime import datetime
from contextlib import contextmanager

import pyodbc
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv("LOG_FILE", "mcp_server.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("SQL Server DBA Tool")

# Configuration
class Config:
    """Server configuration from environment variables"""
    DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    SERVER = os.getenv("DB_SERVER", "sndm.nordstrom.net")
    DATABASE = os.getenv("DB_DATABASE", "ServiceNow")
    TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "yes")
    USERNAME = os.getenv("DB_USERNAME")
    PASSWORD = os.getenv("DB_PASSWORD")
    MAX_ROWS = int(os.getenv("MAX_ROWS", "1000"))
    QUERY_TIMEOUT = int(os.getenv("QUERY_TIMEOUT", "30"))
    MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
    MCP_PORT = int(os.getenv("MCP_PORT", "8000"))

    @classmethod
    def get_connection_string(cls) -> str:
        """Build connection string from configuration"""
        parts = [
            f"DRIVER={{{cls.DRIVER}}}",
            f"SERVER={cls.SERVER}",
            f"DATABASE={cls.DATABASE}",
        ]

        if cls.TRUSTED_CONNECTION.lower() == "yes":
            parts.append("Trusted_Connection=yes")
        else:
            if cls.USERNAME and cls.PASSWORD:
                parts.append(f"UID={cls.USERNAME}")
                parts.append(f"PWD={cls.PASSWORD}")
            else:
                raise ValueError("Either use Trusted_Connection or provide USERNAME and PASSWORD")

        return ";".join(parts)


@contextmanager
def get_db_connection():
    """Context manager for database connections with proper cleanup"""
    conn = None
    try:
        conn = pyodbc.connect(
            Config.get_connection_string(),
            timeout=Config.QUERY_TIMEOUT
        )
        logger.info("Database connection established")
        yield conn
    except pyodbc.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")


def validate_sql_query(sql: str) -> bool:
    """
    Basic SQL validation to prevent dangerous operations.
    This is not foolproof but adds a layer of safety.
    """
    sql_upper = sql.upper().strip()

    # Block potentially dangerous commands
    dangerous_patterns = [
        r'\bDROP\s+DATABASE\b',
        r'\bDROP\s+TABLE\b',
        r'\bTRUNCATE\b',
        r'\bDELETE\s+FROM\b.*WHERE\s+1\s*=\s*1',
        r'\bUPDATE\b.*WHERE\s+1\s*=\s*1',
        r';\s*DROP\b',  # SQL injection attempt
        r'--',  # Comment injection
        r'xp_cmdshell',  # Command execution
        r'sp_executesql',  # Dynamic SQL
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, sql_upper):
            logger.warning(f"Blocked potentially dangerous SQL pattern: {pattern}")
            return False

    return True


def format_query_result(columns: List[str], rows: List[tuple], max_rows: int = None) -> str:
    """Format query results into a JSON string"""
    max_rows = max_rows or Config.MAX_ROWS

    result = {
        "columns": columns,
        "rows": [list(row) for row in rows[:max_rows]],
        "row_count": len(rows),
        "truncated": len(rows) > max_rows,
        "timestamp": datetime.now().isoformat()
    }

    return json.dumps(result, default=str, indent=2)


# ============================================================================
# QUERY TOOLS
# ============================================================================

@mcp.tool()
def query_sql(sql: str, max_rows: Optional[int] = None) -> str:
    """
    Execute a SELECT SQL query and return results.

    Args:
        sql: The SQL SELECT query to execute
        max_rows: Maximum number of rows to return (default from config)

    Returns:
        JSON string with columns, rows, row_count, truncated flag, and timestamp
    """
    try:
        if not validate_sql_query(sql):
            return json.dumps({
                "error": "Query validation failed. Potentially unsafe SQL detected.",
                "timestamp": datetime.now().isoformat()
            }, indent=2)

        # Only allow SELECT queries for safety
        if not sql.strip().upper().startswith('SELECT'):
            return json.dumps({
                "error": "Only SELECT queries are allowed. Use execute_dml for INSERT/UPDATE/DELETE.",
                "timestamp": datetime.now().isoformat()
            }, indent=2)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)

            if cursor.description is None:
                return json.dumps({"message": "Query executed successfully with no results"}, indent=2)

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows)
            # Parse to get row count for logging
            result_dict = json.loads(result_json)
            logger.info(f"Query executed successfully. Returned {result_dict['row_count']} rows")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


@mcp.tool()
def execute_dml(sql: str) -> str:
    """
    Execute a DML statement (INSERT, UPDATE, DELETE) with transaction support.

    Args:
        sql: The DML SQL statement to execute

    Returns:
        JSON string with execution status and rows affected
    """
    try:
        if not validate_sql_query(sql):
            return json.dumps({
                "error": "Query validation failed. Potentially unsafe SQL detected.",
                "timestamp": datetime.now().isoformat()
            }, indent=2)

        sql_upper = sql.strip().upper()
        allowed_commands = ['INSERT', 'UPDATE', 'DELETE']

        if not any(sql_upper.startswith(cmd) for cmd in allowed_commands):
            return json.dumps({
                "error": f"Only {', '.join(allowed_commands)} statements are allowed.",
                "timestamp": datetime.now().isoformat()
            }, indent=2)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows_affected = cursor.rowcount
            conn.commit()

            logger.info(f"DML executed successfully. {rows_affected} rows affected")
            return json.dumps({
                "success": True,
                "rows_affected": rows_affected,
                "timestamp": datetime.now().isoformat()
            }, indent=2)

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


@mcp.tool()
def export_to_csv(sql: str, file_path: str, max_rows: Optional[int] = None) -> str:
    """
    Execute a SELECT query and export results directly to a CSV file on disk.
    This bypasses Claude Desktop's display limits for large datasets.

    Args:
        sql: The SQL SELECT query to execute
        file_path: Full path where CSV should be saved (e.g., C:\\Users\\NRJS\\exports\\data.csv)
        max_rows: Maximum number of rows to export (default: unlimited, use None for all rows)

    Returns:
        JSON string with export status, file path, and row count
    """
    try:
        if not validate_sql_query(sql):
            return json.dumps({
                "error": "Query validation failed. Potentially unsafe SQL detected.",
                "timestamp": datetime.now().isoformat()
            }, indent=2)

        # Only allow SELECT queries for safety
        if not sql.strip().upper().startswith('SELECT'):
            return json.dumps({
                "error": "Only SELECT queries are allowed for CSV export.",
                "timestamp": datetime.now().isoformat()
            }, indent=2)

        # Validate file path
        try:
            export_dir = os.path.dirname(file_path)
            if export_dir and not os.path.exists(export_dir):
                os.makedirs(export_dir)
        except Exception as e:
            return json.dumps({
                "error": f"Invalid file path: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }, indent=2)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)

            if cursor.description is None:
                return json.dumps({
                    "error": "Query returned no results to export",
                    "timestamp": datetime.now().isoformat()
                }, indent=2)

            # Get column names
            columns = [col[0] for col in cursor.description]

            # Write to CSV
            rows_written = 0
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(columns)

                # Write data rows
                if max_rows:
                    for row in cursor.fetchmany(max_rows):
                        writer.writerow(row)
                        rows_written += 1
                else:
                    for row in cursor:
                        writer.writerow(row)
                        rows_written += 1

            file_size = os.path.getsize(file_path)
            logger.info(f"CSV export successful: {rows_written} rows written to {file_path}")

            return json.dumps({
                "success": True,
                "file_path": file_path,
                "rows_exported": rows_written,
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / 1024 / 1024, 2),
                "columns": columns,
                "timestamp": datetime.now().isoformat()
            }, indent=2)

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)
    except IOError as e:
        error_msg = f"File I/O error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


@mcp.tool()
def query_to_csv(sql: str, max_rows: Optional[int] = 10000) -> str:
    """
    Execute a SELECT query and return results as CSV text for download in Claude Desktop.
    Claude Desktop can present this as a downloadable file directly to your Mac.

    Args:
        sql: The SQL SELECT query to execute
        max_rows: Maximum number of rows to return (default: 10000 to prevent browser issues)

    Returns:
        JSON string containing CSV text and metadata that Claude can offer as download
    """
    try:
        if not validate_sql_query(sql):
            return json.dumps({
                "error": "Query validation failed. Potentially unsafe SQL detected.",
                "timestamp": datetime.now().isoformat()
            }, indent=2)

        # Only allow SELECT queries for safety
        if not sql.strip().upper().startswith('SELECT'):
            return json.dumps({
                "error": "Only SELECT queries are allowed for CSV download.",
                "timestamp": datetime.now().isoformat()
            }, indent=2)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)

            if cursor.description is None:
                return json.dumps({
                    "error": "Query returned no results to convert to CSV",
                    "timestamp": datetime.now().isoformat()
                }, indent=2)

            # Get column names
            columns = [col[0] for col in cursor.description]

            # Build CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(columns)

            # Write data rows
            rows_written = 0
            for row in cursor.fetchmany(max_rows):
                writer.writerow(row)
                rows_written += 1

            csv_content = output.getvalue()
            output.close()

            logger.info(f"CSV generation successful: {rows_written} rows")

            return json.dumps({
                "success": True,
                "csv_content": csv_content,
                "rows": rows_written,
                "columns": len(columns),
                "truncated": rows_written >= max_rows,
                "timestamp": datetime.now().isoformat(),
                "instructions": "Claude Desktop can save this as a downloadable CSV file"
            }, indent=2)

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


# ============================================================================
# SCHEMA EXPLORATION TOOLS
# ============================================================================

@mcp.tool()
def list_tables(schema: Optional[str] = None) -> str:
    """
    List all tables in the database, optionally filtered by schema.

    Args:
        schema: Optional schema name to filter (e.g., 'dbo')

    Returns:
        JSON string with table information including schema, name, and row counts
    """
    try:
        query = """
        SELECT
            s.name AS schema_name,
            t.name AS table_name,
            p.rows AS row_count,
            CAST(ROUND(((SUM(a.total_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS total_space_mb
        FROM
            sys.tables t
        INNER JOIN
            sys.schemas s ON t.schema_id = s.schema_id
        INNER JOIN
            sys.indexes i ON t.object_id = i.object_id
        INNER JOIN
            sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
        INNER JOIN
            sys.allocation_units a ON p.partition_id = a.container_id
        WHERE
            t.is_ms_shipped = 0
            AND i.index_id <= 1
        """

        if schema:
            query += f" AND s.name = '{schema}'"

        query += """
        GROUP BY
            s.name, t.name, p.rows
        ORDER BY
            s.name, t.name
        """

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows=None)
            result_dict = json.loads(result_json)
            logger.info(f"Listed {result_dict['row_count']} tables")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


@mcp.tool()
def describe_table(table_name: str, schema: str = "dbo") -> str:
    """
    Get detailed information about a table's structure, including columns, types, and constraints.

    Args:
        table_name: Name of the table
        schema: Schema name (default: 'dbo')

    Returns:
        Dictionary with column definitions, data types, constraints, and indexes
    """
    try:
        query = f"""
        SELECT
            c.name AS column_name,
            t.name AS data_type,
            c.max_length,
            c.precision,
            c.scale,
            c.is_nullable,
            c.is_identity,
            ISNULL(dc.definition, '') AS default_value,
            ISNULL(pk.is_primary_key, 0) AS is_primary_key,
            ISNULL(fk.is_foreign_key, 0) AS is_foreign_key
        FROM
            sys.columns c
        INNER JOIN
            sys.types t ON c.user_type_id = t.user_type_id
        LEFT JOIN
            sys.default_constraints dc ON c.default_object_id = dc.object_id
        LEFT JOIN (
            SELECT ic.object_id, ic.column_id, 1 AS is_primary_key
            FROM sys.index_columns ic
            INNER JOIN sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id
            WHERE i.is_primary_key = 1
        ) pk ON c.object_id = pk.object_id AND c.column_id = pk.column_id
        LEFT JOIN (
            SELECT fkc.parent_object_id, fkc.parent_column_id, 1 AS is_foreign_key
            FROM sys.foreign_key_columns fkc
        ) fk ON c.object_id = fk.parent_object_id AND c.column_id = fk.parent_column_id
        WHERE
            c.object_id = OBJECT_ID('{schema}.{table_name}')
        ORDER BY
            c.column_id
        """

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows=None)
            logger.info(f"Described table {schema}.{table_name}")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


@mcp.tool()
def get_table_sample(table_name: str, schema: str = "dbo", limit: int = 10) -> str:
    """
    Get a sample of rows from a table.

    Args:
        table_name: Name of the table
        schema: Schema name (default: 'dbo')
        limit: Number of rows to return (default: 10)

    Returns:
        Dictionary with sample data from the table
    """
    try:
        query = f"SELECT TOP {limit} * FROM {schema}.{table_name}"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows=limit)
            logger.info(f"Retrieved {limit} sample rows from {schema}.{table_name}")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


# ============================================================================
# INDEX MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
def list_indexes(table_name: Optional[str] = None, schema: str = "dbo") -> str:
    """
    List all indexes in the database or for a specific table.

    Args:
        table_name: Optional table name to filter indexes
        schema: Schema name (default: 'dbo')

    Returns:
        Dictionary with index information including type, columns, and statistics
    """
    try:
        query = """
        SELECT
            s.name AS schema_name,
            t.name AS table_name,
            i.name AS index_name,
            i.type_desc AS index_type,
            i.is_unique,
            i.is_primary_key,
            STUFF((
                SELECT ', ' + c.name
                FROM sys.index_columns ic
                INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
                WHERE ic.object_id = i.object_id AND ic.index_id = i.index_id
                ORDER BY ic.key_ordinal
                FOR XML PATH('')
            ), 1, 2, '') AS index_columns,
            ps.used_page_count * 8 / 1024.0 AS index_size_mb,
            ps.row_count
        FROM
            sys.indexes i
        INNER JOIN
            sys.tables t ON i.object_id = t.object_id
        INNER JOIN
            sys.schemas s ON t.schema_id = s.schema_id
        LEFT JOIN
            sys.dm_db_partition_stats ps ON i.object_id = ps.object_id AND i.index_id = ps.index_id
        WHERE
            t.is_ms_shipped = 0
        """

        if table_name:
            query += f" AND t.name = '{table_name}' AND s.name = '{schema}'"

        query += " ORDER BY s.name, t.name, i.name"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows=None)
            logger.info(f"Listed indexes")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


@mcp.tool()
def get_index_fragmentation(table_name: Optional[str] = None, schema: str = "dbo") -> str:
    """
    Analyze index fragmentation to identify indexes that need maintenance.

    Args:
        table_name: Optional table name to check
        schema: Schema name (default: 'dbo')

    Returns:
        Dictionary with fragmentation statistics for indexes
    """
    try:
        query = """
        SELECT
            OBJECT_SCHEMA_NAME(ips.object_id) AS schema_name,
            OBJECT_NAME(ips.object_id) AS table_name,
            i.name AS index_name,
            ips.index_type_desc,
            ips.avg_fragmentation_in_percent,
            ips.page_count,
            CASE
                WHEN ips.avg_fragmentation_in_percent > 30 THEN 'REBUILD'
                WHEN ips.avg_fragmentation_in_percent > 10 THEN 'REORGANIZE'
                ELSE 'OK'
            END AS recommendation
        FROM
            sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ips
        INNER JOIN
            sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
        WHERE
            ips.avg_fragmentation_in_percent > 0
            AND ips.page_count > 100
        """

        if table_name:
            query += f" AND OBJECT_NAME(ips.object_id) = '{table_name}' AND OBJECT_SCHEMA_NAME(ips.object_id) = '{schema}'"

        query += " ORDER BY ips.avg_fragmentation_in_percent DESC"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows=None)
            logger.info(f"Analyzed index fragmentation")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


# ============================================================================
# PERFORMANCE MONITORING TOOLS
# ============================================================================

@mcp.tool()
def get_table_statistics() -> str:
    """
    Get table statistics including row counts, space usage, and update dates.

    Returns:
        Dictionary with comprehensive table statistics
    """
    try:
        query = """
        SELECT
            s.name AS schema_name,
            t.name AS table_name,
            p.rows AS row_count,
            CAST(ROUND(((SUM(a.total_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS total_space_mb,
            CAST(ROUND(((SUM(a.used_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS used_space_mb,
            CAST(ROUND(((SUM(a.total_pages) - SUM(a.used_pages)) * 8) / 1024.00, 2) AS NUMERIC(36, 2)) AS unused_space_mb,
            STATS_DATE(t.object_id, i.index_id) AS last_stats_update
        FROM
            sys.tables t
        INNER JOIN
            sys.schemas s ON t.schema_id = s.schema_id
        INNER JOIN
            sys.indexes i ON t.object_id = i.object_id
        INNER JOIN
            sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
        INNER JOIN
            sys.allocation_units a ON p.partition_id = a.container_id
        WHERE
            t.is_ms_shipped = 0
            AND i.index_id <= 1
        GROUP BY
            s.name, t.name, t.object_id, i.index_id, p.rows
        ORDER BY
            total_space_mb DESC
        """

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows=None)
            logger.info(f"Retrieved table statistics")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


@mcp.tool()
def get_active_sessions() -> str:
    """
    Get information about active database sessions and connections.

    Returns:
        Dictionary with active session information including queries and wait times
    """
    try:
        query = """
        SELECT
            s.session_id,
            s.login_name,
            s.host_name,
            s.program_name,
            s.status,
            s.cpu_time,
            s.memory_usage,
            s.total_elapsed_time,
            s.last_request_start_time,
            s.last_request_end_time,
            r.command,
            r.wait_type,
            r.wait_time,
            DB_NAME(s.database_id) AS database_name,
            SUBSTRING(
                st.text,
                (r.statement_start_offset/2) + 1,
                ((CASE r.statement_end_offset
                    WHEN -1 THEN DATALENGTH(st.text)
                    ELSE r.statement_end_offset
                END - r.statement_start_offset)/2) + 1
            ) AS executing_query
        FROM
            sys.dm_exec_sessions s
        LEFT JOIN
            sys.dm_exec_requests r ON s.session_id = r.session_id
        OUTER APPLY
            sys.dm_exec_sql_text(r.sql_handle) st
        WHERE
            s.is_user_process = 1
            AND s.session_id != @@SPID
        ORDER BY
            s.last_request_start_time DESC
        """

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows=100)
            logger.info(f"Retrieved active sessions")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


@mcp.tool()
def get_long_running_queries(min_duration_seconds: int = 10) -> str:
    """
    Find long-running queries that exceed a specified duration.

    Args:
        min_duration_seconds: Minimum query duration in seconds (default: 10)

    Returns:
        Dictionary with information about long-running queries
    """
    try:
        query = f"""
        SELECT
            r.session_id,
            s.login_name,
            s.host_name,
            DB_NAME(r.database_id) AS database_name,
            r.status,
            r.command,
            r.cpu_time,
            r.total_elapsed_time / 1000 AS elapsed_seconds,
            r.wait_type,
            r.wait_time,
            r.blocking_session_id,
            SUBSTRING(
                st.text,
                (r.statement_start_offset/2) + 1,
                ((CASE r.statement_end_offset
                    WHEN -1 THEN DATALENGTH(st.text)
                    ELSE r.statement_end_offset
                END - r.statement_start_offset)/2) + 1
            ) AS query_text
        FROM
            sys.dm_exec_requests r
        INNER JOIN
            sys.dm_exec_sessions s ON r.session_id = s.session_id
        CROSS APPLY
            sys.dm_exec_sql_text(r.sql_handle) st
        WHERE
            r.total_elapsed_time / 1000 >= {min_duration_seconds}
        ORDER BY
            r.total_elapsed_time DESC
        """

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows=100)
            logger.info(f"Retrieved long-running queries")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


@mcp.tool()
def get_blocking_sessions() -> str:
    """
    Identify blocking sessions and what they're blocking.

    Returns:
        Dictionary with blocking chain information
    """
    try:
        query = """
        SELECT
            blocking.session_id AS blocking_session_id,
            blocking_s.login_name AS blocking_login,
            blocking_s.host_name AS blocking_host,
            blocked.session_id AS blocked_session_id,
            blocked_s.login_name AS blocked_login,
            blocked_s.host_name AS blocked_host,
            blocked.wait_type,
            blocked.wait_time / 1000 AS wait_seconds,
            SUBSTRING(
                blocking_st.text,
                (blocking_r.statement_start_offset/2) + 1,
                ((CASE blocking_r.statement_end_offset
                    WHEN -1 THEN DATALENGTH(blocking_st.text)
                    ELSE blocking_r.statement_end_offset
                END - blocking_r.statement_start_offset)/2) + 1
            ) AS blocking_query,
            SUBSTRING(
                blocked_st.text,
                (blocked.statement_start_offset/2) + 1,
                ((CASE blocked.statement_end_offset
                    WHEN -1 THEN DATALENGTH(blocked_st.text)
                    ELSE blocked.statement_end_offset
                END - blocked.statement_start_offset)/2) + 1
            ) AS blocked_query
        FROM
            sys.dm_exec_requests blocked
        INNER JOIN
            sys.dm_exec_sessions blocking ON blocked.blocking_session_id = blocking.session_id
        INNER JOIN
            sys.dm_exec_sessions blocked_s ON blocked.session_id = blocked_s.session_id
        INNER JOIN
            sys.dm_exec_sessions blocking_s ON blocking.session_id = blocking_s.session_id
        LEFT JOIN
            sys.dm_exec_requests blocking_r ON blocking.session_id = blocking_r.session_id
        CROSS APPLY
            sys.dm_exec_sql_text(blocked.sql_handle) blocked_st
        OUTER APPLY
            sys.dm_exec_sql_text(blocking_r.sql_handle) blocking_st
        WHERE
            blocked.blocking_session_id > 0
        ORDER BY
            blocked.wait_time DESC
        """

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows=100)
            logger.info(f"Retrieved blocking sessions")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


# ============================================================================
# DATABASE MAINTENANCE TOOLS
# ============================================================================

@mcp.tool()
def get_database_info() -> str:
    """
    Get general database information including size, compatibility level, and status.

    Returns:
        Dictionary with database properties and settings
    """
    try:
        query = """
        SELECT
            name AS database_name,
            database_id,
            compatibility_level,
            collation_name,
            state_desc AS state,
            recovery_model_desc AS recovery_model,
            page_verify_option_desc AS page_verify,
            is_auto_close_on,
            is_auto_shrink_on,
            is_auto_create_stats_on,
            is_auto_update_stats_on,
            snapshot_isolation_state_desc,
            is_read_committed_snapshot_on,
            create_date,
            (
                SELECT SUM(size) * 8.0 / 1024
                FROM sys.master_files
                WHERE database_id = d.database_id AND type = 0
            ) AS data_size_mb,
            (
                SELECT SUM(size) * 8.0 / 1024
                FROM sys.master_files
                WHERE database_id = d.database_id AND type = 1
            ) AS log_size_mb
        FROM
            sys.databases d
        WHERE
            name = DB_NAME()
        """

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows=None)
            logger.info(f"Retrieved database information")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


@mcp.tool()
def get_backup_history(days: int = 7) -> str:
    """
    Get database backup history for the specified number of days.

    Args:
        days: Number of days to look back (default: 7)

    Returns:
        Dictionary with backup history information
    """
    try:
        query = f"""
        SELECT
            bs.database_name,
            bs.backup_start_date,
            bs.backup_finish_date,
            DATEDIFF(SECOND, bs.backup_start_date, bs.backup_finish_date) AS duration_seconds,
            bs.type AS backup_type,
            CASE bs.type
                WHEN 'D' THEN 'Full'
                WHEN 'I' THEN 'Differential'
                WHEN 'L' THEN 'Log'
                ELSE 'Other'
            END AS backup_type_desc,
            bs.backup_size / 1024.0 / 1024.0 AS backup_size_mb,
            bs.compressed_backup_size / 1024.0 / 1024.0 AS compressed_size_mb,
            bmf.physical_device_name,
            bs.user_name,
            bs.is_copy_only
        FROM
            msdb.dbo.backupset bs
        INNER JOIN
            msdb.dbo.backupmediafamily bmf ON bs.media_set_id = bmf.media_set_id
        WHERE
            bs.database_name = DB_NAME()
            AND bs.backup_start_date >= DATEADD(DAY, -{days}, GETDATE())
        ORDER BY
            bs.backup_start_date DESC
        """

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows=None)
            logger.info(f"Retrieved backup history for last {days} days")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


@mcp.tool()
def get_database_files() -> str:
    """
    Get information about database files including size and growth settings.

    Returns:
        Dictionary with database file information
    """
    try:
        query = """
        SELECT
            name AS file_name,
            type_desc AS file_type,
            physical_name,
            size * 8.0 / 1024 AS size_mb,
            max_size,
            CASE max_size
                WHEN -1 THEN 'Unlimited'
                WHEN 268435456 THEN 'Unlimited'
                ELSE CAST(max_size * 8.0 / 1024 AS VARCHAR(50)) + ' MB'
            END AS max_size_desc,
            growth,
            CASE is_percent_growth
                WHEN 1 THEN CAST(growth AS VARCHAR(10)) + '%'
                ELSE CAST(growth * 8 / 1024 AS VARCHAR(10)) + ' MB'
            END AS growth_desc,
            state_desc AS state
        FROM
            sys.database_files
        ORDER BY
            file_id
        """

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows=None)
            logger.info(f"Retrieved database file information")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


@mcp.tool()
def get_wait_statistics() -> str:
    """
    Get wait statistics to identify performance bottlenecks.

    Returns:
        Dictionary with wait statistics showing what the database is waiting on
    """
    try:
        query = """
        SELECT TOP 20
            wait_type,
            wait_time_ms / 1000.0 AS wait_time_seconds,
            waiting_tasks_count,
            (wait_time_ms / 1000.0) / NULLIF(waiting_tasks_count, 0) AS avg_wait_time_seconds,
            max_wait_time_ms / 1000.0 AS max_wait_time_seconds,
            signal_wait_time_ms / 1000.0 AS signal_wait_time_seconds
        FROM
            sys.dm_os_wait_stats
        WHERE
            wait_type NOT IN (
                'CLR_SEMAPHORE', 'LAZYWRITER_SLEEP', 'RESOURCE_QUEUE',
                'SLEEP_TASK', 'SLEEP_SYSTEMTASK', 'SQLTRACE_BUFFER_FLUSH',
                'WAITFOR', 'LOGMGR_QUEUE', 'CHECKPOINT_QUEUE',
                'REQUEST_FOR_DEADLOCK_SEARCH', 'XE_TIMER_EVENT', 'BROKER_TO_FLUSH',
                'BROKER_TASK_STOP', 'CLR_MANUAL_EVENT', 'CLR_AUTO_EVENT',
                'DISPATCHER_QUEUE_SEMAPHORE', 'FT_IFTS_SCHEDULER_IDLE_WAIT',
                'XE_DISPATCHER_WAIT', 'XE_DISPATCHER_JOIN', 'SQLTRACE_INCREMENTAL_FLUSH_SLEEP'
            )
        ORDER BY
            wait_time_ms DESC
        """

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result_json = format_query_result(columns, rows, max_rows=None)
            logger.info(f"Retrieved wait statistics")
            return result_json

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "timestamp": datetime.now().isoformat()}, indent=2)


# ============================================================================
# MCP RESOURCES
# ============================================================================

@mcp.resource("schema://tables")
def resource_tables() -> str:
    """Resource listing all database tables"""
    result_json = list_tables()
    result = json.loads(result_json)

    if "error" in result:
        return f"Error: {result['error']}"

    output = "Database Tables\n" + "=" * 50 + "\n\n"
    for row in result['rows']:
        schema, table, rows, size = row
        output += f"{schema}.{table}\n"
        output += f"  Rows: {rows:,}\n"
        output += f"  Size: {size:.2f} MB\n\n"

    return output


@mcp.resource("database://info")
def resource_database_info() -> str:
    """Resource with database information"""
    result_json = get_database_info()
    result = json.loads(result_json)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result['rows']:
        return "No database information available"

    row = result['rows'][0]
    cols = result['columns']

    output = "Database Information\n" + "=" * 50 + "\n\n"
    for i, col in enumerate(cols):
        output += f"{col}: {row[i]}\n"

    return output


# ============================================================================
# MCP PROMPTS
# ============================================================================

@mcp.prompt()
def sql_query_helper(query_description: str) -> str:
    """
    Help generate SQL queries based on natural language descriptions.

    Args:
        query_description: Description of what you want to query
    """
    return f"""You are a SQL Server expert. Help generate a SQL query for the following request:

{query_description}

Consider:
1. Use proper SQL Server syntax
2. Include appropriate WHERE clauses for filtering
3. Use JOINs when querying multiple tables
4. Add ORDER BY for sorted results
5. Use TOP N to limit results if appropriate
6. Consider performance implications

Provide the SQL query and explain what it does.
"""


@mcp.prompt()
def performance_troubleshooting() -> str:
    """Prompt for troubleshooting database performance issues"""
    return """You are troubleshooting SQL Server performance issues. Follow this systematic approach:

1. Check active sessions and blocking:
   - Use get_active_sessions() to see current activity
   - Use get_blocking_sessions() to identify blocking chains
   - Use get_long_running_queries() to find slow queries

2. Analyze wait statistics:
   - Use get_wait_statistics() to identify bottlenecks
   - Common wait types indicate different issues:
     * PAGEIOLATCH: Disk I/O bottleneck
     * CXPACKET: Parallelism issues
     * LCK_M_*: Locking/blocking problems
     * WRITELOG: Transaction log bottleneck

3. Check index health:
   - Use get_index_fragmentation() to find fragmented indexes
   - Rebuild indexes with >30% fragmentation
   - Reorganize indexes with 10-30% fragmentation

4. Review resource usage:
   - Use get_table_statistics() for space usage
   - Check get_database_files() for file growth issues

Provide specific recommendations based on your findings.
"""


@mcp.prompt()
def index_maintenance_plan() -> str:
    """Prompt for creating an index maintenance strategy"""
    return """Create an index maintenance plan for SQL Server:

1. Analyze current index state:
   - Use get_index_fragmentation() to assess all indexes
   - Use list_indexes() to see index structure

2. Categorize indexes by fragmentation:
   - >30% fragmentation: REBUILD (rebuilds index completely)
   - 10-30% fragmentation: REORGANIZE (defragments in place)
   - <10% fragmentation: No action needed

3. Consider:
   - Schedule during maintenance window
   - Impact on application availability
   - Space requirements for rebuilds
   - Update statistics after maintenance

4. Best practices:
   - Rebuild clustered indexes first
   - Update statistics on all indexes
   - Monitor transaction log space during operations
   - Consider ONLINE rebuilds for production systems

Provide a prioritized list of indexes to maintain and recommended actions.
"""


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting SQL Server DBA MCP Server")
    logger.info(f"Database: {Config.DATABASE} on {Config.SERVER}")
    logger.info(f"Host: {Config.MCP_HOST}:{Config.MCP_PORT}")

    try:
        mcp.run(
            transport="sse",
            host=Config.MCP_HOST,
            port=Config.MCP_PORT
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
