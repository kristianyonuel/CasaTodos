import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🔧 FIXING KRISTIAN'S WEEKLY RESULTS")
print("=" * 40)

# Recalculate KRISTIAN's correct score from his actual picks
cursor.execute("""
    SELECT SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
           SUM(up.points_earned) as points,
           COUNT(*) as total
    FROM user_picks up
    JOIN users u ON up.user_id = u.id
    JOIN nfl_games g ON up.game_id = g.game_id
    WHERE u.username = 'kristian' AND g.week = 9 AND g.year = 2025
""")

actual_stats = cursor.fetchone()
if actual_stats:
    correct, points, total = actual_stats
    print(f"KRISTIAN's actual stats: {correct}/{total} correct, {points} points")
    
    # Update his weekly_results entry
    cursor.execute("""
        UPDATE weekly_results 
        SET correct_picks = ?, total_points = ?, total_picks = ?
        WHERE user_id = (SELECT id FROM users WHERE username = 'kristian')
        AND week = 9 AND year = 2025
    """, (correct, points, total))
    
    print(f"✅ Updated KRISTIAN's weekly_results")

# Now recalculate all ranks since KRISTIAN's score changed
print("\n🏆 RECALCULATING WEEKLY RANKS...")

# Get all users' correct scores for Week 9
cursor.execute("""
    SELECT wr.user_id, u.username, wr.correct_picks, wr.total_points
    FROM weekly_results wr
    JOIN users u ON wr.user_id = u.id
    WHERE wr.week = 9 AND wr.year = 2025
    ORDER BY wr.total_points DESC, wr.correct_picks DESC
""")

users_rankings = cursor.fetchall()

# Update ranks
for rank, (user_id, username, correct, points) in enumerate(users_rankings, 1):
    cursor.execute("""
        UPDATE weekly_results 
        SET weekly_rank = ?
        WHERE user_id = ? AND week = 9 AND year = 2025
    """, (rank, user_id))
    print(f"  {rank:2d}. {username:12s} - {correct:2d}/14 correct ({points} pts)")

conn.commit()

# Verify KRISTIAN's final position
cursor.execute("""
    SELECT wr.weekly_rank, wr.correct_picks, wr.total_points
    FROM weekly_results wr
    JOIN users u ON wr.user_id = u.id
    WHERE u.username = 'kristian' AND wr.week = 9 AND wr.year = 2025
""")

final_kristian = cursor.fetchone()
if final_kristian:
    rank, correct, points = final_kristian
    print(f"\n🎯 KRISTIAN'S FINAL POSITION:")
    print(f"   Rank: {rank}")
    print(f"   Score: {correct}/14 correct ({points} points)")

conn.close()
print(f"\n✅ KRISTIAN'S WEEKLY RESULTS FIXED!")