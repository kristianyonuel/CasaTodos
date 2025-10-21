# Server Crash Investigation - Manual Checklist

## Quick Commands to Run on Server (casa@20.157.116.145)

### 1. Basic Status Check
```bash
pwd                                    # Current directory
ls -la                                 # List files
whoami                                 # Current user
uptime                                 # System uptime
```

### 2. Check if Flask App is Running
```bash
ps aux | grep python                  # Python processes
ps aux | grep flask                   # Flask processes
ps aux | grep casa                    # Casa-related processes
netstat -tlnp | grep :5000           # Check port 5000
```

### 3. Check System Resources
```bash
free -h                               # Memory usage
df -h                                 # Disk usage
top -n 1                              # CPU usage snapshot
```

### 4. Check Application Logs
```bash
ls -la *.log                          # Look for log files
tail -50 app.log                      # Check Flask app log (if exists)
tail -20 /var/log/syslog              # System log
journalctl -n 20                      # Recent system messages
```

### 5. Check Service Status
```bash
systemctl status casa-todos           # Service status (if using systemd)
systemctl status nginx                # Web server status
systemctl list-failed                 # Failed services
```

### 6. Check Recent Activity
```bash
last reboot | head -3                 # Recent reboots
dmesg | tail -10                      # Kernel messages
find . -name "*.log" -mtime -1        # Recent log files
```

### 7. Check Python Environment
```bash
which python3                         # Python location
python3 --version                     # Python version
pip3 list | grep -i flask            # Flask installation
```

### 8. Look for Error Patterns
```bash
grep -i error *.log 2>/dev/null       # Errors in log files
grep -i crash *.log 2>/dev/null       # Crash mentions
grep -i exception *.log 2>/dev/null   # Python exceptions
```

## Expected Issues to Look For:

1. **Port Already in Use**: Another process using port 5000
2. **Memory Issues**: Out of memory causing crash
3. **Permission Problems**: File/directory access issues
4. **Database Lock**: SQLite database locked
5. **Python Import Errors**: Missing dependencies
6. **Service Restart**: SystemD service failed to restart

## Quick Fix Commands:

```bash
# Kill any stuck Python processes
pkill -f python

# Restart the service (if using systemd)
sudo systemctl restart casa-todos

# Manual Flask restart (if running directly)
cd /path/to/casa-todos
python3 app.py

# Check database permissions
ls -la *.db
```

Run these commands in order and report back what you find!