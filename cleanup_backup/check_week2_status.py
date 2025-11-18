import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print('=== Week 2 Games Status ===')
cursor.execute('''
    SELECT id, away_team, home_team, game_date, is_final, home_score, away_score
    FROM nfl_games 
    WHERE week = 2 AND year = 2025 
    ORDER BY game_date
''')

games = cursor.fetchall()
for game in games:
    final_status = 'FINAL' if game['is_final'] else 'NOT FINAL'
    away_score = game['away_score'] if game['away_score'] is not None else '?'
    home_score = game['home_score'] if game['home_score'] is not None else '?'
    score = f'{away_score}-{home_score}'
    print(f'{game["away_team"]} @ {game["home_team"]} - {game["game_date"]} - {final_status} - {score}')

print('\n=== Weekly Results for Week 2 ===')
cursor.execute('''
    SELECT COUNT(*) as final_games FROM nfl_games 
    WHERE week = 2 AND year = 2025 AND is_final = 1
''')
final_count = cursor.fetchone()['final_games']
print(f'Final games in Week 2: {final_count}')

# Check if GB vs WSH game exists and its status
print('\n=== Green Bay vs Washington Game ===')
cursor.execute('''
    SELECT id, away_team, home_team, game_date, is_final, home_score, away_score
    FROM nfl_games 
    WHERE week = 2 AND year = 2025 
    AND (away_team = 'GB' OR home_team = 'GB' OR away_team = 'WSH' OR home_team = 'WSH')
''')

gb_wsh_game = cursor.fetchall()
for game in gb_wsh_game:
    final_status = 'FINAL' if game['is_final'] else 'NOT FINAL'
    away_score = game['away_score'] if game['away_score'] is not None else '?'
    home_score = game['home_score'] if game['home_score'] is not None else '?'
    score = f'{away_score}-{home_score}'
    print(f'Found: {game["away_team"]} @ {game["home_team"]} - {game["game_date"]} - {final_status} - {score}')

conn.close()
