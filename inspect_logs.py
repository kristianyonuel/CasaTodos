#!/usr/bin/env python3
"""
Flask Application Log Inspector
===============================
This tool helps you find and inspect all logs related to your Flask application.
"""

import os
import sys
import datetime
from pathlib import Path

def get_file_info(filepath):
    """Get comprehensive file information"""
    if not os.path.exists(filepath):
        return None
    
    stat = os.stat(filepath)
    return {
        'size': stat.st_size,
        'modified': datetime.datetime.fromtimestamp(stat.st_mtime),
        'created': datetime.datetime.fromtimestamp(stat.st_ctime),
        'readable': os.access(filepath, os.R_OK)
    }

def format_size(bytes_size):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def inspect_logs():
    """Inspect all log files and logging configuration"""
    print("🔍 Flask Application Log Inspector")
    print("=" * 50)
    print(f"Current Directory: {os.getcwd()}")
    print(f"Timestamp: {datetime.datetime.now()}")
    print()
    
    # Check main application log
    print("📋 APPLICATION LOGS")
    print("-" * 30)
    
    log_files = [
        'app.log',
        'crash_diagnosis.log', 
        'flask.log',
        'error.log',
        'debug.log',
        'server.log'
    ]
    
    found_logs = []
    
    for log_file in log_files:
        info = get_file_info(log_file)
        if info:
            found_logs.append((log_file, info))
            status = "✅ EXISTS" if info['size'] > 0 else "⚠️ EMPTY"
            print(f"{status} {log_file}")
            print(f"    Size: {format_size(info['size'])}")
            print(f"    Last Modified: {info['modified']}")
            print(f"    Readable: {info['readable']}")
            print()
        else:
            print(f"❌ NOT FOUND {log_file}")
    
    if not found_logs:
        print("❌ No log files found!")
    
    # Check Flask app configuration
    print("⚙️ LOGGING CONFIGURATION")
    print("-" * 30)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
            
        if 'logging.basicConfig' in content:
            print("✅ Logging is configured in app.py")
        else:
            print("❌ No logging configuration found in app.py")
            
        if 'FileHandler' in content:
            print("✅ File logging is enabled")
        else:
            print("❌ No file logging configured")
            
        if "app.log" in content:
            print("✅ Configured to log to 'app.log'")
        else:
            print("❌ Log file name not found in configuration")
            
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
    
    print()
    
    # Check if Flask has been run recently
    print("🚀 FLASK EXECUTION HISTORY")
    print("-" * 30)
    
    # Check for Python processes
    try:
        import subprocess
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        if 'python.exe' in result.stdout:
            print("✅ Python processes currently running")
            print("    Check: Some Python processes are active")
        else:
            print("❌ No Python processes currently running")
    except Exception as e:
        print(f"⚠️ Could not check running processes: {e}")
    
    # Check recent app.log entries if it exists and has content
    print("\n📖 RECENT LOG ENTRIES")
    print("-" * 30)
    
    for log_file, info in found_logs:
        if info['size'] > 0:
            print(f"\n📄 Last 10 lines of {log_file}:")
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    if lines:
                        for line in lines[-10:]:
                            print(f"    {line.rstrip()}")
                    else:
                        print("    (File is empty)")
            except Exception as e:
                print(f"    Error reading file: {e}")
        else:
            print(f"\n📄 {log_file}: (Empty file)")
    
    # Logging recommendations
    print("\n💡 LOGGING RECOMMENDATIONS")
    print("-" * 30)
    print("1. To capture Flask logs on Ubuntu:")
    print("   python app.py 2>&1 | tee flask_runtime.log")
    print()
    print("2. To enable debug logging, add to app.py:")
    print("   app.logger.setLevel(logging.DEBUG)")
    print()
    print("3. To capture startup errors:")
    print("   python app.py > startup.log 2>&1")
    print()
    print("4. To monitor logs in real-time (Ubuntu):")
    print("   tail -f app.log")
    print()
    print("5. For systemd service logs (Ubuntu):")
    print("   sudo journalctl -u casa-todos -f")
    print()
    print("6. Check Windows Event Logs:")
    print("   eventvwr.msc -> Application Logs")

if __name__ == "__main__":
    inspect_logs()