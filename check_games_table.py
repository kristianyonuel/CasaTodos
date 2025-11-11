import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("NFL_GAMES TABLE STRUCTURE:")
print("=" * 40)
cursor.execute('PRAGMA table_info(nfl_games)')
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

print("\nWEEK 9 GAMES SAMPLE:")
print("=" * 40)
cursor.execute('SELECT * FROM nfl_games WHERE week = 9 LIMIT 3')
games = cursor.fetchall()
for game in games:
    print(game)

conn.close()