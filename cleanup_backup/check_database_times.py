#!/usr/bin/env python3
"""
Check the actual database times and timezone conversion
"""

import sqlite3
from datetime import datetime
import pytz

# Check what's actually stored in the database
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT id, home_team, away_team, game_date 
    FROM nfl_games 
    WHERE week = 6 AND year = 2025 AND (home_team = 'NYJ' OR away_team = 'NYJ')
''')
game = cursor.fetchone()

if game:
    game_id, home, away, raw_date = game
    print(f'Database shows: {away} @ {home}')
    print(f'Raw database time: {raw_date}')
    print(f'Type: {type(raw_date)}')
    
    # Try to parse the date
    if raw_date:
        try:
            if 'T' in str(raw_date):
                dt = datetime.fromisoformat(str(raw_date).replace('T', ' '))
            else:
                dt = datetime.strptime(str(raw_date), '%Y-%m-%d %H:%M:%S')
            
            print(f'Parsed datetime (naive): {dt}')
            
            # The issue might be in how we interpret this time
            # Let's check both interpretations
            
            print('\nInterpretation 1: Assume database time is already in EST/EDT')
            est_tz = pytz.timezone('US/Eastern')
            dt_as_est = est_tz.localize(dt)
            print(f'  As EST/EDT: {dt_as_est.strftime("%a %m/%d %I:%M %p %Z")}')
            
            print('\nInterpretation 2: Assume database time is UTC')
            dt_as_utc = pytz.utc.localize(dt)
            dt_est_from_utc = dt_as_utc.astimezone(est_tz)
            print(f'  As UTC converted to EST: {dt_est_from_utc.strftime("%a %m/%d %I:%M %p %Z")}')
            
            print('\nInterpretation 3: Assume database time is AST')
            ast_tz = pytz.timezone('America/Puerto_Rico')
            dt_as_ast = ast_tz.localize(dt)
            dt_est_from_ast = dt_as_ast.astimezone(est_tz)
            print(f'  As AST converted to EST: {dt_est_from_ast.strftime("%a %m/%d %I:%M %p %Z")}')
            
        except Exception as e:
            print(f'Error parsing date: {e}')
else:
    print('NYJ game not found')

# Check all Sunday games
print('\n' + '='*50)
print('ALL SUNDAY GAMES:')
cursor.execute('''
    SELECT home_team, away_team, game_date 
    FROM nfl_games 
    WHERE week = 6 AND year = 2025 AND game_date LIKE '2025-10-12%'
    ORDER BY game_date
''')
sunday_games = cursor.fetchall()

for home, away, game_date in sunday_games:
    print(f'{away} @ {home}: {game_date}')

conn.close()