#!/usr/bin/env python3
"""
Flask Server Crash Log Capture Tool
===================================
This tool captures comprehensive crash logs when running the Flask server
for submission to Ubuntu server troubleshooting.
"""

import sys
import os
import traceback
import subprocess
import platform
import datetime
import json
import sqlite3
from pathlib import Path

def get_system_info():
    """Get comprehensive system information"""
    info = {
        'platform': platform.platform(),
        'python_version': sys.version,
        'python_executable': sys.executable,
        'current_directory': os.getcwd(),
        'environment_variables': {
            'FLASK_APP': os.environ.get('FLASK_APP', 'Not set'),
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'Not set'),
            'FLASK_DEBUG': os.environ.get('FLASK_DEBUG', 'Not set'),
            'PYTHONPATH': os.environ.get('PYTHONPATH', 'Not set'),
            'PATH': os.environ.get('PATH', 'Not shown for security')[:100] + '...'
        },
        'timestamp': datetime.datetime.now().isoformat()
    }
    return info

def check_database_status():
    """Check database file status"""
    db_status = {}
    
    for db_file in ['database.db', 'nfl_fantasy.db']:
        if os.path.exists(db_file):
            stat = os.stat(db_file)
            db_status[db_file] = {
                'exists': True,
                'size': stat.st_size,
                'readable': os.access(db_file, os.R_OK),
                'writable': os.access(db_file, os.W_OK)
            }
            
            # Try to connect and get basic info
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Get table count
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                db_status[db_file]['tables'] = len(tables)
                
                # Get game count if nfl_games table exists
                try:
                    cursor.execute("SELECT COUNT(*) FROM nfl_games")
                    db_status[db_file]['games_count'] = cursor.fetchone()[0]
                except:
                    db_status[db_file]['games_count'] = 'N/A'
                
                conn.close()
                db_status[db_file]['connection_status'] = 'OK'
                
            except Exception as e:
                db_status[db_file]['connection_status'] = f'ERROR: {str(e)}'
        else:
            db_status[db_file] = {'exists': False}
    
    return db_status

def capture_flask_startup_crash():
    """Capture Flask startup crash with full details"""
    print("=" * 60)
    print("FLASK SERVER CRASH LOG CAPTURE")
    print("=" * 60)
    print(f"Timestamp: {datetime.datetime.now()}")
    print()
    
    # System Information
    print("SYSTEM INFORMATION:")
    print("-" * 30)
    system_info = get_system_info()
    for key, value in system_info.items():
        if key == 'environment_variables':
            print("Environment Variables:")
            for env_key, env_value in value.items():
                print(f"  {env_key}: {env_value}")
        else:
            print(f"{key}: {value}")
    print()
    
    # Database Status
    print("DATABASE STATUS:")
    print("-" * 30)
    db_status = check_database_status()
    for db_name, status in db_status.items():
        print(f"{db_name}:")
        for key, value in status.items():
            print(f"  {key}: {value}")
    print()
    
    # Python Import Test
    print("PYTHON IMPORT TESTS:")
    print("-" * 30)
    required_modules = [
        'Flask', 'sqlite3', 'datetime', 'os', 'sys',
        'werkzeug', 'requests', 'pytz', 'reportlab'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: OK")
        except ImportError as e:
            print(f"❌ {module}: FAILED - {e}")
    print()
    
    # Flask App Import Test
    print("FLASK APP IMPORT TEST:")
    print("-" * 30)
    try:
        import app
        print("✅ app.py import: SUCCESS")
        
        # Test app initialization
        try:
            app.initialize_app()
            print("✅ app.initialize_app(): SUCCESS")
        except Exception as e:
            print(f"❌ app.initialize_app(): FAILED - {e}")
            print(f"Traceback:\n{traceback.format_exc()}")
        
        # Test Flask app object
        try:
            flask_app = app.app
            print(f"✅ Flask app object: {type(flask_app)}")
        except Exception as e:
            print(f"❌ Flask app object: FAILED - {e}")
            
    except Exception as e:
        print(f"❌ app.py import: FAILED - {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
    print()
    
    # Attempt Direct Flask Run
    print("DIRECT FLASK EXECUTION TEST:")
    print("-" * 30)
    try:
        # Try to run Flask in debug mode to capture startup errors
        result = subprocess.run([
            sys.executable, '-c', '''
import sys
import traceback
try:
    import app
    print("Flask import successful")
    app.initialize_app()
    print("App initialization successful")
    # Try to start the development server
    app.app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
except Exception as e:
    print(f"CRASH: {type(e).__name__}: {str(e)}")
    print("TRACEBACK:")
    traceback.print_exc()
    sys.exit(1)
'''
        ], capture_output=True, text=True, timeout=10)
        
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        print(f"Return Code: {result.returncode}")
        
    except subprocess.TimeoutExpired:
        print("✅ Flask server started successfully (timed out after 10 seconds - this is expected)")
    except Exception as e:
        print(f"❌ Flask execution failed: {e}")
    print()
    
    # File Permission Check
    print("FILE PERMISSIONS:")
    print("-" * 30)
    files_to_check = ['app.py', 'database.db', 'nfl_fantasy.db', 'requirements.txt']
    for file_path in files_to_check:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            readable = os.access(file_path, os.R_OK)
            writable = os.access(file_path, os.W_OK)
            print(f"{file_path}: Size={stat.st_size}, Read={readable}, Write={writable}")
        else:
            print(f"{file_path}: NOT FOUND")
    print()
    
    # Port Availability Check
    print("PORT AVAILABILITY:")
    print("-" * 30)
    import socket
    ports_to_check = [5000, 8000, 3000, 80]
    for port in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                print(f"Port {port}: IN USE")
            else:
                print(f"Port {port}: AVAILABLE")
        except Exception as e:
            print(f"Port {port}: ERROR - {e}")
    print()
    
    print("=" * 60)
    print("CRASH LOG CAPTURE COMPLETE")
    print("=" * 60)
    print()
    print("UBUNTU DEPLOYMENT INSTRUCTIONS:")
    print("1. Copy this entire log output")
    print("2. Save it as 'flask_crash_log.txt' on your Ubuntu server")
    print("3. Include it when reporting server issues")
    print("4. Also run: sudo journalctl -u your-service-name -f")
    print("5. Check: sudo systemctl status your-service-name")

if __name__ == "__main__":
    capture_flask_startup_crash()