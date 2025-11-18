import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Get weekly results with usernames, ordered by performance
cursor.execute("""
    SELECT u.username, wr.correct_picks, wr.total_picks, wr.is_winner, wr.total_points
    FROM weekly_results wr
    JOIN users u ON wr.user_id = u.id
    WHERE wr.week = 1 AND wr.year = 2025
    ORDER BY wr.total_points DESC, wr.correct_picks DESC
""")

results = cursor.fetchall()
print("Week 1, 2025 Leaderboard:")
print("Username | Correct | Total | Winner | Points")
print("-" * 45)
for result in results:
    winner_mark = "🏆" if result[3] else ""
    print(f"{result[0]:<12} | {result[1]:>2}/{result[2]:<2} | {result[3]:<6} | {result[4]:>6} {winner_mark}")

# Check if any winner is marked
cursor.execute("SELECT COUNT(*) FROM weekly_results WHERE week = 1 AND year = 2025 AND is_winner = 1")
winner_count = cursor.fetchone()[0]
print(f"\nNumber of marked winners: {winner_count}")

conn.close()
