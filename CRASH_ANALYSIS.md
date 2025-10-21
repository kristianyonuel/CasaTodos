# Casa de Todos App Crash Analysis

## Problem: App crashes periodically and requires service restart

The app (process 332564) appears to be running but becomes unresponsive.
Need to identify root cause of crashes.

## Commands to Run on Server to Find Crash Cause:

### 1. Check Service Logs (Most Important)
```bash
# Check systemd service logs for casa-todos
sudo journalctl -u casa-todos --no-pager -n 100

# Check for crashes in the last 24 hours
sudo journalctl -u casa-todos --since "24 hours ago" --no-pager

# Check for Python errors/tracebacks
sudo journalctl -u casa-todos --no-pager | grep -A10 -B5 -i -E "(error|exception|traceback|crash)"
```

### 2. Check System Resource Issues
```bash
# Check memory usage - could be OOM (Out of Memory) killer
dmesg | grep -i -E "(killed|oom|memory)"
sudo journalctl --since "24 hours ago" | grep -i -E "(oom|killed|memory)"

# Check current memory usage
free -h
cat /proc/meminfo | grep -E "(MemTotal|MemAvailable|MemFree)"
```

### 3. Check Process State in Detail
```bash
# Check if process is actually responsive (zombie check)
ps aux | grep 332564
cat /proc/332564/status | grep -E "(State|VmPeak|VmSize|VmRSS)"
ls -la /proc/332564/fd/ | wc -l  # File descriptor count

# Check what the process is actually doing
strace -p 332564 -f -e trace=all 2>&1 | head -20
```

### 4. Check Database Issues
```bash
# SQLite database lock issues are common
lsof nfl_fantasy.db
ls -la nfl_fantasy.db

# Check for database corruption
sqlite3 nfl_fantasy.db "PRAGMA integrity_check;"
```

### 5. Check Flask Application Logs
```bash
# Look for errors in background updater
tail -50 background_updater.log

# Check for any Python error files
find . -name "*.log" -exec grep -l -i -E "(error|exception|traceback)" {} \;
```

### 6. Check Network/Connection Issues
```bash
# Check if too many connections are causing issues
ss -s  # Socket statistics
netstat -an | grep :80 | wc -l   # Active HTTP connections
netstat -an | grep :443 | wc -l  # Active HTTPS connections
```

## Common Flask App Crash Causes:

1. **Memory Leaks**: App gradually uses more memory until OOM killer terminates it
2. **Database Locks**: SQLite database gets locked, app hangs
3. **Thread Deadlocks**: Background updater thread conflicts with main thread  
4. **Unhandled Exceptions**: Python exceptions not caught, crash the app
5. **Resource Exhaustion**: Too many file descriptors, network connections
6. **Background Process Issues**: ESPN API calls timing out or failing

## Quick Diagnosis Steps:

1. **Check service logs first** - most crash info will be here
2. **Check for OOM kills** - Azure VM might be running out of memory
3. **Check database integrity** - SQLite corruption can cause hangs
4. **Monitor resource usage** - RAM, CPU, file descriptors

Run the service log command first - that's where the crash details will be!