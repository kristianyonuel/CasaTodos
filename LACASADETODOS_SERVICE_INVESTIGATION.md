# La Casa de Todos Service Investigation

## Correct Service Name: lacasadetodos

Now we can get the actual crash logs from the systemd service.

## Commands to Run on Server:

### 1. Check Service Status and Recent Logs
```bash
# Check current service status
sudo systemctl status lacasadetodos

# Get recent service logs (most important)
sudo journalctl -u lacasadetodos --no-pager -n 100

# Look for errors and crashes in recent logs
sudo journalctl -u lacasadetodos --since "24 hours ago" --no-pager | grep -i -E "(error|exception|traceback|failed|crashed|killed)"

# Check logs from last restart
sudo journalctl -u lacasadetodos --since "$(sudo systemctl show lacasadetodos -p ActiveEnterTimestamp --value)" --no-pager
```

### 2. Check Service Configuration
```bash
# See how the service is configured
sudo systemctl cat lacasadetodos

# Check if service has auto-restart enabled
sudo systemctl show lacasadetodos | grep -i restart
```

### 3. Check for Memory/Resource Issues
```bash
# Check if service was killed due to memory limits
sudo journalctl -u lacasadetodos --no-pager | grep -i -E "(oom|memory|killed|limit)"

# Check current resource usage
sudo systemctl status lacasadetodos | grep -E "(Memory|Tasks)"
```

### 4. Look for Specific Error Patterns
```bash
# Python exceptions and tracebacks
sudo journalctl -u lacasadetodos --no-pager | grep -A10 -B5 "Traceback"

# Database errors
sudo journalctl -u lacasadetodos --no-pager | grep -i -E "(database|sqlite|lock)"

# Network/API errors
sudo journalctl -u lacasadetodos --no-pager | grep -i -E "(timeout|connection|api|espn)"

# Background updater errors
sudo journalctl -u lacasadetodos --no-pager | grep -i "background"
```

### 5. Check Service Restart History
```bash
# Show service restart history
sudo journalctl -u lacasadetodos --no-pager | grep -E "(Started|Stopped|Failed|Reloading)"

# Count how many times service has restarted recently
sudo journalctl -u lacasadetodos --since "7 days ago" --no-pager | grep -c "Started"
```

## Expected Findings:

The service logs should reveal:
- **Python exceptions** causing crashes
- **Memory limit** issues 
- **Database problems** (locks, corruption)
- **Network timeouts** with ESPN API
- **Background updater failures**

## Most Common Flask Service Crash Causes:

1. **Unhandled Exceptions**: Python errors not caught
2. **Memory Leaks**: Gradual memory growth until system limit
3. **Database Locks**: SQLite deadlocks freezing the app
4. **Network Timeouts**: ESPN API calls hanging
5. **Threading Issues**: Background updater conflicts

Run the service status and recent logs first - that should show us exactly what's happening!