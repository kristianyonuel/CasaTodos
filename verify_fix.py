#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Test the exact fixed query
cursor.execute("""
    SELECT u.username,
           SUM(CASE WHEN p.is_correct = 1 AND g.is_final = 1 THEN 1 ELSE 0 END) as total_games_won
    FROM users u
    LEFT JOIN user_picks p ON u.id = p.user_id
    LEFT JOIN nfl_games g ON p.game_id = g.id
    WHERE u.is_admin = 0
    GROUP BY u.id, u.username
    ORDER BY total_games_won DESC
    LIMIT 5
""")

results = cursor.fetchall()
print('FIXED QUERY RESULTS:')
print('Username | Total Games Won (Should be ≤15)')
print('-' * 40)
for username, total_games_won in results:
    status = "✅" if total_games_won <= 15 else "❌ TOO HIGH!"
    print(f'{username:12} | {total_games_won:15} {status}')

conn.close()
