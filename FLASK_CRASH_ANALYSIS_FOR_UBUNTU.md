# Flask Server Crash Analysis Report
## Generated on: 2025-09-28 07:13:31

### 🚨 CRITICAL ISSUE IDENTIFIED
**ROOT CAUSE**: Flask is not installed in system Python installation
- System Python: `C:\Python313\python.exe`
- Flask Import: ❌ FAILED - No module named 'Flask'
- Virtual Environment: ✅ Has Flask installed properly

### System Information
- **Platform**: Windows-11-10.0.22631-SP0
- **Python Version**: 3.13.7
- **Python Executable**: C:\Python313\python.exe
- **Current Directory**: C:\Users\cjuarbe\Casa\CasaTodos
- **Timestamp**: 2025-09-28T07:13:32.219808

### Environment Variables
- FLASK_APP: Not set
- FLASK_ENV: Not set  
- FLASK_DEBUG: Not set
- PYTHONPATH: Not set

### Database Status ✅ ALL GOOD
**database.db:**
- Exists: ✅ True
- Size: 319,488 bytes
- Readable: ✅ True
- Writable: ✅ True
- Tables: 14
- Games Count: 78
- Connection Status: ✅ OK

**nfl_fantasy.db:**
- Exists: ✅ True
- Size: 319,488 bytes
- Readable: ✅ True
- Writable: ✅ True
- Tables: 14
- Games Count: 78
- Connection Status: ✅ OK

### Python Module Status
- ❌ **Flask**: FAILED - No module named 'Flask'
- ✅ sqlite3: OK
- ✅ datetime: OK
- ✅ os: OK
- ✅ sys: OK
- ✅ werkzeug: OK
- ✅ requests: OK
- ✅ pytz: OK
- ✅ reportlab: OK

### Flask App Tests
- ✅ app.py import: SUCCESS
- ✅ app.initialize_app(): SUCCESS
- ✅ Flask app object: <class 'flask.app.Flask'>
- ✅ Flask server startup: SUCCESS (when using correct Python environment)

### File Permissions ✅ ALL GOOD
- app.py: Size=187,265, Read=✅, Write=✅
- database.db: Size=319,488, Read=✅, Write=✅
- nfl_fantasy.db: Size=319,488, Read=✅, Write=✅
- requirements.txt: Size=166, Read=✅, Write=✅

### Port Availability ✅ ALL AVAILABLE
- Port 5000: ✅ AVAILABLE
- Port 8000: ✅ AVAILABLE
- Port 3000: ✅ AVAILABLE
- Port 80: ✅ AVAILABLE

### Auto-Update Status ✅ WORKING
- Weekly results table verified/created
- Updated is_correct for 208 picks in Week 1, 2025
- Updated is_correct for 208 picks in Week 2, 2025  
- Updated is_correct for 208 picks in Week 3, 2025
- Updated is_correct for 0 picks in Week 4, 2025
- ✅ Auto-updated scoring for 624 picks on app startup

---

## 🔧 SOLUTION FOR UBUNTU DEPLOYMENT

### The Problem
The Flask server crashes because it's trying to run with system Python instead of the virtual environment Python that has Flask installed.

### Ubuntu Deployment Fix

#### 1. Ensure Virtual Environment is Used
```bash
# Navigate to project directory
cd /path/to/CasaTodos

# Activate virtual environment (CRITICAL)
source .venv/bin/activate

# Verify Flask is installed
python -c "import Flask; print('Flask OK')"

# Run the application
python app.py
```

#### 2. Production Deployment with Gunicorn
```bash
# Install Gunicorn in virtual environment
source .venv/bin/activate
pip install gunicorn

# Run with Gunicorn (recommended)
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

#### 3. Systemd Service Setup (Ubuntu)
Create `/etc/systemd/system/casa-todos.service`:
```ini
[Unit]
Description=Casa Todos NFL Fantasy App
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/CasaTodos
Environment=PATH=/home/your-username/CasaTodos/.venv/bin
ExecStart=/home/your-username/CasaTodos/.venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable casa-todos
sudo systemctl start casa-todos
sudo systemctl status casa-todos
```

#### 4. Debug Commands for Ubuntu
```bash
# Check service logs
sudo journalctl -u casa-todos -f

# Check Python environment
which python
python --version
pip list | grep Flask

# Test app manually
source .venv/bin/activate
python -c "import app; print('Import OK')"

# Check database
ls -la *.db
sqlite3 database.db "SELECT COUNT(*) FROM nfl_games;"

# Check ports
sudo netstat -tulpn | grep :5000
```

### 5. Environment Variables for Production
```bash
export FLASK_APP=app.py
export FLASK_ENV=production
export PYTHONPATH=/home/your-username/CasaTodos
```

---

## 📋 UBUNTU DEPLOYMENT CHECKLIST

### Pre-deployment:
- [ ] Ubuntu server updated: `sudo apt update && sudo apt upgrade`
- [ ] Python 3.8+ installed: `python3 --version`
- [ ] Git installed: `git --version`
- [ ] Virtual environment support: `python3 -m venv --help`

### Deployment Steps:
- [ ] Clone repository: `git clone https://github.com/kristianyonuel/CasaTodos.git`
- [ ] Create virtual environment: `python3 -m venv .venv`
- [ ] Activate virtual environment: `source .venv/bin/activate`
- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Verify database files exist and have correct size (319,488 bytes)
- [ ] Test Flask import: `python -c "import Flask; print('OK')"`
- [ ] Test app import: `python -c "import app; print('OK')"`
- [ ] Start application: `python app.py`

### Troubleshooting:
- [ ] Check virtual environment is activated (prompt shows `(.venv)`)
- [ ] Verify Flask installation: `pip list | grep Flask`
- [ ] Check file permissions: `ls -la app.py *.db`
- [ ] Monitor logs: `tail -f app.log` or `journalctl -u casa-todos -f`
- [ ] Check firewall: `sudo ufw status`
- [ ] Test connectivity: `curl http://localhost:5000/health`

### Success Indicators:
- [ ] Flask server starts without errors
- [ ] Application accessible at http://localhost:5000
- [ ] Database queries work properly
- [ ] Leaderboard loads successfully
- [ ] No "module not found" errors in logs

---

**Next Steps**: Copy this entire report to your Ubuntu server for reference during deployment. The key is ensuring you use the virtual environment Python that has Flask installed, not the system Python.