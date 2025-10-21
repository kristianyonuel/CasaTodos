#!/usr/bin/env python3
"""
Check Week 6 Game Times
"""

import sqlite3
from datetime import datetime
import pytz

# Check Week 6 games and their times
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT home_team, away_team, game_date 
    FROM nfl_games 
    WHERE week = 6 AND year = 2025 
    ORDER BY game_date
''')
games = cursor.fetchall()

print('Week 6 Games Schedule:')
print('=====================')

est_tz = pytz.timezone('US/Eastern')
ast_tz = pytz.timezone('America/Puerto_Rico')

for home, away, game_date_str in games:
    if game_date_str:
        # Parse the game date
        try:
            if 'T' in game_date_str:
                dt = datetime.fromisoformat(game_date_str.replace('T', ' '))
            else:
                dt = datetime.strptime(game_date_str, '%Y-%m-%d %H:%M:%S')
            
            # Convert to EST and AST
            dt_est = est_tz.localize(dt)
            dt_ast = dt_est.astimezone(ast_tz)
            
            print(f'{away} @ {home}:')
            print(f'  EST: {dt_est.strftime("%a %m/%d %I:%M %p")}')
            print(f'  AST: {dt_ast.strftime("%a %m/%d %I:%M %p")}')
            print()
        except Exception as e:
            print(f'{away} @ {home}: Error parsing date {game_date_str} - {e}')
    else:
        print(f'{away} @ {home}: No date set')

conn.close()

# Also check what the earliest game is
print("\nEarliest Game Analysis:")
print("User reported: 9:30 AM EST Sunday = 5:30 AM AST")
print("That's very early for NFL games!")
print("International games (London) typically start around that time.")