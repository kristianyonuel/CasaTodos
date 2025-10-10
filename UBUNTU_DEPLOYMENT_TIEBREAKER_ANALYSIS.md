# Ubuntu Server Deployment - Tiebreaker Changes Analysis

## 🎯 **KEY QUESTION: Will the NEW tiebreaker changes work automatically on Ubuntu server?**

**Answer: YES, but requires proper deployment steps**

---

## 📊 **Current Status Summary**

### ✅ **What's Already Done (Local)**
- `scoring_updater.py` enhanced with NEW tiebreaker logic
- `background_updater.py` continues working (triggers scoring)
- Week 4 manually corrected with guillermo as winner
- Changes committed and pushed to Git repository

### 🔄 **What Needs Ubuntu Server Deployment**
- Updated `scoring_updater.py` with NEW tiebreaker calculations
- Updated `background_updater.py` (if any changes were made)
- Database with corrected Week 4 results

---

## 🚀 **Ubuntu Server Deployment Plan**

### **Step 1: Update Code on Server**
```bash
# SSH to your Ubuntu server
ssh username@your-server-ip

# Navigate to project directory
cd /home/casa/CasaTodos

# Pull latest changes from Git
git pull origin main

# Verify files updated
ls -la scoring_updater.py background_updater.py
```

### **Step 2: Database Sync**
You have two options:

#### **Option A: Upload Corrected Database**
```bash
# From your local machine, upload the corrected database
scp nfl_fantasy.db username@server-ip:/home/casa/CasaTodos/

# Or if server expects different filename:
scp nfl_fantasy.db username@server-ip:/home/casa/CasaTodos/database.db
```

#### **Option B: Let Server Recalculate (Recommended)**
```bash
# SSH to server
ssh username@your-server-ip
cd /home/casa/CasaTodos

# Activate virtual environment
source venv/bin/activate

# Run scoring updater with NEW logic to recalculate Week 4
python scoring_updater.py --week 4 --year 2025

# This will apply NEW tiebreaker rules and set guillermo as winner
```

### **Step 3: Restart Background Services**
```bash
# Check if systemd service is running
sudo systemctl status lacasadetodos.service

# Restart the main Flask app service
sudo systemctl restart lacasadetodos.service

# Check if background updater is running separately
ps aux | grep background_updater.py

# If not running as part of main service, start it
cd /home/casa/CasaTodos
source venv/bin/activate
nohup python background_updater.py &
```

### **Step 4: Verify Deployment**
```bash
# Check application logs
sudo journalctl -u lacasadetodos.service -f

# Test the tiebreaker system
python -c "
from scoring_updater import calculate_weekly_winner
result = calculate_weekly_winner(4, 2025)
print(f'Week 4 Winner: {result}')
"

# Verify database state
python -c "
import sqlite3
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()
cursor.execute('SELECT u.username FROM weekly_results wr JOIN users u ON wr.user_id = u.id WHERE wr.week = 4 AND wr.year = 2025 AND wr.is_winner = 1')
winner = cursor.fetchone()
print(f'Week 4 Winner in DB: {winner[0] if winner else \"None\"}')
conn.close()
"
```

---

## 🔄 **Automatic Future Behavior on Ubuntu**

### **For Week 5 and Beyond:**
1. **Monday Night games finish** (ESPN API detects final scores)
2. **background_updater.py** detects completed games every 15 minutes
3. **scoring_updater.py** automatically triggered with NEW tiebreaker logic
4. **weekly_results table** updated with correct winner using NEW rules
5. **No manual intervention needed**

### **Background Service Architecture:**
```
ESPN API → background_updater.py → scoring_updater.py → Database Update
   ↑              (Every 15 min)        (NEW Logic)        (Automatic)
Live Scores      Game Detection      Tiebreaker Calc    Winner Storage
```

---

## ⚠️ **Potential Ubuntu-Specific Issues**

### **1. Virtual Environment Path**
- Service file: `/home/casa/CasaTodos/venv/bin/python`
- Verify this path exists and has required packages

### **2. Database File Location**
- App might expect `database.db` but you have `nfl_fantasy.db`
- Check `config.py` or database connection code
- Use symlink if needed: `ln -s nfl_fantasy.db database.db`

### **3. File Permissions**
```bash
# Ensure proper ownership
sudo chown -R casa:casa /home/casa/CasaTodos
chmod +x scoring_updater.py background_updater.py
```

### **4. Python Dependencies**
```bash
# Verify all packages installed in venv
source venv/bin/activate
pip list | grep -E "(requests|sqlite|flask)"
```

---

## 🎯 **Verification Checklist**

After deployment, verify these work:

- [ ] **Flask app starts**: `sudo systemctl status lacasadetodos.service`
- [ ] **Background updater running**: `ps aux | grep background_updater`
- [ ] **Database accessible**: Can connect to nfl_fantasy.db/database.db
- [ ] **NEW tiebreaker logic**: Week 4 shows guillermo as winner
- [ ] **Automatic updates**: Future Monday games trigger scoring
- [ ] **Web interface**: Leaderboards show correct data

---

## 📋 **Quick Deployment Commands**

```bash
# Complete deployment in one go:
ssh username@your-server-ip << 'EOF'
cd /home/casa/CasaTodos
git pull origin main
source venv/bin/activate
python scoring_updater.py --week 4 --year 2025
sudo systemctl restart lacasadetodos.service
ps aux | grep background_updater || (nohup python background_updater.py &)
EOF
```

---

## 🔍 **Troubleshooting**

### **If Week 4 Winner Still Wrong:**
```bash
# Force recalculation with NEW logic
python scoring_updater.py --force-recalculate --week 4 --year 2025
```

### **If Background Updater Not Working:**
```bash
# Check logs
tail -f app.log
# Look for background updater messages

# Restart manually
pkill -f background_updater.py
nohup python background_updater.py &
```

### **If Database Issues:**
```bash
# Check database file
ls -la *.db
# Should see nfl_fantasy.db with recent timestamp

# Test database connection
python -c "import sqlite3; print(sqlite3.connect('nfl_fantasy.db').execute('SELECT COUNT(*) FROM weekly_results WHERE week=4').fetchone())"
```

---

## ✅ **FINAL ANSWER**

**YES**, the NEW tiebreaker changes will work automatically on Ubuntu server AFTER:

1. **Code Update**: `git pull` to get enhanced scoring_updater.py
2. **Database Update**: Either upload corrected DB or run scoring recalculation
3. **Service Restart**: Restart Flask app and background services
4. **Verification**: Confirm Week 4 shows guillermo as winner

**Future weeks will be 100% automatic** with no manual intervention needed.

The Ubuntu server will behave exactly like your local system once properly deployed.