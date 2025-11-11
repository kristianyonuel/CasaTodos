#!/usr/bin/env python3
"""
Check what's actually in the server database after upload
Run this on the server to diagnose the issue
"""

import sqlite3
import os

def check_server_database_status():
    """Check the current state of the server database"""
    
    print("🔍 SERVER DATABASE STATUS CHECK")
    print("=" * 40)
    
    # Check database file info
    db_path = '/home/casa/CasaTodos/nfl_fantasy.db'
    
    if os.path.exists(db_path):
        stat = os.stat(db_path)
        print(f"Database file: {db_path}")
        print(f"Size: {stat.st_size} bytes")
        print(f"Modified: {stat.st_mtime}")
    else:
        print("❌ Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check Week 9 data
        print(f"\n📊 WEEK 9 DATA CHECK:")
        
        # Games count
        cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 9 AND year = 2025")
        games_count = cursor.fetchone()[0]
        print(f"Games: {games_count}")
        
        # Picks count
        cursor.execute("""
            SELECT COUNT(*) FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.game_id
            WHERE g.week = 9 AND g.year = 2025
        """)
        picks_count = cursor.fetchone()[0]
        print(f"Picks: {picks_count}")
        
        # Weekly results count
        cursor.execute("SELECT COUNT(*) FROM weekly_results WHERE week = 9 AND year = 2025")
        results_count = cursor.fetchone()[0]
        print(f"Weekly results: {results_count}")
        
        # Current week setting
        cursor.execute("SELECT setting_value FROM league_settings WHERE setting_name = 'current_week'")
        current_week = cursor.fetchone()
        if current_week:
            print(f"Current week setting: {current_week[0]}")
        else:
            print("Current week setting: NOT SET")
        
        # Show actual leaderboard
        print(f"\n🏆 SERVER LEADERBOARD:")
        cursor.execute("""
            SELECT wr.weekly_rank, u.username, wr.correct_picks, wr.total_points
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            WHERE wr.week = 9 AND wr.year = 2025
            ORDER BY wr.weekly_rank
        """)
        
        leaderboard = cursor.fetchall()
        if leaderboard:
            for rank, username, correct, points in leaderboard:
                print(f"  {rank}. {username}: {correct} correct, {points} points")
        else:
            print("  ❌ No leaderboard data found")
        
        # Check KRISTIAN specifically
        print(f"\n🔍 KRISTIAN CHECK:")
        cursor.execute("""
            SELECT COUNT(*) FROM user_picks up
            JOIN users u ON up.user_id = u.id
            JOIN nfl_games g ON up.game_id = g.game_id
            WHERE u.username = 'kristian' AND g.week = 9 AND g.year = 2025
        """)
        kristian_picks = cursor.fetchone()[0]
        print(f"KRISTIAN's picks count: {kristian_picks}")
        
        if kristian_picks > 0:
            cursor.execute("""
                SELECT SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct
                FROM user_picks up
                JOIN users u ON up.user_id = u.id
                JOIN nfl_games g ON up.game_id = g.game_id
                WHERE u.username = 'kristian' AND g.week = 9 AND g.year = 2025
            """)
            kristian_correct = cursor.fetchone()[0]
            print(f"KRISTIAN's correct picks: {kristian_correct}")
        
        conn.close()
        
        # Diagnosis
        print(f"\n🎯 DIAGNOSIS:")
        if games_count == 14 and picks_count == 196 and results_count == 14:
            print("✅ Server database has complete Week 9 data")
            print("🔧 Issue might be Flask app caching or route problem")
        else:
            print("❌ Server database is incomplete:")
            print(f"   Expected: 14 games, 196 picks, 14 results")
            print(f"   Found: {games_count} games, {picks_count} picks, {results_count} results")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_server_database_status()