#!/usr/bin/env python3
"""
Copy local database changes to server
Since local database has all Week 9 data correctly, we need to sync it to server
"""

import sqlite3
import os
import subprocess

def copy_database_to_server():
    """Copy the local database to server and restart Flask"""
    
    print("🔄 COPYING LOCAL DATABASE TO SERVER")
    print("=" * 50)
    
    local_db = 'nfl_fantasy.db'
    if not os.path.exists(local_db):
        print(f"❌ Local database not found: {local_db}")
        return
    
    # First, let's verify our local data one more time
    print("✅ Verifying local database data...")
    conn = sqlite3.connect(local_db)
    cursor = conn.cursor()
    
    # Check Week 9 data
    cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 9 AND year = 2025")
    games = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
    """)
    picks = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM weekly_results WHERE week = 9 AND year = 2025")
    results = cursor.fetchone()[0]
    
    print(f"   Week 9 games: {games}")
    print(f"   Week 9 picks: {picks}")
    print(f"   Week 9 results: {results}")
    
    if games == 14 and picks == 196 and results == 14:
        print("✅ Local database is perfect!")
    else:
        print("❌ Local database has issues!")
        return
    
    # Show current leaderboard
    cursor.execute("""
        SELECT wr.weekly_rank, u.username, wr.correct_picks, wr.total_points
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.week = 9 AND wr.year = 2025
        ORDER BY wr.weekly_rank ASC
        LIMIT 5
    """)
    
    leaderboard = cursor.fetchall()
    print("\n🏆 Current leaderboard (top 5):")
    for rank, username, correct, points in leaderboard:
        print(f"   {rank}. {username}: {correct}/14 correct ({points} pts)")
    
    conn.close()
    
    print("\n📤 Now we need to copy this to the server...")
    print("\n💡 COPY INSTRUCTIONS:")
    print("1. Upload local database to server")
    print("2. Replace server database")
    print("3. Restart Flask service")
    
    # Create the upload script
    upload_script = '''
# Upload local database to server
scp nfl_fantasy.db casa@20.157.116.145:/home/casa/CasaTodos/nfl_fantasy.db.new

# Connect to server and replace database
ssh casa@20.157.116.145 << 'EOF'
cd /home/casa/CasaTodos

# Backup current database
cp nfl_fantasy.db nfl_fantasy.db.backup_$(date +%s)

# Replace with new database
mv nfl_fantasy.db.new nfl_fantasy.db

# Set correct permissions
chmod 644 nfl_fantasy.db
chown casa:casa nfl_fantasy.db

# Restart Flask service
sudo systemctl stop lacasadetodos.service
sleep 3
sudo systemctl start lacasadetodos.service

echo "Database updated and service restarted!"
EOF
'''
    
    with open('upload_database.sh', 'w') as f:
        f.write(upload_script)
    
    print("\n📝 Created upload_database.sh script")
    print("\n🚀 TO DEPLOY:")
    print("   Run: bash upload_database.sh")
    print("   Or manually run the scp and ssh commands")

def check_database_differences():
    """Show what's different between what Flask expects and what we have"""
    
    print("\n🔍 CHECKING FLASK EXPECTATIONS")
    print("=" * 50)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check if Flask might be looking at different week
    print("📅 League settings - current state:")
    cursor.execute("SELECT setting_key, setting_value FROM league_settings WHERE setting_key IN ('current_season', 'current_week')")
    settings = cursor.fetchall()
    for key, value in settings:
        print(f"   {key}: {value}")
    
    # Check if there's a current_week setting that needs updating
    cursor.execute("SELECT * FROM league_settings WHERE setting_key = 'current_week'")
    current_week_setting = cursor.fetchone()
    
    if current_week_setting:
        print(f"\n⚠️  Found current_week setting: {current_week_setting[3]}")
        if current_week_setting[3] != '9':
            print("❌ current_week is not set to 9!")
            print("   Flask might be looking at the wrong week")
            
            # Update current_week to 9
            cursor.execute("UPDATE league_settings SET setting_value = '9' WHERE setting_key = 'current_week'")
            conn.commit()
            print("✅ Updated current_week to 9")
    else:
        print("\n🔧 No current_week setting found, adding it...")
        cursor.execute("""
            INSERT INTO league_settings 
            (category, setting_key, setting_value, data_type, display_name, description, is_active, is_editable)
            VALUES ('general', 'current_week', '9', 'integer', 'Current Week', 'Current NFL week', 1, 1)
        """)
        conn.commit()
        print("✅ Added current_week = 9 setting")
    
    conn.close()

if __name__ == "__main__":
    copy_database_to_server()
    check_database_differences()