# AUTOMATIC SCORING SYSTEM - WEEKLY MAINTENANCE GUIDE

## 🎯 THE BOTTOM LINE

**Your automatic scoring system is currently NOT WORKING on the remote server.**

The Buffalo game (MIA 21 - BUF 31) should have been automatically scored, but it wasn't. This means the background updater is not running properly on your server.

---

## 🔧 WEEKLY MAINTENANCE ROUTINE

### 1. **Run Weekly Monitor** (Every Monday)
```bash
python weekly_auto_monitor.py
```
This will tell you if the system is working or not.

### 2. **If Monitor Shows "NEEDS ATTENTION"**
- SSH to your server
- Check if background updater is running:
  ```bash
  ps aux | grep background_updater
  ```
- If not running, start it:
  ```bash
  nohup python background_updater.py > updater.log 2>&1 &
  ```

### 3. **Emergency Manual Fix** (When auto system fails)
```bash
python manual_score_update.py
```
- Add game results manually
- Upload corrected database to server

---

## 📋 FILES CREATED FOR YOU

### **weekly_auto_monitor.py**
- **Purpose**: Check if automatic system is working
- **When to use**: Every Monday morning
- **What it tells you**: If background updater is working properly

### **manual_score_update.py** 
- **Purpose**: Emergency manual scoring when auto system fails
- **When to use**: When monitor shows problems
- **What it does**: Manually add game scores and update picks

### **fix_remote_server_scoring.py**
- **Purpose**: One-time fix for current Buffalo game issue
- **Status**: Already applied (Buffalo game fixed)

### **check_database_download.py**
- **Purpose**: Validate database status after downloading from server
- **When to use**: To verify current state

---

## 🚨 CURRENT STATUS (Sept 19, 2025)

✅ **Fixed Locally**: Buffalo game MIA 21 - BUF 31, all 7 users scored correctly  
❌ **Server Issue**: Background updater not running  
❌ **Root Cause**: ESPN API SSL certificate errors  

## 📅 WEEKLY SCHEDULE

**Every Monday:**
1. Run `python weekly_auto_monitor.py`
2. If it shows "EXCELLENT" or "GOOD" → You're done!
3. If it shows "NEEDS ATTENTION" → Follow the recommended actions

**During the week:**
- Games should automatically score themselves
- No manual intervention needed (if system working)

**Emergency only:**
- Use `manual_score_update.py` when auto system fails
- Upload corrected database to server

---

## 🎯 GOAL: Set It and Forget It

Once you fix the background updater on your server:
- ✅ Games automatically get scored when they finish
- ✅ Weekly monitor confirms everything is working
- ✅ No more asking "why isn't the API working?" every week

The system SHOULD be fully automatic. Right now it's not because the background process isn't running on your server.

---

## 🆘 QUICK HELP

**System working?** → Run `python weekly_auto_monitor.py`  
**Need manual fix?** → Run `python manual_score_update.py`  
**Check database?** → Run `python check_database_download.py`  

**Most common issue**: Background updater not running on server
**Most common fix**: SSH to server and restart background_updater.py
