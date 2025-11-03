#!/usr/bin/env python3
"""
Check what's actually on the server database
This will run on the server to diagnose the real issue
"""

import sqlite3
import os

def check_server_database():
    """Check what week data exists on the server"""
    
    print("🔍 CHECKING SERVER DATABASE")
    print("=" * 40)
    
    # Check multiple possible database locations
    possible_paths = [
        '/home/casa/CasaTodos/nfl_fantasy.db',
        '/home/casa/nfl_fantasy.db',
        './nfl_fantasy.db',
        'nfl_fantasy.db'
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            print(f"✅ Found database: {path}")
            break
    
    if not db_path:
        print("❌ No database found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current_week setting
    print("\n⚙️ LEAGUE SETTINGS:")
    cursor.execute("SELECT setting_name, setting_value FROM league_settings WHERE setting_name = 'current_week'")
    current_week = cursor.fetchone()
    if current_week:
        print(f"   current_week: {current_week[1]}")
    else:
        print("   ❌ current_week setting not found!")
    
    # Check what weeks have picks
    print("\n📝 WEEKS WITH USER PICKS:")
    cursor.execute("""
        SELECT g.week, g.year, COUNT(DISTINCT up.user_id) as users, COUNT(*) as picks
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        GROUP BY g.week, g.year
        ORDER BY g.year, g.week
    """)
    
    pick_weeks = cursor.fetchall()
    if pick_weeks:
        for week, year, users, picks in pick_weeks:
            print(f"   Week {week}, {year}: {users} users, {picks} picks")
    else:
        print("   ❌ No user picks found!")
    
    # Check Week 9 specifically
    print("\n🎯 WEEK 9 CHECK:")
    cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 9 AND year = 2025")
    week9_games = cursor.fetchone()[0]
    print(f"   Games: {week9_games}")
    
    cursor.execute("""
        SELECT COUNT(*) FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
    """)
    week9_picks = cursor.fetchone()[0]
    print(f"   Picks: {week9_picks}")
    
    if week9_picks > 0:
        print("\n🏆 WEEK 9 LEADERBOARD:")
        cursor.execute("""
            SELECT u.username, 
                   SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
                   COUNT(*) as total
            FROM users u
            JOIN user_picks up ON u.id = up.user_id
            JOIN nfl_games g ON up.game_id = g.game_id
            WHERE g.week = 9 AND g.year = 2025
            GROUP BY u.id, u.username
            ORDER BY correct DESC
            LIMIT 5
        """)
        
        leaderboard = cursor.fetchall()
        for i, (username, correct, total) in enumerate(leaderboard, 1):
            print(f"   {i}. {username}: {correct}/{total}")
    
    conn.close()
    
    print(f"\n🎯 SERVER DATABASE STATUS:")
    if week9_games == 0:
        print("❌ Server has NO Week 9 games")
    elif week9_picks == 0:
        print("❌ Server has Week 9 games but NO picks")
    elif week9_picks < 196:
        print(f"⚠️  Server has partial Week 9 data ({week9_picks}/196 picks)")
    else:
        print("✅ Server has complete Week 9 data")
        print("   Issue might be Flask route or template problem")

if __name__ == "__main__":
    check_server_database()