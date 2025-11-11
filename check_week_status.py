import sqlite3
from datetime import datetime

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("📅 CURRENT WEEK STATUS CHECK")
print("=" * 50)

# Check current date
print(f"Today's Date: {datetime.now().strftime('%A, %B %d, %Y')}")

# Check what week the system thinks we're in
cursor.execute('''
    SELECT DISTINCT week, COUNT(*) as games,
           SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games,
           MIN(game_date) as first_game,
           MAX(game_date) as last_game
    FROM nfl_games 
    WHERE year = 2025 
    GROUP BY week 
    ORDER BY week DESC
    LIMIT 5
''')

weeks = cursor.fetchall()
print("\nRecent Weeks Status:")
print("Week | Games | Final | First Game          | Last Game")
print("-----|-------|-------|---------------------|---------------------")

for week, total, final, first_game, last_game in weeks:
    status = "✅ Complete" if total == final else f"🔄 {final}/{total} done"
    print(f"{week:4d} | {total:5d} | {final:5d} | {first_game[:16]:16s} | {last_game[:16]:16s} | {status}")

# Check Week 9 winner
print("\n🏆 WEEK 9 WINNER VERIFICATION:")
cursor.execute('''
    SELECT u.username, wr.correct_picks, wr.total_picks, wr.is_winner
    FROM weekly_results wr
    JOIN users u ON wr.user_id = u.id
    WHERE wr.week = 9 AND wr.year = 2025 AND wr.is_winner = 1
''')

winner = cursor.fetchone()
if winner:
    username, correct, total, is_winner = winner
    print(f"Week 9 Winner: {username.upper()} with {correct}/{total} picks ✅")
else:
    print("No Week 9 winner found in database ❌")

# Check if Week 10 games exist
cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 10 AND year = 2025')
week10_count = cursor.fetchone()[0]
print(f"\nWeek 10 Games in Database: {week10_count}")

conn.close()