import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🔍 WEEK 9 PICKS VERIFICATION")
print("=" * 40)

# Count picks per user
cursor.execute("""
    SELECT u.username, COUNT(up.id) as pick_count
    FROM users u
    LEFT JOIN user_picks up ON u.id = up.user_id
    LEFT JOIN nfl_games g ON up.game_id = g.game_id AND g.week = 9
    WHERE u.username IN ('JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 'KRISTIAN', 'FER', 'MIKITIN')
    GROUP BY u.id, u.username
    ORDER BY u.username
""")

results = cursor.fetchall()
print("📊 PICK COUNTS:")
for username, count in results:
    print(f"   {username}: {count} picks")

# Sample picks for first two users
print("\n🏈 SAMPLE PICKS (JAVIER & COYOTE):")
cursor.execute("""
    SELECT u.username, g.away_team, g.home_team, up.selected_team
    FROM users u 
    JOIN user_picks up ON u.id = up.user_id 
    JOIN nfl_games g ON up.game_id = g.game_id 
    WHERE g.week = 9 AND u.username IN ('JAVIER', 'COYOTE')
    ORDER BY u.username, g.game_date, g.game_id
""")

for row in cursor.fetchall():
    print(f"   {row[0]}: {row[1]} @ {row[2]} -> {row[3]}")

# Tiebreaker verification
print("\n🎯 TIEBREAKER SCORES (Monday Night):")
cursor.execute("""
    SELECT u.username, up.predicted_away_score, up.predicted_home_score
    FROM users u 
    JOIN user_picks up ON u.id = up.user_id 
    JOIN nfl_games g ON up.game_id = g.game_id 
    WHERE g.week = 9 AND g.away_team = 'Arizona Cardinals' AND g.home_team = 'Dallas Cowboys'
    ORDER BY u.username
""")

for row in cursor.fetchall():
    if row[1] is not None and row[2] is not None:
        print(f"   {row[0]}: {row[1]}-{row[2]}")

conn.close()