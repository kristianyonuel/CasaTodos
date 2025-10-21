# Clear Commands for lacasadetodos Service Investigation

## Run these commands one at a time:

### 1. Check if lacasadetodos service exists and its status:
```bash
sudo systemctl status lacasadetodos
```

### 2. If that doesn't work, try these variations:
```bash
sudo systemctl status lacasa*
sudo systemctl list-units | grep casa
sudo systemctl list-units | grep todos
```

### 3. Check all Python processes to see what's running:
```bash
ps aux | grep python | grep -v grep
```

### 4. Check if there's a process running from /home/casa/CasaTodos:
```bash
ps aux | grep CasaTodos
```

### 5. Look for any casa-related systemd services:
```bash
sudo systemctl list-unit-files | grep casa
```

### 6. Check if there are any custom service files:
```bash
ls /etc/systemd/system/ | grep casa
ls /etc/systemd/system/ | grep todos
```

## Key Information Needed:

From your output, I see:
- Process 332564 is running manually (not as a service)
- Command: `/usr/bin/python3 /home/casa/CasaTodos/app.py`
- Running since Oct 14
- State: Sleeping (which could mean hung)

## Most Likely Scenario:

The app might be:
1. **Running manually** (not as a systemd service)
2. **Started in screen/tmux** session
3. **Background process** that gets stuck

Let's first confirm what service name exists, then get the logs.