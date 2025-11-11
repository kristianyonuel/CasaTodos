import sqlite3

conn = sqlite3.connect('/home/casa/CasaTodos/nfl_fantasy.db')
cursor = conn.cursor()

print("🧹 CLEANING DUPLICATE WEEK 9 PICKS")
print("=" * 40)

# First, let's see the extent of the problem
cursor.execute("""
    SELECT u.username, COUNT(up.id) as total_picks
    FROM users u
    JOIN user_picks up ON u.id = up.user_id
    JOIN nfl_games g ON up.game_id = g.game_id
    WHERE g.week = 9 AND g.year = 2025
    GROUP BY u.id, u.username
    ORDER BY total_picks DESC
""")

duplicates = cursor.fetchall()
print("Current pick counts (should be 14 each):")
for username, count in duplicates:
    print(f"  {username}: {count} picks")

# Delete ALL Week 9 picks
print(f"\n🗑️ Deleting all Week 9 picks...")
cursor.execute("""
    DELETE FROM user_picks 
    WHERE game_id IN (SELECT game_id FROM nfl_games WHERE week = 9 AND year = 2025)
""")
deleted_picks = cursor.rowcount
print(f"Deleted {deleted_picks} duplicate picks")

# Delete ALL Week 9 weekly results
cursor.execute("DELETE FROM weekly_results WHERE week = 9 AND year = 2025")
deleted_results = cursor.rowcount
print(f"Deleted {deleted_results} weekly results")

conn.commit()
conn.close()

print(f"\n✅ Server database cleaned!")
print("Now re-run the picks insertion script...")