import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Check KRISTIAN in users table
cursor.execute("SELECT id, username FROM users WHERE LOWER(username) LIKE '%kristian%'")
users = cursor.fetchall()

print("KRISTIAN users found:")
for user_id, username in users:
    print(f"  ID: {user_id}, Username: '{username}'")

# Check weekly_results for KRISTIAN
cursor.execute("""
    SELECT wr.weekly_rank, wr.correct_picks, wr.total_points, wr.total_picks
    FROM weekly_results wr
    JOIN users u ON wr.user_id = u.id
    WHERE LOWER(u.username) = 'kristian' AND wr.week = 9 AND wr.year = 2025
""")

weekly_result = cursor.fetchone()

if weekly_result:
    rank, correct, points, total = weekly_result
    print(f"\nKRISTIAN's weekly_results:")
    print(f"  Rank: {rank}")
    print(f"  Correct picks: {correct}")
    print(f"  Total points: {points}")
    print(f"  Total picks: {total}")
else:
    print("\nKRISTIAN not found in weekly_results")

conn.close()