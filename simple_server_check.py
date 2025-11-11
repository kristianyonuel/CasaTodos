import sqlite3

conn = sqlite3.connect('/home/casa/CasaTodos/nfl_fantasy.db')
cursor = conn.cursor()

# Check server data
cursor.execute("""
    SELECT COUNT(*) FROM user_picks up 
    JOIN nfl_games g ON up.game_id = g.game_id 
    WHERE g.week = 9 AND g.year = 2025
""")
picks = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM weekly_results WHERE week = 9 AND year = 2025")
results = cursor.fetchone()[0]

cursor.execute("SELECT setting_value FROM league_settings WHERE setting_name = 'current_week'")
current_week = cursor.fetchone()

print(f"Server has {picks} picks and {results} weekly results for Week 9")
print(f"Current week setting: {current_week[0] if current_week else 'NOT SET'}")

# Check what admin interface might see
cursor.execute("""
    SELECT u.username, COUNT(up.id) as pick_count
    FROM users u
    LEFT JOIN user_picks up ON u.id = up.user_id
    LEFT JOIN nfl_games g ON up.game_id = g.game_id AND g.week = 9 AND g.year = 2025
    GROUP BY u.id, u.username
    ORDER BY u.username
""")

admin_view = cursor.fetchall()
print("\nWhat admin interface should see:")
for username, pick_count in admin_view:
    print(f"  {username}: {pick_count} picks")

conn.close()