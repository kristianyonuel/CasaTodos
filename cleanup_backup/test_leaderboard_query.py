#!/usr/bin/env python3
"""
Test the exact same database query used by the leaderboard route
to see if there's a discrepancy between what we expect and what the app gets.
"""

import sqlite3
from datetime import datetime

def test_leaderboard_query():
    print("🧪 Testing Leaderboard Database Query")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Use the exact same connection method as the app
    DATABASE_PATH = 'nfl_fantasy.db'
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("🔍 Running EXACT same query as leaderboard route...")
    
    # This is the exact query from the leaderboard route in app.py
    cursor.execute('''
        SELECT u.username,
               (SELECT COUNT(*) FROM weekly_results wr WHERE wr.user_id = u.id AND wr.is_winner = 1) as weekly_wins,
               (SELECT SUM(CASE WHEN p2.is_correct = 1 AND g2.is_final = 1 THEN 1 ELSE 0 END)
                FROM user_picks p2
                JOIN nfl_games g2 ON p2.game_id = g2.id
                WHERE p2.user_id = u.id) as total_games_won,
               (SELECT COUNT(DISTINCT g3.week || '-' || g3.year)
                FROM user_picks p3
                JOIN nfl_games g3 ON p3.game_id = g3.id
                WHERE p3.user_id = u.id AND g3.is_final = 1) as weeks_played,
               (SELECT COUNT(*)
                FROM user_picks p4
                JOIN nfl_games g4 ON p4.game_id = g4.id
                WHERE p4.user_id = u.id AND g4.is_final = 1) as total_games_played,
               ROUND(
                   CASE
                       WHEN (SELECT COUNT(DISTINCT g5.week || '-' || g5.year)
                             FROM user_picks p5
                             JOIN nfl_games g5 ON p5.game_id = g5.id
                             WHERE p5.user_id = u.id AND g5.is_final = 1) > 0
                       THEN CAST((SELECT SUM(CASE WHEN p6.is_correct = 1 AND g6.is_final = 1 THEN 1 ELSE 0 END)
                                  FROM user_picks p6
                                  JOIN nfl_games g6 ON p6.game_id = g6.id
                                  WHERE p6.user_id = u.id) AS FLOAT) /
                            (SELECT COUNT(DISTINCT g7.week || '-' || g7.year)
                             FROM user_picks p7
                             JOIN nfl_games g7 ON p7.game_id = g7.id
                             WHERE p7.user_id = u.id AND g7.is_final = 1)
                       ELSE 0
                   END, 1
               ) as avg_games_won_per_week
        FROM users u
        WHERE u.is_admin = 0
        AND ((SELECT COUNT(*) FROM user_picks p8 JOIN nfl_games g8 ON p8.game_id = g8.id WHERE p8.user_id = u.id AND g8.is_final = 1) > 0
             OR (SELECT COUNT(*) FROM weekly_results wr WHERE wr.user_id = u.id AND wr.is_winner = 1) > 0)
        ORDER BY weekly_wins DESC, total_games_won DESC, avg_games_won_per_week DESC, u.username
    ''')
    
    results = cursor.fetchall()
    
    print("📊 Leaderboard Query Results:")
    print("-" * 80)
    print(f"{'Username':<12} {'Weekly Wins':<12} {'Total Games':<12} {'Weeks':<8} {'Total':<8} {'Avg':<8}")
    print("-" * 80)
    
    for row in results:
        username = row[0]
        weekly_wins = row[1] or 0
        total_games_won = row[2] or 0
        weeks_played = row[3] or 0
        total_games_played = row[4] or 0
        avg_games_won_per_week = row[5] or 0.0
        
        print(f"{username:<12} {weekly_wins:<12} {total_games_won:<12} {weeks_played:<8} {total_games_played:<8} {avg_games_won_per_week:<8.1f}")
    
    print()
    print("🎯 Key Focus (Weekly Wins):")
    print("-" * 30)
    
    focus_users = ['kristian', 'robert', 'ramfis']
    for row in results:
        username = row[0].lower()
        weekly_wins = row[1] or 0
        if username in focus_users:
            print(f"  {username.upper()}: {weekly_wins} weekly wins")
    
    print()
    print("🔍 Direct verification of weekly_results table:")
    cursor.execute("""
        SELECT u.username, wr.week, wr.is_winner
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.is_winner = 1 AND wr.year = 2025
        ORDER BY wr.week, u.username
    """)
    
    weekly_winners = cursor.fetchall()
    print("  Weekly winners from database:")
    winner_counts = {}
    for username, week, is_winner in weekly_winners:
        print(f"    Week {week}: {username.upper()}")
        winner_counts[username.upper()] = winner_counts.get(username.upper(), 0) + 1
    
    print()
    print("📈 Summary - Database says:")
    for username, count in sorted(winner_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {username}: {count} wins")
    
    print()
    print("🚨 Your app display says:")
    print("  KRISTIAN: 3 wins")
    print("  ROBERT: 2 wins")
    print("  RAMFIS: 1 win")
    
    print()
    if winner_counts.get('KRISTIAN', 0) != 3 or winner_counts.get('ROBERT', 0) != 2:
        print("❌ MISMATCH CONFIRMED: App display ≠ Database reality")
        print("💡 The query is correct, data is correct, but app still shows wrong values")
        print("🔧 This suggests a template caching or browser caching issue")
    else:
        print("✅ Database matches app display - issue may be resolved")
    
    conn.close()

if __name__ == "__main__":
    test_leaderboard_query()