# 🚀 La Casa de Todos - Remote Server Deployment Guide

## Quick Deployment Commands

### 1. **Deploy to Remote Server**
```bash
# On your remote server, run:
cd /home/casa/CasaTodos
git pull origin main
chmod +x deploy_ubuntu.sh
./deploy_ubuntu.sh
```

### 2. **Check Service Status**
```bash
# Check if lacasadetodos service is running
sudo systemctl status lacasadetodos

# View real-time logs
sudo journalctl -u lacasadetodos -f

# Check application logs
tail -f /home/casa/CasaTodos/app.log
```

### 3. **Manual Service Control**
```bash
# Start service
sudo systemctl start lacasadetodos

# Stop service
sudo systemctl stop lacasadetodos

# Restart service
sudo systemctl restart lacasadetodos

# Enable auto-start on boot
sudo systemctl enable lacasadetodos
```

## 🔧 Auto-Restart Configuration

### Systemd Auto-Restart (Primary)
Your `lacasadetodos.service` is configured with:
- **Restart=always**: Automatically restarts on any failure
- **RestartSec=10**: Waits 10 seconds between restart attempts
- **StartLimitBurst=5**: Max 5 restart attempts in the interval
- **StartLimitIntervalSec=300**: 5-minute interval for restart limits

### Process Watchdog (Secondary)
For additional monitoring, you can run the watchdog script:

```bash
# Make watchdog executable
chmod +x lacasadetodos_watchdog.sh

# Run watchdog in background
nohup ./lacasadetodos_watchdog.sh > watchdog.log 2>&1 &

# Or create a systemd service for the watchdog
sudo cp lacasadetodos-watchdog.service /etc/systemd/system/
sudo systemctl enable lacasadetodos-watchdog
sudo systemctl start lacasadetodos-watchdog
```

## 🏥 Health Check Endpoints

Your app now includes health monitoring:

- **Simple Check**: `http://your-domain.com/health/simple`
  - Returns: `OK` (200) or error (500)
  
- **Detailed Check**: `http://your-domain.com/health`
  - Returns JSON with database status, user count, etc.

## 📋 Complete Deployment Process

### Step 1: Initial Setup (One-time)
```bash
# SSH to your remote server
ssh your-user@your-server-ip

# Navigate to app directory
cd /home/casa/CasaTodos

# Pull latest code
git pull origin main

# Setup service
sudo cp lacasadetodos.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lacasadetodos
```

### Step 2: Deploy Updates
```bash
# Run deployment script
chmod +x deploy_ubuntu.sh
./deploy_ubuntu.sh
```

### Step 3: Verify Deployment
```bash
# Check service status
sudo systemctl status lacasadetodos

# Test health endpoints
curl http://localhost/health/simple
curl http://localhost/health

# Check logs
tail -f app.log
```

## 🔥 Troubleshooting Auto-Restart Issues

### Service Won't Start
```bash
# Check service logs
sudo journalctl -u lacasadetodos -n 50

# Check file permissions
ls -la /home/casa/CasaTodos/
sudo chown -R root:root /home/casa/CasaTodos/venv
sudo chmod +x /home/casa/CasaTodos/app.py

# Test manual start
cd /home/casa/CasaTodos
source venv/bin/activate
python app.py production
```

### Service Keeps Restarting
```bash
# Check application logs
tail -f /home/casa/CasaTodos/app.log

# Check system resources
free -h
df -h
top

# Check ports
sudo netstat -tlnp | grep -E ":80|:443"
sudo lsof -i :80
```

### Health Checks Failing
```bash
# Test health endpoints manually
curl -v http://localhost/health/simple
curl -v http://localhost/health

# Check database connectivity
cd /home/casa/CasaTodos
source venv/bin/activate
python -c "
import sqlite3
conn = sqlite3.connect('nfl_fantasy.db')
print('Database OK')
conn.close()
"
```

## 📊 Monitoring Commands

### Real-time Monitoring
```bash
# Service status
watch -n 5 'sudo systemctl status lacasadetodos'

# Application logs
tail -f /home/casa/CasaTodos/app.log

# System logs
sudo journalctl -u lacasadetodos -f

# Resource usage
htop
```

### Health Check Script
```bash
# Create simple monitoring script
cat > check_health.sh << 'EOF'
#!/bin/bash
echo "=== Service Status ==="
sudo systemctl is-active lacasadetodos

echo "=== Health Check ==="
curl -s http://localhost/health/simple || echo "Health check failed"

echo "=== Recent Logs ==="
sudo journalctl -u lacasadetodos -n 5 --no-pager
EOF

chmod +x check_health.sh
./check_health.sh
```

## 🛡️ Security Notes

- Service runs as root (required for ports 80/443)
- Logs are written to `/home/casa/CasaTodos/app.log`
- Database and app files are protected with proper permissions
- Network capabilities limited to binding privileged ports

## 📱 Remote Monitoring Options

### Option 1: Simple HTTP Monitoring
Set up a cron job to check health:
```bash
# Add to crontab
*/5 * * * * curl -f http://localhost/health/simple > /dev/null 2>&1 || echo "Health check failed at $(date)" >> /home/casa/health_failures.log
```

### Option 2: External Monitoring
Use services like:
- UptimeRobot
- Pingdom  
- StatusCake

Monitor these URLs:
- `http://your-domain.com/health/simple`
- `http://your-domain.com/`

### Option 3: Log Monitoring
Monitor application logs for errors:
```bash
# Alert on specific errors
tail -f /home/casa/CasaTodos/app.log | grep -i "error\|exception\|failed" >> /home/casa/error_alerts.log
```

## 🚀 Quick Recovery Commands

If everything fails, use these commands to get back online quickly:

```bash
# Nuclear option - kill everything and restart
sudo pkill -f "python.*app.py"
sudo systemctl stop lacasadetodos
sleep 5
sudo systemctl start lacasadetodos

# Check status
sudo systemctl status lacasadetodos
curl http://localhost/health/simple
```

## 📞 Support

If issues persist:
1. Check the health endpoints: `/health` and `/health/simple`
2. Review application logs: `tail -f app.log`
3. Check system logs: `sudo journalctl -u lacasadetodos -f`
4. Verify database connectivity
5. Check system resources (disk space, memory, CPU)

Your server now has comprehensive auto-restart capabilities and monitoring!
