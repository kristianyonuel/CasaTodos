#!/bin/bash
# Ubuntu Deployment Script for NFL Fantasy App Monday Night Fixes
# Run this script on your Ubuntu server to deploy the latest fixes

echo "🏈 Deploying NFL Fantasy App Monday Night Fixes to Ubuntu"
echo "=========================================================="

# Navigate to the application directory
cd /path/to/your/CasaTodos  # Update this path to your actual app directory

# Pull the latest changes
echo "📥 Pulling latest changes from git..."
git pull origin main

# Check if we're running in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Activating venv..."
    source venv/bin/activate || source env/bin/activate || echo "Please activate your virtual environment manually"
fi

# Install any new dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check database integrity
echo "🔍 Checking database integrity..."
python -c "
import sqlite3
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users')
user_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 1')
game_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM user_picks WHERE game_id IN (SELECT id FROM nfl_games WHERE week = 1)')
pick_count = cursor.fetchone()[0]
print(f'Database Status:')
print(f'  Users: {user_count}')
print(f'  Week 1 Games: {game_count}')  
print(f'  Week 1 Picks: {pick_count}')
conn.close()
"

# Restart the application service
echo "🔄 Restarting application service..."

# Option 1: If using systemd service
if systemctl is-active --quiet nfl-fantasy; then
    echo "Restarting systemd service..."
    sudo systemctl restart nfl-fantasy
    sudo systemctl status nfl-fantasy --no-pager
elif systemctl is-active --quiet casa-todos; then
    echo "Restarting casa-todos service..."
    sudo systemctl restart casa-todos
    sudo systemctl status casa-todos --no-pager
else
    echo "⚠️  No systemd service found. Please restart manually:"
    echo "   Option A: Kill existing processes and restart"
    echo "   pkill -f 'python.*app.py' && nohup python app.py > app.log 2>&1 &"
    echo ""
    echo "   Option B: If using PM2"
    echo "   pm2 restart app"
    echo ""
    echo "   Option C: If using screen/tmux"
    echo "   # Kill existing screen session and start new one"
    echo "   screen -S nfl-fantasy -X quit"
    echo "   screen -dmS nfl-fantasy python app.py"
fi

echo ""
echo "✅ Deployment completed!"
echo ""
echo "🌐 Your app should now be running with the Monday Night fixes:"
echo "   - Monday Night picks are now visible even when game is in progress"
echo "   - Weekly leaderboard shows accurate standings and all user picks"
echo "   - Expandable pick details with predicted vs actual scores"
echo "   - Proper Monday Night tiebreaker status display"
echo ""
echo "📊 You can verify the fixes by:"
echo "   1. Visiting /weekly_leaderboard/1 in your browser"
echo "   2. Checking that Monday Night picks are displayed"
echo "   3. Expanding user rows to see all pick details"
echo ""
echo "🎯 After tonight's Monday Night game finishes:"
echo "   - Final scores will be automatically updated"
echo "   - Weekly winner will be determined correctly"
echo "   - Leaderboard will show final accurate standings"
