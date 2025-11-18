import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("CHECKING ALL USER PICKS IN DATABASE:")
print("=" * 60)

# Check all picks by week
cursor.execute('''
    SELECT ng.week, u.username, COUNT(*) as pick_count,
           SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks
    FROM user_picks up
    JOIN nfl_games ng ON up.game_id = ng.game_id
    JOIN users u ON up.user_id = u.id
    WHERE ng.year = 2025
    GROUP BY ng.week, u.username
    ORDER BY ng.week, correct_picks DESC, u.username
''')

picks_data = cursor.fetchall()

current_week = None
for week, username, pick_count, correct_picks in picks_data:
    if week != current_week:
        print(f"\n📅 WEEK {week}:")
        print("-" * 40)
        current_week = week
    
    print(f"  {username:12s}: {correct_picks}/{pick_count}")

# Count total picks per user across all weeks
print("\n\n🎯 TOTAL PICKS PER USER (ALL WEEKS):")
print("-" * 50)
cursor.execute('''
    SELECT u.username, COUNT(*) as total_picks,
           SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks
    FROM user_picks up
    JOIN nfl_games ng ON up.game_id = ng.game_id
    JOIN users u ON up.user_id = u.id
    WHERE ng.year = 2025
    GROUP BY u.username
    ORDER BY correct_picks DESC, u.username
''')

user_totals = cursor.fetchall()
for username, total_picks, correct_picks in user_totals:
    print(f"  {username:12s}: {correct_picks}/{total_picks}")

conn.close()