#!/usr/bin/env python3
"""
Debug weekly leaderboard display issues
Check if data exists and what queries Flask should be running
"""

import sqlite3
import os

def check_leaderboard_data():
    """Check all data needed for weekly leaderboard display"""
    
    print("🏆 CHECKING WEEKLY LEADERBOARD DATA")
    print("=" * 50)
    
    db_path = 'nfl_fantasy.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current league settings
    print("⚙️ LEAGUE SETTINGS:")
    cursor.execute("SELECT * FROM league_settings")
    settings = cursor.fetchall()
    for setting in settings:
        print(f"   {setting}")
    
    # Check what weeks have data
    print("\n📅 WEEKS WITH GAME DATA:")
    cursor.execute("SELECT DISTINCT week, year, COUNT(*) as games FROM nfl_games GROUP BY week, year ORDER BY year, week")
    weeks = cursor.fetchall()
    for week, year, count in weeks:
        print(f"   Week {week}, {year}: {count} games")
    
    # Check what weeks have user picks
    print("\n📝 WEEKS WITH USER PICKS:")
    cursor.execute("""
        SELECT g.week, g.year, COUNT(DISTINCT up.user_id) as users, COUNT(*) as picks
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        GROUP BY g.week, g.year
        ORDER BY g.year, g.week
    """)
    pick_weeks = cursor.fetchall()
    for week, year, users, picks in pick_weeks:
        print(f"   Week {week}, {year}: {users} users, {picks} picks")
    
    # Check weekly_results table
    print("\n📊 WEEKLY RESULTS DATA:")
    cursor.execute("SELECT DISTINCT week, year, COUNT(*) as entries FROM weekly_results GROUP BY week, year ORDER BY year, week")
    results_weeks = cursor.fetchall()
    for week, year, count in results_weeks:
        print(f"   Week {week}, {year}: {count} result entries")
    
    # Detailed Week 9 check
    print("\n🎯 WEEK 9 DETAILED CHECK:")
    print("-" * 30)
    
    # Week 9 games
    cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 9 AND year = 2025")
    week9_games = cursor.fetchone()[0]
    print(f"Week 9 games: {week9_games}")
    
    # Week 9 picks
    cursor.execute("""
        SELECT COUNT(*) FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
    """)
    week9_picks = cursor.fetchone()[0]
    print(f"Week 9 picks: {week9_picks}")
    
    # Week 9 results
    cursor.execute("SELECT COUNT(*) FROM weekly_results WHERE week = 9 AND year = 2025")
    week9_results = cursor.fetchone()[0]
    print(f"Week 9 results: {week9_results}")
    
    # Test the exact query Flask would use for weekly leaderboard
    print("\n🔍 FLASK LEADERBOARD QUERY TEST:")
    print("-" * 30)
    
    # This is likely what Flask is running for weekly leaderboard
    cursor.execute("""
        SELECT 
            wr.weekly_rank,
            u.username,
            wr.correct_picks,
            wr.total_points,
            wr.total_picks
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.week = 9 AND wr.year = 2025
        ORDER BY wr.weekly_rank ASC
    """)
    
    leaderboard = cursor.fetchall()
    
    if leaderboard:
        print(f"✅ Found {len(leaderboard)} leaderboard entries for Week 9:")
        print("   Rank | Username    | Correct | Points | Total")
        print("   -----|-------------|---------|--------|------")
        for rank, username, correct, points, total in leaderboard:
            print(f"   {rank:4d} | {username:11s} | {correct:7d} | {points:6d} | {total:5d}")
    else:
        print("❌ No leaderboard data found for Week 9!")
    
    # Alternative query that Flask might use
    print("\n🔄 ALTERNATIVE LEADERBOARD QUERY:")
    print("-" * 30)
    
    cursor.execute("""
        SELECT 
            u.username,
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
    
    alt_leaderboard = cursor.fetchall()
    
    if alt_leaderboard:
        print(f"✅ Alternative query found {len(alt_leaderboard)} entries:")
        print("   Username    | Correct | Points | Total")
        print("   ------------|---------|--------|------")
        for username, correct, points, total in alt_leaderboard:
            print(f"   {username:11s} | {correct:7d} | {points:6d} | {total:5d}")
    else:
        print("❌ Alternative query also returned no data!")
    
    # Check if Flask is looking for a different week
    print("\n🔍 CHECKING ALL AVAILABLE WEEKLY RESULTS:")
    print("-" * 30)
    
    cursor.execute("""
        SELECT wr.week, wr.year, COUNT(*) as entries,
               MIN(wr.weekly_rank) as min_rank, MAX(wr.weekly_rank) as max_rank
        FROM weekly_results wr
        GROUP BY wr.week, wr.year
        ORDER BY wr.year DESC, wr.week DESC
    """)
    
    all_results = cursor.fetchall()
    for week, year, count, min_rank, max_rank in all_results:
        print(f"   Week {week}, {year}: {count} entries (ranks {min_rank}-{max_rank})")
    
    # Check user table
    print("\n👥 USER COUNT CHECK:")
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"Total users in database: {user_count}")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    
    if week9_games == 14 and week9_picks == 196 and week9_results == 14:
        print("✅ All Week 9 data is present and correct")
        print("✅ Database has complete leaderboard information")
        print("🔧 Issue is likely with Flask app caching or route handling")
        print("\n💡 SOLUTIONS:")
        print("1. Restart Flask service: sudo systemctl restart lacasadetodos.service")
        print("2. Check Flask app logs for errors")
        print("3. Verify Flask route is querying the right week/year")
        print("4. Clear any Flask caching")
    else:
        print("❌ Week 9 data is incomplete:")
        print(f"   Games: {week9_games}/14")
        print(f"   Picks: {week9_picks}/196")
        print(f"   Results: {week9_results}/14")

if __name__ == "__main__":
    check_leaderboard_data()