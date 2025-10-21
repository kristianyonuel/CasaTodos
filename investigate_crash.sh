#!/bin/bash
# Server Crash Investigation Script
# Run this on the server: bash investigate_crash.sh

echo "========================================"
echo "SERVER CRASH INVESTIGATION - $(date)"
echo "========================================"

echo -e "\n=== BASIC INFO ==="
whoami
pwd
hostname
uptime

echo -e "\n=== CURRENT DIRECTORY ==="
ls -la

echo -e "\n=== PYTHON PROCESSES ==="
ps aux | grep python | grep -v grep

echo -e "\n=== FLASK/CASA PROCESSES ==="
ps aux | grep -E "(flask|casa)" | grep -v grep

echo -e "\n=== SYSTEM RESOURCES ==="
free -h
df -h .

echo -e "\n=== NETWORK PORTS ==="
netstat -tlnp 2>/dev/null | grep -E "(:5000|:80|:443)" || ss -tlnp | grep -E "(:5000|:80|:443)"

echo -e "\n=== SYSTEMD SERVICES ==="
systemctl status casa-todos 2>/dev/null || echo "casa-todos service not found"
systemctl status nginx 2>/dev/null || echo "nginx service not found"

echo -e "\n=== APPLICATION DIRECTORY ==="
if [ -d "~/CasaTodos" ]; then
    ls -la ~/CasaTodos/
elif [ -d "~/casa-todos" ]; then
    ls -la ~/casa-todos/
elif [ -d "/opt/casa-todos" ]; then
    ls -la /opt/casa-todos/
else
    echo "Application directory not found in common locations"
fi

echo -e "\n=== RECENT LOG FILES ==="
find . -name "*.log" -mtime -1 2>/dev/null

echo -e "\n=== FLASK APP LOG (if exists) ==="
if [ -f "app.log" ]; then
    echo "Found app.log - last 20 lines:"
    tail -20 app.log
else
    echo "app.log not found"
fi

echo -e "\n=== SYSTEM LOGS ==="
echo "Recent syslog entries:"
tail -10 /var/log/syslog 2>/dev/null || tail -10 /var/log/messages 2>/dev/null || echo "System logs not accessible"

echo -e "\n=== RECENT CRASHES ==="
journalctl --no-pager -n 20 | grep -i -E "(error|crash|fail|exception)" || echo "No recent error messages in journal"

echo -e "\n=== PYTHON ENVIRONMENT ==="
which python3
python3 --version 2>/dev/null || python --version
pip3 list 2>/dev/null | grep -i flask || pip list | grep -i flask

echo -e "\n=== RECENT REBOOTS ==="
last reboot | head -3 2>/dev/null || echo "Reboot history not available"

echo -e "\n=== INVESTIGATION COMPLETE ==="
echo "$(date)"