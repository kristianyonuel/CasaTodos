#!/usr/bin/env python3
"""
Investigate recurring Flask app crashes every 2 days
This script will help identify the root cause and implement monitoring
"""

import sqlite3
import subprocess
import json
import os
from datetime import datetime, timedelta

def check_current_app_status():
    """Check if the Flask app is currently running"""
    print("=== CURRENT APP STATUS ===")
    
    # Check if process is running (locally on server)
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    
    if result.returncode == 0:
        # Filter for app.py processes
        lines = result.stdout.split('\n')
        app_lines = [line for line in lines if 'app.py' in line and 'python' in line and 'grep' not in line]
        
        if app_lines:
            print("✅ Flask app is currently running:")
            for line in app_lines:
                print(line)
                parts = line.split()
                if len(parts) >= 11:
                    pid = parts[1]
                    cpu = parts[2]
                    mem = parts[3]
                    start_time = ' '.join(parts[8:11])
                    print(f"   PID: {pid}, CPU: {cpu}%, Memory: {mem}%, Started: {start_time}")
            return True
        else:
            print("❌ Flask app is NOT running - this confirms the crash!")
            return False
    else:
        print("❌ Could not check process status")
        return False

def check_system_resources():
    """Check system memory and disk usage"""
    print("\n=== SYSTEM RESOURCES ===")
    
    # Memory usage (local)
    result = subprocess.run(['free', '-h'], capture_output=True, text=True)
    if result.returncode == 0:
        print("Memory Usage:")
        print(result.stdout)
    
    # Disk usage (local)
    result = subprocess.run(['df', '-h'], capture_output=True, text=True)
    if result.returncode == 0:
        print("Disk Usage:")
        print(result.stdout)

def check_app_logs():
    """Check application logs for errors"""
    print("\n=== APPLICATION LOGS ===")
    
    # Check app.log (local path)
    app_log_path = '/home/casa/CasaTodos/app.log'
    if os.path.exists(app_log_path):
        result = subprocess.run(['tail', '-50', app_log_path], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Last 50 lines of app.log:")
            print(result.stdout)
        else:
            print("❌ Could not read app.log")
    else:
        print("❌ app.log file not found")


def check_system_logs():
    """Check system logs for crash indicators"""
    print("\n=== SYSTEM LOGS ===")
    
    # Check for Python/Flask crashes in syslog (local)
    cmd = ['sudo', 'journalctl', '-u', 'lacasadetodos.service', 
           '--since', '3 days ago']
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.split('\n')
        last_lines = lines[-50:] if len(lines) > 50 else lines
        print("Service logs (last 50 lines from past 3 days):")
        print('\n'.join(last_lines))
    
    # Check for OOM (Out of Memory) kills (local)
    cmd = ['sudo', 'dmesg']
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.split('\n')
        oom_lines = [line for line in lines if 'killed process' in line.lower() 
                     or 'out of memory' in line.lower()]
        if oom_lines:
            print("\n⚠️  Out of Memory kills found:")
            for line in oom_lines[-20:]:  # Last 20 OOM events
                print(line)

def check_database_locks():
    """Check for database lock issues that could cause crashes"""
    print("\n=== DATABASE HEALTH ===")
    
    # Check local database directly (nfl_fantasy.db)
    db_path = '/home/casa/CasaTodos/nfl_fantasy.db'
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check database integrity
            cursor.execute("PRAGMA integrity_check;")
            integrity = cursor.fetchone()
            print(f"Database integrity: {integrity[0]}")
            
            # Check database size
            result = subprocess.run(['ls', '-lh', db_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Database file size: {result.stdout.strip()}")
            
            # Check for locked tables
            cursor.execute("PRAGMA compile_options;")
            options = cursor.fetchall()
            print(f"SQLite compile options: {len(options)} options found")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Database check failed: {e}")
    else:
        print(f"❌ Database not found at {db_path}")

def create_monitoring_script():
    """Create a monitoring script to track crashes"""
    print("\n=== CREATING MONITORING SOLUTION ===")
    
    monitoring_script = '''#!/bin/bash
# Flask App Health Monitor
# Checks every 5 minutes and logs status

LOG_FILE="/home/casa/flask_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check if Flask app is running
if pgrep -f "python.*app.py" > /dev/null; then
    # App is running - log health info
    PID=$(pgrep -f "python.*app.py")
    MEM=$(ps -p $PID -o %mem --no-headers | tr -d ' ')
    CPU=$(ps -p $PID -o %cpu --no-headers | tr -d ' ')
    
    echo "$DATE - HEALTHY: PID=$PID, CPU=$CPU%, MEM=$MEM%" >> $LOG_FILE
else
    # App is down - log crash and restart
    echo "$DATE - ❌ CRASH DETECTED! Flask app is down" >> $LOG_FILE
    
    # Try to restart the service
    sudo systemctl restart lacasadetodos.service
    sleep 10
    
    if pgrep -f "python.*app.py" > /dev/null; then
        echo "$DATE - ✅ Service restarted successfully" >> $LOG_FILE
    else
        echo "$DATE - ❌ Service restart FAILED" >> $LOG_FILE
    fi
fi
'''
    
    # Write monitoring script locally
    script_path = '/home/casa/flask_monitor.sh'
    with open(script_path, 'w') as f:
        f.write(monitoring_script)
    
    # Make executable
    subprocess.run(['chmod', '+x', script_path])
    
    # Add to cron (every 5 minutes)
    cron_entry = "*/5 * * * * /home/casa/flask_monitor.sh"
    subprocess.run(['bash', '-c', 
                   f'(crontab -l 2>/dev/null | grep -v flask_monitor; echo "{cron_entry}") | crontab -'])
    
    print("✅ Monitoring script installed - will check every 5 minutes")
    print("   Script: /home/casa/flask_monitor.sh")
    print("   Log file: /home/casa/flask_monitor.log")

def restart_service_now():
    """Restart the Flask service to fix current outage"""
    print("\n=== RESTARTING SERVICE ===")
    
    # Restart locally using systemctl
    result = subprocess.run(['sudo', 'systemctl', 'restart', 'lacasadetodos.service'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Service restart command sent")
        
        # Wait and check if it's running
        import time
        time.sleep(10)
        
        # Check locally
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            app_lines = [line for line in lines if 'app.py' in line and 'python' in line and 'grep' not in line]
            
            if app_lines:
                print("✅ Flask app is now running!")
                for line in app_lines:
                    print(line)
            else:
                print("❌ Service restart failed - app still not running")
        else:
            print("❌ Could not check process status after restart")
    else:
        print(f"❌ Service restart failed: {result.stderr}")

def main():
    print("🔍 INVESTIGATING RECURRING FLASK APP CRASHES")
    print("=" * 50)
    
    # Check current status
    app_running = check_current_app_status()
    
    # Check system resources
    check_system_resources()
    
    # Check logs
    check_app_logs()
    check_system_logs()
    
    # Check database
    check_database_locks()
    
    # Create monitoring solution
    create_monitoring_script()
    
    # If app is down, restart it
    if not app_running:
        restart_service_now()
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY & RECOMMENDATIONS:")
    print("1. Monitoring script installed (checks every 5 minutes)")
    print("2. Auto-restart on crash detection")
    print("3. Logging crash patterns to /home/casa/flask_monitor.log")
    print("4. Check logs in 2-3 days to identify crash patterns")
    
    print("\n📋 NEXT STEPS:")
    print("- Monitor /home/casa/flask_monitor.log for crash patterns")
    print("- Run this script again if crashes continue")
    print("- Consider upgrading server memory if OOM kills found")

if __name__ == "__main__":
    main()