import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🔧 FIXING WEEKLY_RESULTS TABLE")
print("=" * 40)

# Delete existing Week 9 results to start fresh
print("🗑️ Clearing existing Week 9 results...")
cursor.execute("DELETE FROM weekly_results WHERE week = 9 AND year = 2025")

# Calculate and insert correct results for all users
print("📊 Calculating results for all users...")
cursor.execute("""
    SELECT u.id, u.username,
           SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
           SUM(up.points_earned) as points,
           COUNT(*) as total
    FROM users u
    JOIN user_picks up ON u.id = up.user_id
    JOIN nfl_games g ON up.game_id = g.game_id
    WHERE g.week = 9 AND g.year = 2025
    GROUP BY u.id, u.username
    ORDER BY points DESC, correct DESC
""")

user_results = cursor.fetchall()

print(f"Found {len(user_results)} users with Week 9 picks")

# Insert weekly results with correct ranks
for rank, (user_id, username, correct, points, total) in enumerate(user_results, 1):
    cursor.execute("""
        INSERT INTO weekly_results 
        (user_id, week, year, correct_picks, total_points, total_picks, weekly_rank)
        VALUES (?, 9, 2025, ?, ?, ?, ?)
    """, (user_id, correct, points, total, rank))
    
    print(f"  {rank:2d}. {username:12s} - {correct:2d}/{total} correct ({points} pts)")

conn.commit()

# Verify the fix
print(f"\n✅ VERIFICATION - Final leaderboard:")
cursor.execute("""
    SELECT wr.weekly_rank, u.username, wr.correct_picks, wr.total_points, wr.total_picks
    FROM weekly_results wr
    JOIN users u ON wr.user_id = u.id
    WHERE wr.week = 9 AND wr.year = 2025
    ORDER BY wr.weekly_rank
""")

final_results = cursor.fetchall()
for rank, username, correct, points, total in final_results:
    print(f"  {rank:2d}. {username.upper():12s} - {correct:2d}/{total} correct ({points} pts)")

conn.close()

print(f"\n🎯 WEEKLY_RESULTS TABLE FIXED!")
print("Now your Flask leaderboard should show all 14 users!")
print("Upload this database to your server and restart Flask.")