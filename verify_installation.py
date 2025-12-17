"""
Installation Verification Script for SQL Server MCP

Run this script to verify all dependencies and configuration are correct.
"""

import sys
import os
from packaging.version import Version, InvalidVersion

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("  [OK] Python version is compatible")
        return True
    else:
        print("  [ERROR] Python 3.8+ required")
        return False

def check_dependencies():
    """Check required dependencies"""
    dependencies = {
        'pyodbc': '5.0.0',
        'fastmcp': '2.0.0',
        'mcp': '1.0.0',
        'dotenv': '1.0.0',
        'colorlog': '6.0.0'
    }

    print("\nChecking Dependencies:")
    all_ok = True

    for package, min_version in dependencies.items():
        try:
            if package == 'dotenv':
                import dotenv as pkg
                name = 'python-dotenv'
            elif package == 'pyodbc':
                import pyodbc as pkg
                name = 'pyodbc'
            elif package == 'fastmcp':
                import fastmcp as pkg
                name = 'fastmcp'
            elif package == 'mcp':
                import mcp as pkg
                name = 'mcp'
            elif package == 'colorlog':
                import colorlog as pkg
                name = 'colorlog'

            if hasattr(pkg, '__version__'):
                version = pkg.__version__
            elif hasattr(pkg, 'version'):
                version = pkg.version
            else:
                version = 'unknown'

            status = "[OK]"
            message = f"{name:20s} version {version}"

            if version != 'unknown':
                try:
                    if Version(str(version)) < Version(min_version):
                        status = "[ERROR]"
                        message = f"{name:20s} version {version} (minimum {min_version})"
                        all_ok = False
                except InvalidVersion:
                    status = "[WARNING]"
                    message = f"{name:20s} version {version} (unable to parse, expected >= {min_version})"

            print(f"  {status} {message}")
        except ImportError:
            print(f"  [ERROR] {name} not installed")
            all_ok = False

    return all_ok

def check_odbc_drivers():
    """Check available ODBC drivers"""
    print("\nChecking ODBC Drivers:")
    try:
        import pyodbc
        drivers = pyodbc.drivers()

        required_driver = None
        for driver in drivers:
            if 'SQL Server' in driver:
                print(f"  [OK] Found: {driver}")
                if 'ODBC Driver' in driver:
                    required_driver = driver

        if required_driver:
            return True
        else:
            print("  [WARNING] No ODBC Driver for SQL Server found (only generic SQL Server driver)")
            return True  # Still allow, may work
    except Exception as e:
        print(f"  [ERROR] Could not check ODBC drivers: {e}")
        return False

def check_env_file():
    """Check .env file exists"""
    print("\nChecking Configuration:")
    if os.path.exists('.env'):
        print("  [OK] .env file exists")
        return True
    else:
        print("  [WARNING] .env file not found")
        print("         Copy .env.example to .env and configure it")
        return False

def check_server_import():
    """Check server can be imported"""
    print("\nChecking Server Code:")
    try:
        import sql_mcp_server
        print("  [OK] Server imports successfully")

        # Check configuration
        config = sql_mcp_server.Config
        print(f"  [OK] Configuration loaded")
        print(f"       Server: {config.SERVER}")
        print(f"       Database: {config.DATABASE}")
        print(f"       Host: {config.MCP_HOST}:{config.MCP_PORT}")

        return True
    except Exception as e:
        print(f"  [ERROR] Server import failed: {e}")
        return False

def test_database_connection():
    """Test database connection (optional)"""
    print("\nTesting Database Connection:")
    print("  (This will attempt to connect to the database)")

    try:
        import sql_mcp_server

        # Try to get a connection
        try:
            with sql_mcp_server.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()[0]
                print(f"  [OK] Database connection successful")
                version_line = version.split("\n")[0][:80]
                print(f"       SQL Server: {version_line}")
                return True
        except Exception as e:
            print(f"  [ERROR] Database connection failed: {e}")
            print("         Check your .env configuration and database access")
            return False

    except Exception as e:
        print(f"  [ERROR] Could not test connection: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 70)
    print("SQL Server MCP - Installation Verification")
    print("=" * 70)

    results = []

    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("ODBC Drivers", check_odbc_drivers()))
    results.append(("Configuration", check_env_file()))
    results.append(("Server Code", check_server_import()))

    # Optional: Test database connection
    print("\n" + "=" * 70)
    test_db = input("Test database connection? (y/n): ").lower().strip()
    if test_db == 'y':
        results.append(("Database Connection", test_database_connection()))

    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)

    all_passed = True
    for name, passed in results:
        status = "[OK]" if passed else "[FAILED]"
        print(f"{status:10s} {name}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("\n[SUCCESS] All checks passed! Server is ready to run.")
        print("\nTo start the server, run:")
        print("  python sql_mcp_server.py")
    else:
        print("\n[WARNING] Some checks failed. Review errors above.")
        print("\nRefer to README.md for installation instructions.")

    print("=" * 70)

if __name__ == "__main__":
    main()
