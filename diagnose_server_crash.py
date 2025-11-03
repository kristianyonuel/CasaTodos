#!/usr/bin/env python3
"""
Server Crash Diagnosis Script
============================

Checks the status of casa@20.157.116.145 and diagnoses potential crash causes.

Created: October 31, 2025
"""

import subprocess
import sys
import socket
from datetime import datetime

def check_server_status():
    print("🔍 Server Crash Diagnosis")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: casa@20.157.116.145")
    print()
    
    server_ip = "20.157.116.145"
    
    # 1. Check basic connectivity
    print("1. 🌐 Testing Network Connectivity...")
    try:
        result = subprocess.run(['ping', '-n', '4', server_ip], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Server is reachable via ping")
            # Extract ping statistics
            lines = result.stdout.split('\n')
            for line in lines:
                if 'packets' in line.lower() or 'average' in line.lower():
                    print(f"      {line.strip()}")
        else:
            print("   ❌ Server is not responding to ping")
            print("   🚨 This indicates network/server is completely down")
    except subprocess.TimeoutExpired:
        print("   ⏱️ Ping timeout - server may be severely overloaded")
    except Exception as e:
        print(f"   ❌ Ping failed: {e}")
    
    print()
    
    # 2. Check SSH connectivity
    print("2. 🔐 Testing SSH Connectivity...")
    try:
        # Test if SSH port is open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((server_ip, 22))
        sock.close()
        
        if result == 0:
            print("   ✅ SSH port (22) is open")
            print("   💡 You can try: ssh casa@20.157.116.145")
        else:
            print("   ❌ SSH port (22) is not accessible")
            print("   🚨 SSH service may be down or blocked")
    except Exception as e:
        print(f"   ❌ SSH connectivity test failed: {e}")
    
    print()
    
    # 3. Check HTTP/Web services
    print("3. 🌐 Testing Web Services...")
    
    # Common web ports to check
    web_ports = [80, 443, 5000, 8000, 8080]
    
    for port in web_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((server_ip, port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ Port {port} is open")
            else:
                print(f"   ❌ Port {port} is closed")
        except Exception as e:
            print(f"   ❌ Port {port} test failed: {e}")
    
    print()
    
    # 4. DNS Resolution
    print("4. 🔍 DNS Resolution Check...")
    try:
        hostname = socket.gethostbyaddr(server_ip)
        print(f"   ✅ Reverse DNS: {hostname[0]}")
    except socket.herror:
        print("   ⚠️ No reverse DNS entry found")
    except Exception as e:
        print(f"   ❌ DNS lookup failed: {e}")
    
    print()
    
    # 5. Provide common crash troubleshooting
    print("5. 🛠️ Common Crash Causes & Solutions:")
    print("-" * 40)
    
    print("   💾 Disk Space Issues:")
    print("      - Check: df -h")
    print("      - Solution: Clean logs, temp files")
    print()
    
    print("   🧠 Memory Issues:")
    print("      - Check: free -h, top, htop")
    print("      - Solution: Restart services, add swap")
    print()
    
    print("   🔧 Service Crashes:")
    print("      - Check: systemctl status nginx")
    print("      - Check: systemctl status apache2")
    print("      - Check: ps aux | grep python")
    print("      - Check: journalctl -xe")
    print()
    
    print("   📁 Log Files to Check:")
    print("      - /var/log/syslog")
    print("      - /var/log/nginx/error.log") 
    print("      - /var/log/apache2/error.log")
    print("      - ~/.pm2/logs/ (if using PM2)")
    print("      - Application logs in project directory")
    print()
    
    print("   🔄 Restart Commands:")
    print("      - sudo systemctl restart nginx")
    print("      - sudo systemctl restart apache2")
    print("      - sudo reboot (if necessary)")
    print("      - pm2 restart all (if using PM2)")
    print()
    
    # 6. SSH connection commands
    print("6. 🔧 Diagnostic Commands to Run:")
    print("-" * 35)
    print("   If you can SSH in:")
    print("   ssh casa@20.157.116.145")
    print()
    print("   Then run these diagnostic commands:")
    print("   sudo systemctl status --failed")
    print("   df -h")
    print("   free -h")
    print("   top -n 1")
    print("   tail -50 /var/log/syslog")
    print("   systemctl status nginx")
    print("   systemctl status apache2")
    print("   ps aux | grep python")
    print()
    
    # 7. Azure-specific checks
    print("7. ☁️ Azure-Specific Checks:")
    print("-" * 25)
    print("   - Check Azure Portal for VM status")
    print("   - Verify VM hasn't been deallocated")
    print("   - Check Azure Resource Health")
    print("   - Review Activity Log for errors")
    print("   - Check Network Security Group rules")
    print("   - Verify public IP assignment")
    print()
    
    print("🎯 IMMEDIATE ACTIONS:")
    print("=" * 30)
    print("1. Try SSH connection first")
    print("2. If SSH works, check system resources")
    print("3. If SSH fails, check Azure Portal")
    print("4. Review logs for crash cause")
    print("5. Restart services as needed")

if __name__ == "__main__":
    check_server_status()