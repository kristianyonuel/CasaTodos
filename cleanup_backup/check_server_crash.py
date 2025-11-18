#!/usr/bin/env python3
"""
Server Crash Diagnosis Tool
===========================
This tool helps diagnose why the Flask server is crashing by:
1. Checking application logs
2. Testing database connections
3. Verifying imports and dependencies
4. Running startup tests
5. Providing detailed error reporting

Run this before starting the Flask app to identify potential issues.
"""

import os
import sys
import sqlite3
import traceback
import logging
from datetime import datetime
import subprocess

def setup_logging():
    """Setup detailed logging for diagnosis"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('crash_diagnosis.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def check_log_files():
    """Check existing log files for crash information"""
    logger = logging.getLogger(__name__)
    log_files = ['app.log', 'error.log', 'flask.log', 'nohup.out']
    
    logger.info("🔍 CHECKING EXISTING LOG FILES")
    logger.info("=" * 50)
    
    for log_file in log_files:
        if os.path.exists(log_file):
            logger.info(f"📄 Found log file: {log_file}")
            
            # Get file size
            size = os.path.getsize(log_file)
            logger.info(f"   Size: {size:,} bytes")
            
            # Show last 20 lines
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        logger.info(f"   Last modified: {datetime.fromtimestamp(os.path.getmtime(log_file))}")
                        logger.info("   Last 10 lines:")
                        for line in lines[-10:]:
                            logger.info(f"   > {line.strip()}")
                    else:
                        logger.info("   File is empty")
            except Exception as e:
                logger.error(f"   Error reading {log_file}: {e}")
        else:
            logger.info(f"❌ Log file not found: {log_file}")
    
    logger.info("")

def test_database_connection():
    """Test database connections and structure"""
    logger = logging.getLogger(__name__)
    logger.info("🗄️ TESTING DATABASE CONNECTIONS")
    logger.info("=" * 50)
    
    databases = ['database.db', 'nfl_fantasy.db']
    
    for db_file in databases:
        logger.info(f"📁 Testing {db_file}:")
        
        if not os.path.exists(db_file):
            logger.error(f"   ❌ Database file not found: {db_file}")
            continue
        
        size = os.path.getsize(db_file)
        logger.info(f"   Size: {size:,} bytes")
        
        if size == 0:
            logger.error(f"   ❌ Database file is empty: {db_file}")
            continue
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            logger.info(f"   Tables found: {len(tables)}")
            
            required_tables = ['users', 'nfl_games', 'user_picks']
            for table in required_tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    logger.info(f"   ✅ {table}: {count} records")
                else:
                    logger.error(f"   ❌ Missing table: {table}")
            
            conn.close()
            logger.info(f"   ✅ {db_file} connection successful")
            
        except Exception as e:
            logger.error(f"   ❌ Database error in {db_file}: {e}")
    
    logger.info("")

def test_python_imports():
    """Test critical Python imports that Flask app needs"""
    logger = logging.getLogger(__name__)
    logger.info("🐍 TESTING PYTHON IMPORTS")
    logger.info("=" * 50)
    
    critical_imports = [
        'flask',
        'sqlite3', 
        'werkzeug',
        'datetime',
        'logging',
        'os',
        'sys',
        'json',
        'csv',
        'io'
    ]
    
    project_imports = [
        'nfl_week_calculator',
        'deadline_manager',
        'models'
    ]
    
    for module in critical_imports:
        try:
            __import__(module)
            logger.info(f"   ✅ {module}")
        except ImportError as e:
            logger.error(f"   ❌ {module}: {e}")
    
    logger.info("\n   Project-specific imports:")
    for module in project_imports:
        try:
            __import__(module)
            logger.info(f"   ✅ {module}")
        except ImportError as e:
            logger.error(f"   ❌ {module}: {e}")
    
    logger.info("")

def check_file_permissions():
    """Check file and directory permissions"""
    logger = logging.getLogger(__name__)
    logger.info("🔐 CHECKING FILE PERMISSIONS")
    logger.info("=" * 50)
    
    critical_files = [
        'app.py',
        'database.db',
        'nfl_fantasy.db',
        'templates/',
        'static/'
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            # Check if readable
            readable = os.access(file_path, os.R_OK)
            writable = os.access(file_path, os.W_OK)
            
            logger.info(f"   {file_path}:")
            logger.info(f"     Readable: {'✅' if readable else '❌'}")
            logger.info(f"     Writable: {'✅' if writable else '❌'}")
            
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                logger.info(f"     Size: {size:,} bytes")
        else:
            logger.error(f"   ❌ Not found: {file_path}")
    
    logger.info("")

def test_port_availability():
    """Check if the Flask port is available"""
    logger = logging.getLogger(__name__)
    logger.info("🌐 CHECKING PORT AVAILABILITY")
    logger.info("=" * 50)
    
    import socket
    
    ports_to_check = [5000, 8000, 3000, 80]
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            logger.warning(f"   ⚠️  Port {port} is already in use")
        else:
            logger.info(f"   ✅ Port {port} is available")
    
    logger.info("")

def run_minimal_flask_test():
    """Run a minimal Flask app to test if Flask starts"""
    logger = logging.getLogger(__name__)
    logger.info("🧪 TESTING MINIMAL FLASK APP")
    logger.info("=" * 50)
    
    try:
        from flask import Flask
        
        test_app = Flask(__name__)
        
        @test_app.route('/test')
        def test_route():
            return "Test successful"
        
        # Try to get the app context
        with test_app.app_context():
            logger.info("   ✅ Flask app context created successfully")
        
        logger.info("   ✅ Minimal Flask app test passed")
        
    except Exception as e:
        logger.error(f"   ❌ Minimal Flask test failed: {e}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
    
    logger.info("")

def check_system_resources():
    """Check system resources that might cause crashes"""
    logger = logging.getLogger(__name__)
    logger.info("💻 CHECKING SYSTEM RESOURCES")
    logger.info("=" * 50)
    
    try:
        import psutil
        
        # Memory
        memory = psutil.virtual_memory()
        logger.info(f"   Memory usage: {memory.percent}%")
        logger.info(f"   Available memory: {memory.available / (1024**3):.1f} GB")
        
        # Disk space
        disk = psutil.disk_usage('.')
        logger.info(f"   Disk usage: {disk.percent}%")
        logger.info(f"   Free disk space: {disk.free / (1024**3):.1f} GB")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        logger.info(f"   CPU usage: {cpu_percent}%")
        
    except ImportError:
        logger.warning("   ⚠️  psutil not available, install with: pip install psutil")
        
        # Basic disk space check
        try:
            import shutil
            total, used, free = shutil.disk_usage('.')
            logger.info(f"   Free disk space: {free / (1024**3):.1f} GB")
        except Exception as e:
            logger.error(f"   Error checking disk space: {e}")
    
    logger.info("")

def suggest_fixes():
    """Suggest common fixes for server crashes"""
    logger = logging.getLogger(__name__)
    logger.info("💡 SUGGESTED FIXES FOR COMMON ISSUES")
    logger.info("=" * 50)
    
    suggestions = [
        "1. Check if database files exist and are not corrupted",
        "2. Verify all required Python packages are installed: pip install -r requirements.txt",
        "3. Check for port conflicts - kill existing Flask processes",
        "4. Ensure proper file permissions for database and static files",
        "5. Check available disk space and memory",
        "6. Look for syntax errors in Python files",
        "7. Verify environment variables and configuration",
        "8. Check for circular imports in Python modules",
        "9. Test with minimal Flask configuration first",
        "10. Enable debug mode to see detailed error messages"
    ]
    
    for suggestion in suggestions:
        logger.info(f"   {suggestion}")
    
    logger.info("")
    logger.info("🔧 Quick Commands to Try:")
    logger.info("   Kill existing Flask processes: pkill -f 'python.*app.py'")
    logger.info("   Check running processes: ps aux | grep python")
    logger.info("   Run Flask in debug mode: python app.py --debug")
    logger.info("   Check Python syntax: python -m py_compile app.py")

def main():
    """Main diagnosis function"""
    logger = setup_logging()
    
    logger.info("🚑 FLASK SERVER CRASH DIAGNOSIS")
    logger.info("=" * 60)
    logger.info(f"Started at: {datetime.now()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("")
    
    try:
        check_log_files()
        test_database_connection()
        test_python_imports()
        check_file_permissions()
        test_port_availability()
        run_minimal_flask_test()
        check_system_resources()
        suggest_fixes()
        
        logger.info("🎯 DIAGNOSIS COMPLETE")
        logger.info("Check crash_diagnosis.log for full details")
        logger.info("Look for ❌ marks above to identify issues")
        
    except Exception as e:
        logger.error(f"Diagnosis script error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    main()