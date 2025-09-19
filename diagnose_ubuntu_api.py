#!/usr/bin/env python3
"""
Ubuntu API Diagnostic Script
Identifies specific issues preventing the background updater from working on Ubuntu
"""

import os
import sys
import subprocess
import sqlite3
import requests
import json
from datetime import datetime, timedelta
import socket
import ssl

def check_python_environment():
    """Check Python environment and dependencies"""
    print("🐍 PYTHON ENVIRONMENT CHECK")
    print("=" * 50)
    
    # Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check required packages
    required_packages = [
        'requests', 'sqlite3', 'json', 'datetime', 'time', 'logging',
        'urllib3', 'ssl', 'socket', 'threading'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - Available")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
    
    return len(missing_packages) == 0

def check_file_permissions():
    """Check file permissions for critical files"""
    print("\n📁 FILE PERMISSIONS CHECK")
    print("=" * 50)
    
    critical_files = [
        'background_updater.py',
        'database.db',
        'nfl_fantasy.db',
        'app.py',
        'config.py'
    ]
    
    permission_issues = []
    
    for filename in critical_files:
        if os.path.exists(filename):
            stat_info = os.stat(filename)
            permissions = oct(stat_info.st_mode)[-3:]
            readable = os.access(filename, os.R_OK)
            writable = os.access(filename, os.W_OK)
            executable = os.access(filename, os.X_OK) if filename.endswith('.py') else True
            
            status = "✅" if (readable and writable and executable) else "❌"
            print(f"{status} {filename} - Permissions: {permissions} (R:{readable} W:{writable} X:{executable})")
            
            if not (readable and writable and executable):
                permission_issues.append(filename)
        else:
            print(f"❌ {filename} - FILE NOT FOUND")
            permission_issues.append(filename)
    
    return len(permission_issues) == 0

def check_database_access():
    """Check database connectivity and structure"""
    print("\n🗃️  DATABASE ACCESS CHECK")
    print("=" * 50)
    
    db_files = ['database.db', 'nfl_fantasy.db']
    db_accessible = False
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Check if main tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                print(f"✅ {db_file} - Accessible")
                print(f"   Tables: {', '.join(tables)}")
                
                # Check for recent games
                if 'nfl_games' in tables:
                    cursor.execute("""
                        SELECT COUNT(*) as total, 
                               SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games,
                               MAX(game_date) as latest_game
                        FROM nfl_games 
                        WHERE year = 2025
                    """)
                    stats = cursor.fetchone()
                    print(f"   2025 Games: {stats[0]} total, {stats[1]} final, latest: {stats[2]}")
                
                conn.close()
                db_accessible = True
                break
                
            except Exception as e:
                print(f"❌ {db_file} - Error: {e}")
        else:
            print(f"❌ {db_file} - Not found")
    
    return db_accessible

def check_network_connectivity():
    """Check network connectivity to ESPN API"""
    print("\n🌐 NETWORK CONNECTIVITY CHECK")
    print("=" * 50)
    
    # Test URLs
    test_urls = [
        'https://www.espn.com',
        'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard',
        'https://httpbin.org/get'  # Simple test endpoint
    ]
    
    connectivity_ok = True
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10, verify=True)
            print(f"✅ {url} - Status: {response.status_code}")
        except requests.exceptions.SSLError as e:
            print(f"🔒 {url} - SSL Error: {e}")
            connectivity_ok = False
        except requests.exceptions.ConnectionError as e:
            print(f"❌ {url} - Connection Error: {e}")
            connectivity_ok = False
        except requests.exceptions.Timeout as e:
            print(f"⏰ {url} - Timeout: {e}")
            connectivity_ok = False
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
            connectivity_ok = False
    
    return connectivity_ok

def check_ssl_certificates():
    """Check SSL certificate configuration"""
    print("\n🔒 SSL CERTIFICATE CHECK")
    print("=" * 50)
    
    try:
        # Test ESPN API SSL
        hostname = 'site.api.espn.com'
        context = ssl.create_default_context()
        
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                print(f"✅ ESPN SSL - Valid certificate")
                print(f"   Subject: {cert.get('subject', 'Unknown')}")
                print(f"   Issuer: {cert.get('issuer', 'Unknown')}")
                
        return True
        
    except Exception as e:
        print(f"❌ ESPN SSL - Error: {e}")
        return False

def check_background_processes():
    """Check if background updater is running"""
    print("\n🔄 BACKGROUND PROCESS CHECK")
    print("=" * 50)
    
    try:
        # Check for Python processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        background_running = False
        python_processes = []
        
        for line in result.stdout.split('\n'):
            if 'python' in line.lower():
                python_processes.append(line.strip())
                if 'background_updater' in line:
                    background_running = True
                    print(f"✅ Background updater found: {line.strip()}")
        
        if not background_running:
            print("❌ Background updater NOT running")
            
        print(f"\n📋 All Python processes ({len(python_processes)}):")
        for proc in python_processes[:10]:  # Show first 10
            print(f"   {proc}")
        
        return background_running
        
    except Exception as e:
        print(f"❌ Process check failed: {e}")
        return False

def check_cron_jobs():
    """Check for any cron jobs related to the updater"""
    print("\n⏰ CRON JOBS CHECK")
    print("=" * 50)
    
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        
        if result.returncode == 0:
            cron_lines = result.stdout.strip().split('\n')
            relevant_crons = [line for line in cron_lines if 'background_updater' in line or 'casa' in line.lower()]
            
            if relevant_crons:
                print("✅ Found relevant cron jobs:")
                for cron in relevant_crons:
                    print(f"   {cron}")
            else:
                print("⚠️  No relevant cron jobs found")
        else:
            print("❌ No crontab found or access denied")
            
    except Exception as e:
        print(f"❌ Cron check failed: {e}")

def check_log_files():
    """Check for log files and recent entries"""
    print("\n📝 LOG FILES CHECK")
    print("=" * 50)
    
    log_files = [
        'app.log',
        'updater.log',
        'background_updater.log',
        'nohup.out'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                print(f"✅ {log_file} - {len(lines)} lines")
                
                # Show last few lines
                if lines:
                    print("   Last 3 lines:")
                    for line in lines[-3:]:
                        print(f"   {line.strip()}")
                        
            except Exception as e:
                print(f"❌ {log_file} - Error reading: {e}")
        else:
            print(f"❌ {log_file} - Not found")

def generate_fix_commands():
    """Generate specific fix commands for Ubuntu"""
    print("\n🔧 RECOMMENDED FIX COMMANDS")
    print("=" * 50)
    
    commands = [
        "# 1. Check if background updater is running",
        "ps aux | grep background_updater",
        "",
        "# 2. Kill any existing background updater processes",
        "pkill -f background_updater",
        "",
        "# 3. Fix file permissions",
        "chmod +x background_updater.py",
        "chmod 664 *.db",
        "",
        "# 4. Install/update required Python packages",
        "pip3 install --upgrade requests urllib3 certifi",
        "",
        "# 5. Start background updater with logging",
        "nohup python3 background_updater.py > updater.log 2>&1 &",
        "",
        "# 6. Verify it's running",
        "ps aux | grep background_updater",
        "tail -f updater.log",
        "",
        "# 7. Test ESPN API manually",
        "curl -I https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
        "",
        "# 8. Check SSL certificates",
        "curl -v https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard 2>&1 | grep -i ssl"
    ]
    
    for cmd in commands:
        print(cmd)

def main():
    """Run comprehensive Ubuntu API diagnostics"""
    print("🏈 UBUNTU API DIAGNOSTIC TOOL")
    print("=" * 70)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📂 Working directory: {os.getcwd()}")
    
    # Run all checks
    checks = [
        ("Python Environment", check_python_environment),
        ("File Permissions", check_file_permissions),
        ("Database Access", check_database_access),
        ("Network Connectivity", check_network_connectivity),
        ("SSL Certificates", check_ssl_certificates),
        ("Background Processes", check_background_processes),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            results[check_name] = False
    
    # Additional checks that don't return boolean
    check_cron_jobs()
    check_log_files()
    
    # Summary
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} checks passed")
    
    if passed < total:
        print("\n🚨 CRITICAL ISSUES DETECTED")
        generate_fix_commands()
    else:
        print("\n✅ All checks passed - API should be working")
    
    # Save report
    report_file = f"ubuntu_diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    print(f"\n📄 Report will be saved to: {report_file}")

if __name__ == "__main__":
    main()
