import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🔍 COMPREHENSIVE WEEKLY LEADERBOARD CHECK")
print("=" * 50)

# First, let's see what the weekly_results table currently shows
print("📊 CURRENT WEEKLY_RESULTS TABLE:")
cursor.execute("""
    SELECT u.username, wr.weekly_rank, wr.correct_picks, wr.total_points, wr.total_picks
    FROM weekly_results wr
    JOIN users u ON wr.user_id = u.id
    WHERE wr.week = 9 AND wr.year = 2025
    ORDER BY wr.weekly_rank
""")

weekly_results = cursor.fetchall()
print("Rank | Username     | Correct | Points | Total")
print("-----|--------------|---------|--------|-------")
for username, rank, correct, points, total in weekly_results:
    print(f"{rank:4d} | {username:12s} | {correct:7d} | {points:6d} | {total:5d}")

print(f"\n📝 WHAT USER PICKS ACTUALLY SHOW:")
cursor.execute("""
    SELECT u.username, 
           SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as actual_correct,
           SUM(up.points_earned) as actual_points,
           COUNT(*) as actual_total
    FROM users u
    JOIN user_picks up ON u.id = up.user_id
    JOIN nfl_games g ON up.game_id = g.game_id
    WHERE g.week = 9 AND g.year = 2025
    GROUP BY u.id, u.username
    ORDER BY actual_correct DESC, actual_points DESC
""")

actual_results = cursor.fetchall()
print("Rank | Username     | Correct | Points | Total")
print("-----|--------------|---------|--------|-------")
for i, (username, correct, points, total) in enumerate(actual_results, 1):
    print(f"{i:4d} | {username:12s} | {correct:7d} | {points:6d} | {total:5d}")

print(f"\n🔍 DETAILED COMPARISON:")
print("Username     | Weekly_Results | Actual Picks | Match?")
print("-------------|----------------|--------------|-------")

# Create dictionaries for comparison
weekly_dict = {username: (correct, points) for username, rank, correct, points, total in weekly_results}
actual_dict = {username: (correct, points) for username, correct, points, total in actual_results}

all_users = set(weekly_dict.keys()) | set(actual_dict.keys())

for username in sorted(all_users):
    weekly_data = weekly_dict.get(username, (0, 0))
    actual_data = actual_dict.get(username, (0, 0))
    
    match = "✅" if weekly_data == actual_data else "❌"
    print(f"{username:12s} | {weekly_data[0]:2d}/{weekly_data[1]:2d}          | {actual_data[0]:2d}/{actual_data[1]:2d}         | {match}")

print(f"\n🎯 ISSUES FOUND:")
mismatches = []
for username in all_users:
    weekly_data = weekly_dict.get(username, (0, 0))
    actual_data = actual_dict.get(username, (0, 0))
    if weekly_data != actual_data:
        mismatches.append((username, weekly_data, actual_data))

if mismatches:
    for username, weekly, actual in mismatches:
        print(f"❌ {username}: weekly_results shows {weekly[0]}/{weekly[1]}, but picks show {actual[0]}/{actual[1]}")
else:
    print("✅ All data matches!")

print(f"\n📋 WHAT FLASK SHOULD SHOW (from actual picks):")
print("This is what your website leaderboard should display:")
print("-" * 50)
for i, (username, correct, points, total) in enumerate(actual_results, 1):
    print(f"{i:2d}. {username.upper():12s} - {correct:2d}/{total} correct ({points} points)")

conn.close()