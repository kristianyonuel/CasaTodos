# Server Database Fix - Deployment Instructions

## Problem
Server shows error: `sqlite3.OperationalError: no such table: nfl_games`
This happens when the server is looking at an empty `database.db` file instead of the populated `nfl_fantasy.db` file.

## Solution
Run the database fix tool on the server:

### Step 1: Pull Latest Changes
```bash
cd ~/CasaTodos
git pull origin main
```

### Step 2: Run Database Fix Tool
```bash
python fix_database_path.py
```

When prompted with "Apply this fix? [y/N]:", type `y` and press Enter.

### Step 3: Restart Flask Application
```bash
# Kill any running Flask processes
pkill -f "python app.py"

# Start Flask app again
python app.py
```

### Step 4: Verify Fix
Visit the weekly leaderboard page. You should now see completed games instead of "No completed games found".

## What the Fix Does
- Checks both `database.db` and `nfl_fantasy.db` files
- Copies the populated database to the location the server expects
- Preserves all existing data and user picks
- Creates a backup of the original file for safety

## Expected Results After Fix
- Weekly leaderboard shows completed games for ongoing weeks
- Week 4 should show 16 games total with 1 completed (SEA @ ARI)
- All existing user picks and data remain intact

## Troubleshooting
If the fix doesn't work:
1. Check if the Flask app restarted successfully
2. Verify both database files exist and have data
3. Check the Flask app logs for any new errors

## Files Involved
- `fix_database_path.py` - The diagnostic and fix tool
- `database.db` - Target database file (may be empty initially) 
- `nfl_fantasy.db` - Source database file (has the actual data)
- `app.py` - Flask application (uses DATABASE_PATH = 'nfl_fantasy.db')