import sqlite3
from datetime import datetime

conn = sqlite3.connect('nfl_fantasy.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print('=== Database Year Check ===')
print(f'Current date: {datetime.now().strftime("%Y-%m-%d")}')

# Check what years exist in the database
cursor.execute('SELECT DISTINCT year FROM nfl_games ORDER BY year')
years = cursor.fetchall()
print(f'Years in database: {[row["year"] for row in years]}')

# Check Week 1 games to see if they have scores
print('\n=== Week 1 Games Status ===')
cursor.execute('''
    SELECT id, away_team, home_team, game_date, is_final, home_score, away_score
    FROM nfl_games 
    WHERE week = 1 
    ORDER BY year, game_date
    LIMIT 5
''')

week1_games = cursor.fetchall()
for game in week1_games:
    final_status = 'FINAL' if game['is_final'] else 'NOT FINAL'
    away_score = game['away_score'] if game['away_score'] is not None else '?'
    home_score = game['home_score'] if game['home_score'] is not None else '?'
    score = f'{away_score}-{home_score}'
    print(f'{game["away_team"]} @ {game["home_team"]} - {game["game_date"]} - {final_status} - {score}')

# Check if there are any games marked as final
print('\n=== Any Final Games ===')
cursor.execute('SELECT COUNT(*) as final_count FROM nfl_games WHERE is_final = 1')
final_count = cursor.fetchone()['final_count']
print(f'Total final games in database: {final_count}')

if final_count > 0:
    cursor.execute('''
        SELECT week, year, away_team, home_team, away_score, home_score 
        FROM nfl_games 
        WHERE is_final = 1 
        LIMIT 3
    ''')
    final_games = cursor.fetchall()
    print('Sample final games:')
    for game in final_games:
        print(f'Week {game["week"]} {game["year"]}: {game["away_team"]} {game["away_score"]} @ {game["home_team"]} {game["home_score"]}')

conn.close()
