import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT u.username, COUNT(up.id) as picks
    FROM users u 
    JOIN user_picks up ON u.id = up.user_id 
    JOIN nfl_games g ON up.game_id = g.game_id 
    WHERE g.week = 9 AND u.username = 'vizca'
    GROUP BY u.username
""")

result = cursor.fetchone()
if result:
    print(f"VIZCA has {result[1]} Week 9 picks")
else:
    print("VIZCA has 0 Week 9 picks")

conn.close()