#!/usr/bin/env python3
"""
Fix the Flask app issue with weekly leaderboard display
The problem is the query is getting season totals instead of weekly data
"""

import sqlite3

def fix_weekly_leaderboard():
    """Fix the weekly leaderboard query issue"""
    
    print("🔧 FIXING WEEKLY LEADERBOARD DISPLAY")
    print("=" * 50)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # The issue: Flask might be using a weekly_results table that needs updating
    print("📊 CHECKING WEEKLY_RESULTS TABLE:")
    cursor.execute("SELECT * FROM weekly_results WHERE week = 9 AND year = 2025")
    weekly_data = cursor.fetchall()
    
    if weekly_data:
        print(f"   Found {len(weekly_data)} weekly results")
        for row in weekly_data[:3]:
            print(f"     {row}")
    else:
        print("   ❌ No weekly results found - this is the problem!")
    
    # Check the structure of weekly_results
    cursor.execute("PRAGMA table_info(weekly_results)")
    columns = cursor.fetchall()
    print("   Weekly results columns:")
    for col in columns:
        print(f"     {col[1]} ({col[2]})")
    
    # Insert/update weekly results for Week 9
    print(f"\n💾 INSERTING WEEK 9 RESULTS INTO weekly_results:")
    
    # First, delete any existing Week 9 data
    cursor.execute("DELETE FROM weekly_results WHERE week = 9 AND year = 2025")
    
    # Get the correct Week 9 leaderboard
    cursor.execute("""
        SELECT u.id, u.username, 
               SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
               SUM(up.points_earned) as points,
               COUNT(*) as total_picks
        FROM users u
        JOIN user_picks up ON u.id = up.user_id
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
        GROUP BY u.id, u.username
        ORDER BY points DESC, correct DESC
    """)
    
    week9_results = cursor.fetchall()
    
    # Insert into weekly_results table
    for rank, (user_id, username, correct, points, total) in enumerate(week9_results, 1):
        cursor.execute("""
            INSERT INTO weekly_results 
            (user_id, week, year, correct_picks, total_points, total_picks, weekly_rank)
            VALUES (?, 9, 2025, ?, ?, ?, ?)
        """, (user_id, correct, points, total, rank))
        
        print(f"   {rank}. {username}: {correct}/{total} correct, {points} points")
    
    conn.commit()
    
    # Verify the fix
    print(f"\n✅ VERIFYING weekly_results:")
    cursor.execute("""
        SELECT u.username, wr.correct_picks, wr.total_points, wr.weekly_rank
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.week = 9 AND wr.year = 2025
        ORDER BY wr.weekly_rank
    """)
    
    verified_results = cursor.fetchall()
    for username, correct, points, rank in verified_results:
        print(f"     {rank}. {username}: {correct} correct, {points} points")
    
    # Also check if there's a cache table or setting that needs updating
    print(f"\n🔄 CHECKING FOR CACHE TABLES:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%cache%'")
    cache_tables = cursor.fetchall()
    if cache_tables:
        for table in cache_tables:
            print(f"   Cache table found: {table[0]}")
    else:
        print("   No cache tables found")
    
    # Update any league settings that might affect display
    cursor.execute("SELECT * FROM league_settings WHERE setting_name LIKE '%week%' OR setting_name LIKE '%display%'")
    settings = cursor.fetchall()
    if settings:
        print(f"\n⚙️ RELEVANT LEAGUE SETTINGS:")
        for setting in settings:
            print(f"   {setting}")
    
    # Force update the current week setting if it exists
    cursor.execute("UPDATE league_settings SET setting_value = '9' WHERE setting_name = 'current_week'")
    cursor.execute("UPDATE league_settings SET setting_value = '2025' WHERE setting_name = 'current_year'")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎯 WEEKLY LEADERBOARD FIX COMPLETE!")
    print("   ✅ Added Week 9 data to weekly_results table")
    print("   ✅ Set current week to 9")
    print("   🌐 Flask app should now display the leaderboard!")

if __name__ == "__main__":
    fix_weekly_leaderboard()