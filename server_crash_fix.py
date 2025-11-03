#!/usr/bin/env python3
"""
Server-side crash investigation script for recurring Flask app crashes
Run this directly on the Azure VM: python3 server_crash_fix.py
"""

import subprocess
import sqlite3
import os


def check_app_status():
    """Check if Flask app is running"""
    print("=== CHECKING FLASK APP STATUS ===")
    
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.split('\n')
        app_lines = [line for line in lines if 'app.py' in line and 'python' in line and 'grep' not in line]
        
        if app_lines:
            print("✅ Flask app is running:")
            for line in app_lines:
                print(f"   {line}")
            return True
        else:
            print("❌ Flask app is NOT running!")
            return False
    return False


def restart_flask_service():
    """Restart the Flask service"""
    print("\n=== RESTARTING FLASK SERVICE ===")
    
    result = subprocess.run(['sudo', 'systemctl', 'restart', 'lacasadetodos.service'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Service restart command executed")
        
        # Wait a moment
        import time
        time.sleep(5)
        
        # Check if it's running now
        if check_app_status():
            print("✅ Service successfully restarted!")
        else:
            print("❌ Service restart failed")
    else:
        print(f"❌ Restart failed: {result.stderr}")


def check_database():
    """Check database health"""
    print("\n=== CHECKING DATABASE ===")
    
    db_path = '/home/casa/CasaTodos/nfl_fantasy.db'
    
    if os.path.exists(db_path):
        try:
            # Check file size
            size_result = subprocess.run(['ls', '-lh', db_path], capture_output=True, text=True)
            if size_result.returncode == 0:
                print(f"Database file: {size_result.stdout.strip()}")
            
            # Check integrity
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            integrity = cursor.fetchone()
            print(f"Database integrity: {integrity[0]}")
            conn.close()
            
        except Exception as e:
            print(f"❌ Database error: {e}")
    else:
        print(f"❌ Database not found at {db_path}")


def setup_monitoring():
    """Set up crash monitoring and auto-restart"""
    print("\n=== SETTING UP MONITORING ===")
    
    monitor_script = '''#!/bin/bash
# Auto-restart Flask app if crashed
LOG_FILE="/home/casa/flask_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

if pgrep -f "python.*app.py" > /dev/null; then
    PID=$(pgrep -f "python.*app.py")
    MEM=$(ps -p $PID -o %mem --no-headers | tr -d ' ')
    echo "$DATE - HEALTHY: PID=$PID, MEM=$MEM%" >> $LOG_FILE
else
    echo "$DATE - CRASH DETECTED! Restarting..." >> $LOG_FILE
    sudo systemctl restart lacasadetodos.service
    sleep 5
    if pgrep -f "python.*app.py" > /dev/null; then
        echo "$DATE - RESTARTED OK" >> $LOG_FILE
    else
        echo "$DATE - RESTART FAILED" >> $LOG_FILE
    fi
fi
'''
    
    # Write monitoring script
    script_path = '/home/casa/flask_monitor.sh'
    with open(script_path, 'w') as f:
        f.write(monitor_script)
    
    # Make executable
    subprocess.run(['chmod', '+x', script_path])
    
    # Add to cron (every 5 minutes)
    cron_cmd = '(crontab -l 2>/dev/null | grep -v flask_monitor; echo "*/5 * * * * /home/casa/flask_monitor.sh") | crontab -'
    subprocess.run(['bash', '-c', cron_cmd])
    
    print("✅ Monitoring script created: /home/casa/flask_monitor.sh")
    print("✅ Cron job added: checks every 5 minutes")
    print("✅ Log file: /home/casa/flask_monitor.log")


def check_system_resources():
    """Check memory and disk usage"""
    print("\n=== SYSTEM RESOURCES ===")
    
    # Memory
    mem_result = subprocess.run(['free', '-h'], capture_output=True, text=True)
    if mem_result.returncode == 0:
        print("Memory usage:")
        print(mem_result.stdout)
    
    # Disk
    disk_result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
    if disk_result.returncode == 0:
        print("Disk usage:")
        print(disk_result.stdout)


def main():
    print("🔧 FLASK APP CRASH INVESTIGATION & FIX")
    print("=" * 50)
    
    # Check current status
    app_running = check_app_status()
    
    # Check system resources
    check_system_resources()
    
    # Check database
    check_database()
    
    # If app is down, restart it
    if not app_running:
        restart_flask_service()
    
    # Set up monitoring
    setup_monitoring()
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print("1. ✅ Monitoring installed (checks every 5 minutes)")
    print("2. ✅ Auto-restart on crash detection")
    print("3. ✅ Logging to /home/casa/flask_monitor.log")
    print("\n📋 NEXT STEPS:")
    print("- Check /home/casa/flask_monitor.log after 2-3 days")
    print("- Look for crash patterns in the logs")
    print("- This script will prevent extended outages")


if __name__ == "__main__":
    main()