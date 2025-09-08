#!/usr/bin/env python3
"""
Diagnostic script to find the problematic query causing the us.total_games_won error
"""

import sqlite3
import sys
import traceback

def test_all_leaderboard_queries():
    """Test various leaderboard queries to find the problematic one"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🔍 Testing leaderboard queries to find us.total_games_won error...")
    print("=" * 70)
    
    # Test 1: Basic leaderboard query (from app.py)
    print("\n1. Testing main leaderboard query...")
    try:
        cursor.execute('''
            SELECT u.username,
                   COUNT(DISTINCT CASE WHEN wr.is_winner = 1 THEN wr.week || '-' || wr.year END) as weekly_wins,
                   SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as total_games_won,
                   COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week || '-' || g.year END) as weeks_played,
                   COUNT(CASE WHEN g.is_final = 1 THEN 1 END) as total_games_played
            FROM users u
            LEFT JOIN user_picks p ON u.id = p.user_id
            LEFT JOIN nfl_games g ON p.game_id = g.id
            LEFT JOIN weekly_results wr ON u.id = wr.user_id
            WHERE u.is_admin = 0
            GROUP BY u.id, u.username
            HAVING COUNT(CASE WHEN g.is_final = 1 THEN 1 END) > 0 OR COUNT(CASE WHEN wr.is_winner = 1 THEN 1 END) > 0
            ORDER BY weekly_wins DESC, total_games_won DESC, u.username
        ''')
        results = cursor.fetchall()
        print(f"✅ Main leaderboard query OK - {len(results)} results")
    except Exception as e:
        print(f"❌ Main leaderboard query failed: {e}")
        traceback.print_exc()
    
    # Test 2: Query that might use user_statistics
    print("\n2. Testing user_statistics-based query...")
    try:
        cursor.execute('''
            SELECT u.username, us.total_wins
            FROM users u
            LEFT JOIN user_statistics us ON u.id = us.user_id
            WHERE u.is_admin = 0
            ORDER BY us.total_wins DESC
        ''')
        results = cursor.fetchall()
        print(f"✅ User statistics query OK - {len(results)} results")
    except Exception as e:
        print(f"❌ User statistics query failed: {e}")
        traceback.print_exc()
    
    # Test 3: Try the problematic query pattern
    print("\n3. Testing problematic query pattern...")
    try:
        cursor.execute('''
            SELECT u.username, us.total_games_won
            FROM users u
            LEFT JOIN user_statistics us ON u.id = us.user_id
            WHERE u.is_admin = 0
            ORDER BY us.total_games_won DESC
        ''')
        results = cursor.fetchall()
        print(f"✅ Problematic query OK - {len(results)} results")
    except Exception as e:
        print(f"❌ Problematic query failed (EXPECTED): {e}")
        print("    This confirms the issue - total_games_won doesn't exist in user_statistics")
    
    # Test 4: Test if there's a query building function that might be wrong
    print("\n4. Testing corrected query...")
    try:
        cursor.execute('''
            SELECT u.username, us.total_wins as total_games_won
            FROM users u
            LEFT JOIN user_statistics us ON u.id = us.user_id
            WHERE u.is_admin = 0
            ORDER BY us.total_wins DESC
        ''')
        results = cursor.fetchall()
        print(f"✅ Corrected query OK - {len(results)} results")
        for row in results[:5]:
            print(f"   {row[0]}: {row[1]} total wins")
    except Exception as e:
        print(f"❌ Corrected query failed: {e}")
        traceback.print_exc()
    
    # Test 5: Check for any views or triggers
    print("\n5. Checking for views or triggers...")
    try:
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='view'")
        views = cursor.fetchall()
        print(f"   Found {len(views)} views")
        for view in views:
            print(f"   View: {view[0]}")
            if view[1] and 'total_games_won' in view[1]:
                print(f"   ⚠️  View contains total_games_won: {view[1]}")
    except Exception as e:
        print(f"❌ Error checking views: {e}")
    
    conn.close()
    print("\n" + "=" * 70)
    print("🎯 Analysis complete. If test 3 failed as expected, then somewhere")
    print("   in your code there's a query using us.total_games_won that needs")
    print("   to be changed to us.total_wins")

if __name__ == "__main__":
    test_all_leaderboard_queries()
