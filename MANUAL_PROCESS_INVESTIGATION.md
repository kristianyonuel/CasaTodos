# Casa de Todos - Manual Process Investigation

## Current Situation Analysis

### What We Found:
- Process 332564 is running manually (not as systemd service)  
- No service logs because it's not a service
- Process is in "sleeping" state (normal for Flask app)
- No recent OOM kills

### Next Investigation Steps:

```bash
# 1. Check if process is actually serving requests (CRITICAL)
curl -v http://localhost:80 --connect-timeout 10
curl -v http://localhost:443 --connect-timeout 10 -k

# 2. Check what the process is actually doing right now
sudo strace -p 332564 -f -e trace=network,file -o /tmp/strace.log &
sleep 10
sudo kill %1
cat /tmp/strace.log | tail -20

# 3. Check app output - where are the app logs going?
sudo lsof -p 332564 | grep -E "(log|out|err)"

# 4. Check background updater status
tail -20 background_updater.log

# 5. Check memory usage trend
cat /proc/332564/status | grep -E "(VmPeak|VmSize|VmRSS|Threads)"

# 6. Check for database locks
lsof nfl_fantasy.db 2>/dev/null || echo "No locks on database"

# 7. Test database integrity  
sqlite3 nfl_fantasy.db "SELECT COUNT(*) FROM users;" 2>&1

# 8. Check network connections
sudo netstat -p | grep 332564 | head -10
```

## Likely Crash Scenarios:

### 1. **Silent Hang**: Process alive but not responding to requests
- Background updater stuck in infinite loop
- Database deadlock 
- Thread synchronization issues

### 2. **Gradual Memory Leak**: Process slowly consuming memory
- Flask memory not being freed
- Database connections not closed
- Background threads accumulating

### 3. **Network Issues**: External API calls failing
- ESPN API timeouts causing hangs
- Unhandled network exceptions

### 4. **Database Problems**: SQLite issues
- Database corruption
- Lock contention between threads
- Large query performance issues

## Immediate Actions:

1. **Test if app responds** to HTTP requests
2. **Check what process is doing** with strace
3. **Look for app output** in system logs or stdout
4. **Check background updater** logs for errors

## Long-term Solution:
Convert to proper systemd service with:
- Automatic restart on crash
- Proper logging
- Resource monitoring
- Graceful shutdown handling

Run the connectivity test first - that will tell us if it's actually crashed or just appears unresponsive!