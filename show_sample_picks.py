import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🏈 WEEK 9 PICKS VERIFICATION - SAMPLE")
print("=" * 45)

# Get sample picks for first few games
cursor.execute("""
    SELECT g.away_team, g.home_team, u.username, up.selected_team
    FROM nfl_games g
    JOIN user_picks up ON g.game_id = up.game_id
    JOIN users u ON up.user_id = u.id
    WHERE g.week = 9
    ORDER BY g.game_date, g.game_id, u.username
    LIMIT 42
""")

results = cursor.fetchall()
current_game = None

for away, home, user, pick in results:
    game = f"{away} @ {home}"
    if game != current_game:
        print(f"\n📅 {game}:")
        current_game = game
    print(f"   {user}: {pick}")

print(f"\n📊 Total entries shown: {len(results)}")

conn.close()