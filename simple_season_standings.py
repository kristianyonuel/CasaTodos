import sqlite3

# Connect directly to database without app initialization
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🏆 2025 NFL FANTASY SEASON STANDINGS")
print("=" * 80)

# Get weekly winners for each week
cursor.execute('''
    SELECT week, winner_username, winner_score, total_games
    FROM weekly_results 
    WHERE year = 2025 
    ORDER BY week
''')

weekly_results = cursor.fetchall()

print("\n📅 WEEKLY WINNERS:")
print("-" * 50)
user_wins = {}

for week, winner, score, total in weekly_results:
    print(f"Week {week:2d}: {winner:12s} ({score}/{total})")
    if winner not in user_wins:
        user_wins[winner] = []
    user_wins[winner].append(week)

print("\n🎯 SEASON SUMMARY:")
print("-" * 50)

# Sort users by number of wins (descending)
sorted_users = sorted(user_wins.items(), key=lambda x: len(x[1]), reverse=True)

for user, weeks_won in sorted_users:
    weeks_str = ", ".join([f"Week {w}" for w in sorted(weeks_won)])
    print(f"{user:12s}: {len(weeks_won)} wins - {weeks_str}")

# Show detailed breakdown for KRISTIAN and ROBERT
print("\n🔍 DETAILED BREAKDOWN:")
print("-" * 50)

for user in ['KRISTIAN', 'ROBERT']:
    if user in user_wins:
        print(f"\n{user}'s {len(user_wins[user])} wins:")
        for week in sorted(user_wins[user]):
            # Get detailed info for each win
            cursor.execute('''
                SELECT winner_score, total_games, runner_up_username, runner_up_score
                FROM weekly_results 
                WHERE year = 2025 AND week = ? AND winner_username = ?
            ''', (week, user))
            
            result = cursor.fetchone()
            if result:
                win_score, total, runner_up, runner_score = result
                print(f"  Week {week}: {win_score}/{total} (beat {runner_up} {runner_score}/{total})")

conn.close()