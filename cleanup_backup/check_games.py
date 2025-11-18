import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Check all games in week 1
cursor.execute('SELECT game_id, away_team, home_team, away_score, home_score, is_final, game_status FROM nfl_games WHERE week = 1 AND year = 2025')
games = cursor.fetchall()

print("Week 1 Games:")
for game in games:
    print(f"Game {game[0]}: {game[1]} {game[3] or '?'} - {game[4] or '?'} {game[2]} | Final: {game[5]} | Status: {game[6]}")

# Check weekly results
cursor.execute('SELECT user_id, total_correct, is_winner FROM weekly_results WHERE week = 1 AND year = 2025')
results = cursor.fetchall()

print("\nWeekly Results:")
for result in results:
    cursor.execute('SELECT username FROM users WHERE id = ?', (result[0],))
    username = cursor.fetchone()[0]
    print(f"{username}: {result[1]} correct, Winner: {result[2]}")

conn.close()
