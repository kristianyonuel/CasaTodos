import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🏆 2025 NFL FANTASY SEASON STANDINGS")
print("=" * 80)

# Get weekly winners for each week by finding who had the most correct picks
weekly_winners = {}

for week in range(1, 10):  # Weeks 1-9
    cursor.execute('''
        SELECT u.username, COUNT(CASE WHEN up.is_correct = 1 THEN 1 END) as correct_picks,
               COUNT(*) as total_picks
        FROM user_picks up
        JOIN users u ON up.user_id = u.id
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE ng.week = ? AND ng.year = 2025
        GROUP BY u.id, u.username
        ORDER BY correct_picks DESC, u.username
    ''', (week,))
    
    results = cursor.fetchall()
    if results:
        # Find the winner (highest score)
        max_score = results[0][1]
        winners = [r for r in results if r[1] == max_score]
        
        if len(winners) == 1:
            winner_name = winners[0][0]
            winner_score = winners[0][1]
            total_games = winners[0][2]
        else:
            # Handle ties - could be multiple winners
            winner_name = f"{winners[0][0]} (tied with {len(winners)-1} others)"
            winner_score = winners[0][1]
            total_games = winners[0][2]
        
        weekly_winners[week] = (winner_name, winner_score, total_games, results)

print("\n📅 WEEKLY WINNERS:")
print("-" * 50)
user_wins = {}

for week in sorted(weekly_winners.keys()):
    winner_name, score, total, all_results = weekly_winners[week]
    print(f"Week {week:2d}: {winner_name:15s} ({score}/{total})")
    
    # Track individual wins (not tied wins)
    if " (tied" not in winner_name:
        if winner_name not in user_wins:
            user_wins[winner_name] = []
        user_wins[winner_name].append(week)

print("\n🎯 SEASON SUMMARY (Individual Wins Only):")
print("-" * 50)

# Sort users by number of wins (descending)
if user_wins:
    sorted_users = sorted(user_wins.items(), key=lambda x: len(x[1]), reverse=True)
    
    for user, weeks_won in sorted_users:
        weeks_str = ", ".join([f"Week {w}" for w in sorted(weeks_won)])
        print(f"{user:12s}: {len(weeks_won)} wins - {weeks_str}")

# Show detailed breakdown for KRISTIAN and ROBERT
print("\n🔍 DETAILED BREAKDOWN FOR KRISTIAN & ROBERT:")
print("-" * 60)

for target_user in ['KRISTIAN', 'ROBERT']:
    print(f"\n{target_user}:")
    wins_count = 0
    
    for week in sorted(weekly_winners.keys()):
        winner_name, score, total, all_results = weekly_winners[week]
        
        # Find this user's performance this week
        user_result = None
        for username, correct, total_picks in all_results:
            if username == target_user:
                user_result = (correct, total_picks)
                break
        
        if user_result:
            correct, total_picks = user_result
            if winner_name == target_user:
                wins_count += 1
                print(f"  Week {week}: {correct}/{total_picks} ✅ WON")
            else:
                print(f"  Week {week}: {correct}/{total_picks}")
    
    print(f"  Total wins: {wins_count}")

conn.close()