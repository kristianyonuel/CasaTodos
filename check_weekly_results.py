import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Check if weekly_results table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weekly_results'")
table_exists = cursor.fetchone()
print(f"Weekly results table exists: {table_exists is not None}")

if table_exists:
    # Check table structure
    cursor.execute("PRAGMA table_info(weekly_results)")
    columns = cursor.fetchall()
    print("\nTable structure:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check if there are any records
    cursor.execute("SELECT COUNT(*) FROM weekly_results")
    count = cursor.fetchone()[0]
    print(f"\nTotal records in weekly_results: {count}")
    
    # Check Week 1 specifically
    cursor.execute("SELECT COUNT(*) FROM weekly_results WHERE week = 1 AND year = 2025")
    week1_count = cursor.fetchone()[0]
    print(f"Week 1, 2025 records: {week1_count}")

# Check Buffalo game specifically
cursor.execute("SELECT game_id, away_team, home_team, away_score, home_score, is_final FROM nfl_games WHERE (away_team = 'BAL' AND home_team = 'BUF') OR (away_team = 'BUF' AND home_team = 'BAL')")
buffalo_game = cursor.fetchone()
if buffalo_game:
    print(f"\nBuffalo game: {buffalo_game[1]} {buffalo_game[3]} - {buffalo_game[4]} {buffalo_game[2]} (Final: {buffalo_game[5]})")
else:
    print("\nNo Buffalo game found")

conn.close()
