import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Check game_date format for WSH@GB Thursday game  
cursor.execute('SELECT game_date, home_team, away_team FROM nfl_games WHERE home_team = "GB" AND away_team = "WSH"')
result = cursor.fetchone()

if result:
    print(f'Game date format: "{result[0]}"')
    print(f'Game: {result[2]} @ {result[1]}')
    print(f'Length: {len(result[0])}')
    print(f'Type: {type(result[0])}')
else:
    print('Game not found')

conn.close()
