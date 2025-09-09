# Remote Server Database Update Guide

## Steps to Update Your Remote Server

### 1. Deploy Updated Code
```bash
# On your remote server, pull the latest changes
git pull origin main

# Make sure your virtual environment is activated
source venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate    # Windows

# Install any new dependencies
pip install -r requirements.txt
```

### 2. Stop the Running Application
```bash
# Stop your Flask app (method depends on how you're running it)
sudo systemctl stop your-app-name
# OR
pkill -f "python.*app.py"
# OR kill the process running on your port
```

### 3. Run the Database Fix Script
```bash
# Run the production fix script
python production_database_fix.py
```

### 4. Restart Your Application
```bash
# Restart your Flask app
sudo systemctl start your-app-name
# OR
python app.py
# OR however you normally start it
```

## Alternative: Manual Database Update

If you prefer to do it manually on the remote server:

### Step 1: Backup the database
```bash
cp nfl_fantasy.db nfl_fantasy_backup_$(date +%Y%m%d_%H%M%S).db
```

### Step 2: Run the fix commands
```bash
python -c "
import sqlite3
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Fix all NULL is_correct values
cursor.execute('''
    UPDATE user_picks 
    SET is_correct = CASE 
        WHEN selected_team = (CASE 
            WHEN g.home_score > g.away_score THEN g.home_team
            WHEN g.away_score > g.home_score THEN g.away_team
            ELSE 'TIE'
        END) THEN 1 
        ELSE 0 
    END
    FROM nfl_games g 
    WHERE user_picks.game_id = g.id 
    AND g.week = 1 AND g.year = 2025 AND g.is_final = 1
    AND user_picks.is_correct IS NULL
''')

# Fix coyote's prediction if needed
cursor.execute('''
    UPDATE user_picks 
    SET predicted_away_score = 27, predicted_home_score = 21 
    WHERE id IN (
        SELECT p.id FROM user_picks p
        JOIN nfl_games g ON p.game_id = g.id
        JOIN users u ON p.user_id = u.id
        WHERE u.username = \"coyote\" 
        AND g.week = 1 AND g.year = 2025
        AND g.home_team = \"CHI\" AND g.away_team = \"MIN\"
        AND p.predicted_away_score != 27
    )
''')

conn.commit()
conn.close()
print('Database fixed!')
"
```

### Step 3: Update weekly results
```bash
python -c "
from scoring_updater import ScoringUpdater
updater = ScoringUpdater()
success = updater.update_weekly_results(1, 2025)
print('Weekly results updated!' if success else 'Failed to update')
"
```

## Verification

After running the fix, verify it worked:

```bash
python verify_final_results.py
```

You should see:
- coyote: 13 correct picks (ranked #1)
- raymond: 13 correct picks (ranked #2) 
- vizca: 13 correct picks (ranked #3)
- All other users with their correct scores

## Troubleshooting

If something goes wrong:
1. Restore from backup: `cp nfl_fantasy_backup_*.db nfl_fantasy.db`
2. Check the error messages
3. Make sure the updated code is properly deployed
4. Verify the database file permissions

## What This Fixes

✅ All NULL is_correct values → proper 1/0 values
✅ Coyote's reversed Monday Night prediction 
✅ Monday Night tiebreaker logic using correct winner priority
✅ Updated weekly results and leaderboard rankings
