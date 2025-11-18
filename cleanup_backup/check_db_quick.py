import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("Available tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for t in tables:
    print(f"  {t[0]}")

# Check if we have games table
cursor.execute("SELECT COUNT(*) FROM games WHERE week = 1 AND year = 2025")
count = cursor.fetchone()[0]
print(f"\nGames for Week 1, 2025: {count}")

if count > 0:
    cursor.execute("SELECT id, away_team, home_team, game_date FROM games WHERE week = 1 AND year = 2025 AND strftime('%w', game_date) = '1' ORDER BY game_date DESC LIMIT 1")
    mnf_game = cursor.fetchone()
    if mnf_game:
        print(f"Monday Night Football game: {mnf_game}")
    else:
        print("No Monday Night Football game found")

conn.close()
