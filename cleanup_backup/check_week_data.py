import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("WEEKS WITH DATA IN DATABASE:")
print("=" * 50)

# Check what weeks have games
cursor.execute('''
    SELECT DISTINCT week 
    FROM nfl_games 
    WHERE year = 2025 
    ORDER BY week
''')
weeks_with_games = cursor.fetchall()
print("Weeks with games:", [w[0] for w in weeks_with_games])

# Check what weeks have picks
cursor.execute('''
    SELECT DISTINCT ng.week, COUNT(*) as pick_count
    FROM user_picks up
    JOIN nfl_games ng ON up.game_id = ng.game_id
    WHERE ng.year = 2025
    GROUP BY ng.week
    ORDER BY ng.week
''')
weeks_with_picks = cursor.fetchall()
print("\nWeeks with picks:")
for week, count in weeks_with_picks:
    print(f"  Week {week}: {count} picks")

# Check what weeks have finalized games (with scores)
cursor.execute('''
    SELECT DISTINCT week, COUNT(*) as games, 
           SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games
    FROM nfl_games 
    WHERE year = 2025 
    GROUP BY week 
    ORDER BY week
''')
weeks_status = cursor.fetchall()
print("\nWeeks game status:")
for week, total_games, final_games in weeks_status:
    print(f"  Week {week}: {final_games}/{total_games} games finalized")

conn.close()