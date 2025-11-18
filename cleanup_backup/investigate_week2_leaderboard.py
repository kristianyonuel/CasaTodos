import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('=== Week 2 Completed Games Check ===')
cursor.execute('''
    SELECT COUNT(*) as completed_count FROM nfl_games 
    WHERE week = 2 AND year = 2025 AND is_final = 1
''')
completed_count = cursor.fetchone()[0]
print(f'Completed games for Week 2, 2025: {completed_count}')

if completed_count == 0:
    print('\nThis is why the weekly leaderboard shows "No completed games"')
    print('Let me check what games are available in Week 2:')
    
    cursor.execute('''
        SELECT away_team, home_team, game_date, is_final, home_score, away_score
        FROM nfl_games 
        WHERE week = 2 AND year = 2025 
        ORDER BY game_date
    ''')
    
    games = cursor.fetchall()
    print(f'\nTotal Week 2 games: {len(games)}')
    for game in games:
        away_team, home_team, game_date, is_final, home_score, away_score = game
        status = 'FINAL' if is_final else 'NOT FINAL'
        score = f'{away_score or "?"}-{home_score or "?"}'
        print(f'{away_team} @ {home_team} - {game_date} - {status} - {score}')

# Let me also check if yesterday's date could have been Green Bay vs Washington
print('\n=== Date Analysis ===')
from datetime import datetime, timedelta
yesterday = datetime.now() - timedelta(days=1)
print(f'Yesterday was: {yesterday.strftime("%Y-%m-%d")}')

# Check if there are any games scheduled for yesterday
cursor.execute('''
    SELECT away_team, home_team, game_date, is_final, home_score, away_score
    FROM nfl_games 
    WHERE DATE(game_date) = ? AND year = 2025
''', (yesterday.strftime('%Y-%m-%d'),))

yesterday_games = cursor.fetchall()
if yesterday_games:
    print('Games scheduled for yesterday:')
    for game in yesterday_games:
        away_team, home_team, game_date, is_final, home_score, away_score = game
        status = 'FINAL' if is_final else 'NOT FINAL'
        score = f'{away_score or "?"}-{home_score or "?"}'
        print(f'{away_team} @ {home_team} - {game_date} - {status} - {score}')
else:
    print('No games scheduled for yesterday')

conn.close()
