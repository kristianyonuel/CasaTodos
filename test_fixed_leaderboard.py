#!/usr/bin/env python3
"""Test the fixed leaderboard query"""

import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Test the fixed query
cursor.execute('''
    SELECT u.username,
           COUNT(DISTINCT CASE WHEN wr.is_winner = 1 THEN wr.week || '-' || wr.year END) as weekly_wins,
           SUM(CASE WHEN p.is_correct = 1 AND g.is_final = 1 THEN 1 ELSE 0 END) as total_games_won
    FROM users u
    LEFT JOIN user_picks p ON u.id = p.user_id
    LEFT JOIN nfl_games g ON p.game_id = g.id
    LEFT JOIN weekly_results wr ON u.id = wr.user_id
    WHERE u.is_admin = 0
    GROUP BY u.id, u.username
    HAVING COUNT(CASE WHEN g.is_final = 1 THEN 1 END) > 0
    ORDER BY weekly_wins DESC, total_games_won DESC
    LIMIT 10
''')

results = cursor.fetchall()

print("🎯 FIXED LEADERBOARD RESULTS:")
print("Username | Weekly Wins | Total Games Won (Fixed)")
print("-" * 50)

for username, weekly_wins, total_games_won in results:
    print(f"{username:12} | {weekly_wins:11} | {total_games_won:19}")

conn.close()
