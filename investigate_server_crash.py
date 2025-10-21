#!/usr/bin/env python3
"""
Server Crash Investigation Script
Run this script on the server to diagnose the app crash
"""

import subprocess
import os
import sys
from datetime import datetime

def run_command(cmd, description):
    """Run a command and capture its output"""
    print(f"\n{'='*60}")
    print(f"CHECKING: {description}")
    print(f"COMMAND: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"EXIT CODE: {result.returncode}")
    except subprocess.TimeoutExpired:
        print("TIMEOUT: Command took too long")
    except Exception as e:
        print(f"ERROR: {e}")

def investigate_crash():
    """Main investigation function"""
    print(f"SERVER CRASH INVESTIGATION - {datetime.now()}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Basic system info
    run_command("whoami", "Current user")
    run_command("pwd", "Current directory")
    run_command("ls -la", "Directory contents")
    
    # Check if Flask app is running
    run_command("ps aux | grep python", "Python processes")
    run_command("ps aux | grep flask", "Flask processes")
    run_command("ps aux | grep casa", "Casa-related processes")
    
    # Check system resources
    run_command("free -h", "Memory usage")
    run_command("df -h", "Disk usage")
    run_command("uptime", "System uptime and load")
    
    # Check network and ports
    run_command("netstat -tlnp | grep :5000", "Port 5000 status")
    run_command("netstat -tlnp | grep :80", "Port 80 status")
    run_command("netstat -tlnp | grep :443", "Port 443 status")
    
    # Check systemd services (if applicable)
    run_command("systemctl status casa-todos", "Casa-todos service status")
    run_command("systemctl status nginx", "Nginx status")
    run_command("systemctl status apache2", "Apache status")
    
    # Check recent logs
    run_command("ls -la /var/log/ | head -20", "Recent system logs")
    run_command("tail -50 /var/log/syslog", "Recent syslog entries")
    run_command("journalctl -u casa-todos --no-pager -n 50", "Casa-todos service logs")
    
    # Check application directory
    run_command("ls -la ~/CasaTodos/ 2>/dev/null || ls -la ~/casa-todos/ 2>/dev/null || ls -la /opt/casa-todos/ 2>/dev/null", "App directory")
    
    # Check for crash dumps or error logs
    run_command("find . -name '*.log' -mtime -1", "Recent log files")
    run_command("find /tmp -name 'core*' -mtime -1 2>/dev/null", "Recent core dumps")
    
    # Check Python environment
    run_command("which python3", "Python3 location")
    run_command("python3 --version", "Python3 version")
    run_command("pip3 list | grep -i flask", "Flask installation")
    
    # Check recent system events
    run_command("last reboot | head -5", "Recent reboots")
    run_command("dmesg | tail -20", "Recent kernel messages")

if __name__ == "__main__":
    investigate_crash()