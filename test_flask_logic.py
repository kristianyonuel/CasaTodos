#!/usr/bin/env python3
"""
Test the Flask app leaderboard logic locally to identify the display issue
"""

import sqlite3

def test_flask_leaderboard_logic():
    """Test the exact logic Flask app might be using"""
    
    print("🧪 TESTING FLASK LEADERBOARD LOGIC")
    print("=" * 50)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Test different query variations that Flask might use
    
    print("📊 TEST 1: Basic leaderboard query")
    cursor.execute("""
        SELECT u.username, 
               SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
               SUM(up.points_earned) as points,
               COUNT(*) as total_picks
        FROM users u
        JOIN user_picks up ON u.id = up.user_id
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
        GROUP BY u.username
        ORDER BY points DESC, correct DESC
    """)
    
    results = cursor.fetchall()
    if results:
        print(f"   ✅ Results found: {len(results)} users")
        for username, correct, points, total in results[:5]:
            print(f"     {username}: {correct}/{total} correct, {points} points")
    else:
        print("   ❌ No results")
    
    print(f"\n📊 TEST 2: Check if Flask filters by is_final")
    cursor.execute("""
        SELECT u.username, 
               SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
               SUM(up.points_earned) as points
        FROM users u
        JOIN user_picks up ON u.id = up.user_id
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025 AND g.is_final = 1
        GROUP BY u.username
        ORDER BY points DESC
    """)
    
    results = cursor.fetchall()
    if results:
        print(f"   ✅ Final games results: {len(results)} users")
        for username, correct, points in results[:5]:
            print(f"     {username}: {correct} correct, {points} points")
    else:
        print("   ❌ No final games results")
    
    print(f"\n📊 TEST 3: Check if there are any NULL values causing issues")
    cursor.execute("""
        SELECT 
            COUNT(*) as total_picks,
            COUNT(up.is_correct) as non_null_correct,
            COUNT(up.points_earned) as non_null_points,
            SUM(CASE WHEN up.is_correct IS NULL THEN 1 ELSE 0 END) as null_correct,
            SUM(CASE WHEN up.points_earned IS NULL THEN 1 ELSE 0 END) as null_points
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
    """)
    
    total, non_null_correct, non_null_points, null_correct, null_points = cursor.fetchone()
    print(f"   Total picks: {total}")
    print(f"   Non-null is_correct: {non_null_correct}")
    print(f"   Non-null points_earned: {non_null_points}")
    print(f"   NULL is_correct: {null_correct}")
    print(f"   NULL points_earned: {null_points}")
    
    print(f"\n📊 TEST 4: Check specific user (JEAN - the leader)")
    cursor.execute("""
        SELECT g.away_team, g.home_team, up.selected_team, up.is_correct, up.points_earned,
               g.away_score, g.home_score, g.is_final
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        JOIN users u ON up.user_id = u.id
        WHERE u.username = 'jean' AND g.week = 9 AND g.year = 2025
        ORDER BY g.game_id
    """)
    
    jean_picks = cursor.fetchall()
    if jean_picks:
        print(f"   ✅ JEAN's picks found: {len(jean_picks)} games")
        correct_count = 0
        for away, home, pick, correct, points, away_score, home_score, is_final in jean_picks:
            status = "✅" if correct else "❌"
            if correct:
                correct_count += 1
            print(f"     {status} {away} {away_score} - {home_score} {home}: Picked {pick} ({points} pts)")
        print(f"   📊 JEAN total: {correct_count} correct")
    else:
        print("   ❌ No picks found for JEAN")
    
    # Check if Flask might be using a different table or query
    print(f"\n📊 TEST 5: Check all table schemas")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("   Available tables:")
    for table in tables:
        print(f"     - {table[0]}")
    
    # Check if there might be a cache issue
    print(f"\n🔄 FORCE UPDATE TIMESTAMPS:")
    cursor.execute("""
        UPDATE nfl_games 
        SET updated_at = datetime('now')
        WHERE week = 9 AND year = 2025
    """)
    
    cursor.execute("""
        UPDATE user_picks 
        SET created_at = datetime('now')
        WHERE game_id IN (SELECT game_id FROM nfl_games WHERE week = 9 AND year = 2025)
    """)
    
    conn.commit()
    print("   ✅ Updated timestamps to force cache refresh")
    
    conn.close()

def create_simple_test_query():
    """Create a simple test to verify the exact query Flask should use"""
    
    print(f"\n🎯 CREATING SIMPLE FLASK TEST:")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # This is likely the exact query Flask uses
    query = """
        SELECT 
            u.username,
            COALESCE(SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END), 0) as correct_picks,
            COALESCE(SUM(up.points_earned), 0) as total_points
        FROM users u
        LEFT JOIN user_picks up ON u.id = up.user_id
        LEFT JOIN nfl_games g ON up.game_id = g.game_id AND g.week = 9 AND g.year = 2025
        WHERE u.is_active = 1
        GROUP BY u.id, u.username
        HAVING total_points > 0 OR correct_picks > 0
        ORDER BY total_points DESC, correct_picks DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print(f"   ✅ Flask-style query results: {len(results)} users")
        for username, correct, points in results:
            print(f"     {username.upper()}: {correct} correct, {points} points")
    else:
        print("   ❌ Flask-style query returned no results")
        
        # Check if users are active
        cursor.execute("SELECT username, is_active FROM users")
        users = cursor.fetchall()
        print("   User status:")
        for username, is_active in users:
            print(f"     {username}: {'Active' if is_active else 'Inactive'}")
    
    conn.close()

if __name__ == "__main__":
    test_flask_leaderboard_logic()
    create_simple_test_query()