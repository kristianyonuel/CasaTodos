# Flask App Ubuntu Deployment Guide

## Prerequisites for Ubuntu Server

### 1. Update System and Install Python
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv sqlite3 git -y
```

### 2. Clone Your Repository
```bash
git clone https://github.com/kristianyonuel/CasaTodos.git
cd CasaTodos
```

### 3. Create Python Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Required Packages
```bash
pip install -r requirements.txt
```
*If requirements.txt doesn't exist, install manually:*
```bash
pip install Flask Werkzeug requests python-dotenv pytz reportlab pillow blinker
```

### 5. Set Up Database
Ensure both database files exist:
```bash
ls -la *.db
```
You should see:
- `database.db` (319,488 bytes)
- `nfl_fantasy.db` (319,488 bytes)

### 6. Run the Flask Application

#### Development Mode (Debug):
```bash
python3 app.py
```

#### Production Mode (with Gunicorn):
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn (recommended for production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Background/Daemon Mode:
```bash
# Using nohup for background execution
nohup python3 app.py > app.log 2>&1 &

# Check if it's running
ps aux | grep python3
```

### 7. Check Application Status

#### Test Local Connection:
```bash
curl http://localhost:5000/health
```

#### Check Logs:
```bash
# If running in background
tail -f app.log

# If using systemd service
sudo journalctl -u casa-todos -f
```

### 8. Firewall Configuration (if needed)
```bash
# Allow Flask port (5000) through firewall
sudo ufw allow 5000
sudo ufw status
```

### 9. System Service Setup (Optional - for auto-start)

Create service file:
```bash
sudo nano /etc/systemd/system/casa-todos.service
```

Service content:
```ini
[Unit]
Description=Casa Todos NFL Fantasy App
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/CasaTodos
Environment=PATH=/path/to/CasaTodos/.venv/bin
ExecStart=/path/to/CasaTodos/.venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable casa-todos
sudo systemctl start casa-todos
sudo systemctl status casa-todos
```

## Troubleshooting Commands

### Check Database Content:
```bash
sqlite3 database.db "SELECT COUNT(*) as games FROM nfl_games;"
sqlite3 database.db "SELECT game_id, away_team || ' @ ' || home_team as matchup, is_final FROM nfl_games WHERE week = 4 AND year = 2025 LIMIT 5;"
```

### Check Python Environment:
```bash
which python3
python3 --version
pip list | grep -E "(Flask|Werkzeug|sqlite)"
```

### Monitor Application:
```bash
# Check what's running on port 5000
sudo netstat -tulpn | grep :5000

# Monitor system resources
top | grep python

# Check disk space
df -h
```

### Application Logs and Debugging:
```bash
# Enable Flask debug mode (add to app.py or environment)
export FLASK_DEBUG=1
export FLASK_ENV=development

# Run with verbose output
python3 -u app.py
```

## Quick Start Commands (Copy & Paste)

For immediate deployment on Ubuntu:

```bash
# 1. System setup
sudo apt update && sudo apt install python3 python3-pip python3-venv sqlite3 -y

# 2. Navigate to your project directory
cd /path/to/your/CasaTodos

# 3. Create and activate virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 4. Install dependencies
pip install Flask Werkzeug requests python-dotenv pytz reportlab pillow blinker

# 5. Verify databases exist
ls -la *.db

# 6. Run the application
python3 app.py
```

## Expected Output

When successful, you should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
```

The application will be accessible at:
- Local: http://localhost:5000
- Network: http://your-server-ip:5000 (if configured for external access)

## Production Deployment Notes

1. **Use Gunicorn or uWSGI** instead of Flask's built-in server
2. **Set up Nginx** as reverse proxy for better performance
3. **Configure SSL/TLS** for HTTPS
4. **Set proper environment variables** for production
5. **Regular database backups**
6. **Monitor system resources** and logs

## Security Considerations

1. Change default Flask secret key in production
2. Configure proper firewall rules
3. Use environment variables for sensitive data
4. Regular security updates
5. Monitor access logs for suspicious activity