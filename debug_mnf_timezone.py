import sqlite3
from datetime import datetime
import pytz

# Connect to database
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('=== MONDAY NIGHT FOOTBALL TIME ANALYSIS ===')

# Get MNF games for Week 7
cursor.execute('''
    SELECT id, home_team, away_team, game_date, is_monday_night
    FROM nfl_games 
    WHERE week = 7 AND year = 2025 AND is_monday_night = 1
    ORDER BY game_date
''')

mnf_games = cursor.fetchall()

print('Current MNF game times (stored in database):')
for game in mnf_games:
    print(f'  {game[2]} @ {game[1]} - {game[3]} (MNF: {game[4]})')

print('\nConverting to AST:')
eastern = pytz.timezone('US/Eastern')
# AST timezone (UTC-4)
from datetime import timezone, timedelta
ast = timezone(timedelta(hours=-4))

problematic_games = []

for game in mnf_games:
    # Parse stored time
    try:
        dt = datetime.strptime(game[3], '%Y-%m-%d %H:%M:%S')
        # Assume Eastern Time
        dt_eastern = eastern.localize(dt)
        # Convert to AST
        dt_ast = dt_eastern.astimezone(ast)
        
        print(f'\n  {game[2]} @ {game[1]}:')
        et_format = dt_eastern.strftime("%a %m/%d %I:%M %p")
        ast_format = dt_ast.strftime("%a %m/%d %I:%M %p")
        print(f'    ET:  {et_format} ET')
        print(f'    AST: {ast_format} AST')
        
        # Check if it shows as Tuesday in AST
        if dt_ast.strftime('%A') == 'Tuesday':
            print(f'    ❌ PROBLEM: Shows as Tuesday in AST!')
            problematic_games.append(game[0])  # Store game ID
        else:
            print(f'    ✅ OK: Shows as {dt_ast.strftime("%A")} in AST')
            
    except Exception as e:
        print(f'    Error parsing time: {e}')

conn.close()

print(f'\n=== ANALYSIS COMPLETE ===')
print(f'Found {len(problematic_games)} games showing as Tuesday in AST')

if problematic_games:
    print('\n💡 SOLUTION: Monday Night games should be 8:15 PM ET (7:15 PM AST)')
    print('   This keeps them on Monday in both timezones.')
    print(f'\nProblematic game IDs: {problematic_games}')
else:
    print('\n✅ All MNF games display correctly in AST!')