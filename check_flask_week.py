#!/usr/bin/env python3
"""
Check what week Flask is actually looking for and what data exists
"""

import sqlite3
import os

def check_flask_week_expectations():
    """Check what week Flask thinks it should display"""
    
    print("🔍 CHECKING WHAT WEEK FLASK IS LOOKING FOR")
    print("=" * 50)
    
    db_path = 'nfl_fantasy.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check league settings for current week
    print("⚙️ LEAGUE SETTINGS:")
    cursor.execute("SELECT setting_name, setting_value FROM league_settings WHERE setting_name LIKE '%week%' OR setting_name LIKE '%current%'")
    week_settings = cursor.fetchall()
    
    if week_settings:
        for name, value in week_settings:
            print(f"   {name}: {value}")
    else:
        print("   No week-related settings found")
    
    # Check what weeks actually have complete data
    print("\n📊 WEEKS WITH COMPLETE DATA:")
    cursor.execute("""
        SELECT g.week, g.year, 
               COUNT(DISTINCT g.game_id) as games,
               COUNT(DISTINCT up.user_id) as users_with_picks,
               COUNT(up.user_id) as total_picks,
               COUNT(DISTINCT wr.user_id) as users_with_results
        FROM nfl_games g
        LEFT JOIN user_picks up ON g.game_id = up.game_id
        LEFT JOIN weekly_results wr ON g.week = wr.week AND g.year = wr.year
        GROUP BY g.week, g.year
        HAVING COUNT(DISTINCT up.user_id) > 0
        ORDER BY g.year, g.week
    """)
    
    complete_weeks = cursor.fetchall()
    
    print("   Week | Year | Games | Users | Picks | Results")
    print("   -----|------|-------|-------|-------|--------")
    for week, year, games, users, picks, results in complete_weeks:
        status = "✅" if users > 10 and results > 10 else "⚠️"
        print(f"   {status} {week:2d} | {year} |  {games:2d}   |  {users:2d}   | {picks:3d}  |   {results:2d}")
    
    # Check if there's a "current" or "active" week in any table
    print("\n🎯 CHECKING FOR CURRENT/ACTIVE WEEK MARKERS:")
    
    # Check if there's a current_week in any other table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        if 'current' in table.lower() or 'active' in table.lower():
            print(f"   Found table: {table}")
            cursor.execute(f"SELECT * FROM {table} LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                print(f"     {row}")
    
    # Check if games have any "current" or "active" flags
    cursor.execute("PRAGMA table_info(nfl_games)")
    game_columns = cursor.fetchall()
    print(f"\n📋 NFL_GAMES TABLE COLUMNS:")
    for col in game_columns:
        print(f"   {col[1]} ({col[2]})")
    
    # Check if there are any games marked as current/active
    cursor.execute("SELECT DISTINCT week, year, COUNT(*) FROM nfl_games GROUP BY week, year ORDER BY year DESC, week DESC LIMIT 5")
    recent_weeks = cursor.fetchall()
    print(f"\n📅 MOST RECENT WEEKS IN DATABASE:")
    for week, year, count in recent_weeks:
        print(f"   Week {week}, {year}: {count} games")
    
    # Check what the latest week with picks is
    cursor.execute("""
        SELECT g.week, g.year, COUNT(DISTINCT up.user_id) as users, COUNT(*) as picks
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        GROUP BY g.week, g.year
        ORDER BY g.year DESC, g.week DESC
        LIMIT 1
    """)
    
    latest_picks = cursor.fetchone()
    if latest_picks:
        week, year, users, picks = latest_picks
        print(f"\n🎯 LATEST WEEK WITH PICKS: Week {week}, {year}")
        print(f"   {users} users made {picks} picks")
        
        # Show leaderboard for this week
        cursor.execute("""
            SELECT u.username, 
                   SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
                   COUNT(*) as total
            FROM users u
            JOIN user_picks up ON u.id = up.user_id
            JOIN nfl_games g ON up.game_id = g.game_id
            WHERE g.week = ? AND g.year = ?
            GROUP BY u.id, u.username
            ORDER BY correct DESC
            LIMIT 10
        """, (week, year))
        
        leaderboard = cursor.fetchall()
        print(f"\n🏆 LEADERBOARD FOR WEEK {week}:")
        for i, (username, correct, total) in enumerate(leaderboard, 1):
            print(f"   {i:2d}. {username:12s} - {correct:2d}/{total} correct")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print("Check which week Flask is configured to show")
    print("The issue might be Flask is looking for a different week number")

if __name__ == "__main__":
    check_flask_week_expectations()