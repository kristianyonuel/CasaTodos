import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🏆 WEEKLY RESULTS TABLE ANALYSIS")
print("=" * 60)

# Check what's in the weekly_results table
print("1. WEEKLY_RESULTS table structure:")
cursor.execute("PRAGMA table_info(weekly_results)")
columns = cursor.fetchall()
for col in columns:
    print(f"   {col[1]:20s} {col[2]}")

print("\n2. Sample data from weekly_results:")
cursor.execute("SELECT * FROM weekly_results ORDER BY week, is_winner DESC LIMIT 10")
rows = cursor.fetchall()
for row in rows:
    print(f"   {row}")

print("\n3. Weekly winners in weekly_results:")
cursor.execute('''
    SELECT wr.week, wr.year, u.username, wr.correct_picks, wr.total_picks, wr.is_winner
    FROM weekly_results wr
    JOIN users u ON wr.user_id = u.id
    WHERE wr.is_winner = 1 AND wr.year = 2025
    ORDER BY wr.week
''')
winners = cursor.fetchall()

if winners:
    print("   Week | Year | Winner    | Score | Winner?")
    print("   -----|------|-----------|-------|--------")
    for week, year, username, correct, total, is_winner in winners:
        print(f"   {week:4d} | {year} | {username:9s} | {correct:2d}/{total:2d} | {bool(is_winner)}")
else:
    print("   No weekly winners found!")

print("\n4. All data in weekly_results by week:")
cursor.execute('''
    SELECT wr.week, u.username, wr.correct_picks, wr.total_picks, wr.is_winner, wr.weekly_rank
    FROM weekly_results wr
    JOIN users u ON wr.user_id = u.id
    WHERE wr.year = 2025
    ORDER BY wr.week, wr.weekly_rank
''')
all_results = cursor.fetchall()

current_week = None
for week, username, correct, total, is_winner, rank in all_results:
    if week != current_week:
        print(f"\n   📅 WEEK {week}:")
        current_week = week
    
    winner_mark = "🏆" if is_winner else " "
    print(f"   {winner_mark} {rank:2d}. {username:12s}: {correct:2d}/{total:2d}")

print(f"\n5. Total records in weekly_results: {len(all_results)}")

conn.close()