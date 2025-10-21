import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('=== DATABASE TABLES ===')
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
for table in tables:
    print(f'  {table[0]}')

print('\n=== USER_PICKS TABLE STRUCTURE ===')
cursor.execute('PRAGMA table_info(user_picks)')
picks_columns = cursor.fetchall()
for col in picks_columns:
    print(f'  {col[1]} ({col[2]})')

print('\n=== WEEK 7 MNF GAMES ===')
cursor.execute('''
    SELECT id, home_team, away_team, game_date, is_monday_night
    FROM nfl_games 
    WHERE week = 7 AND year = 2025 AND is_monday_night = 1
    ORDER BY game_date
''')

mnf_games = cursor.fetchall()
for game in mnf_games:
    print(f'  Game {game[0]}: {game[2]} @ {game[1]} - {game[3]}')

print('\n=== TIEBREAKER PICKS CHECK ===')
for game in mnf_games:
    cursor.execute('''
        SELECT user_id, tiebreaker_total 
        FROM user_picks 
        WHERE game_id = ? AND tiebreaker_total IS NOT NULL
    ''', (game[0],))
    
    tiebreaker_picks = cursor.fetchall()
    print(f'Game {game[0]} tiebreaker predictions: {len(tiebreaker_picks)}')
    if tiebreaker_picks:
        for pick in tiebreaker_picks:
            print(f'  User {pick[0]}: {pick[1]} total points')

# Check if there's a specific tiebreaker configuration
print('\n=== CHECKING FOR TIEBREAKER CONFIGURATION ===')
try:
    cursor.execute('SELECT * FROM tiebreakers LIMIT 5')
    tiebreakers = cursor.fetchall()
    print(f'Found tiebreakers table with {len(tiebreakers)} entries')
except:
    print('No tiebreakers table found')

# Check app configuration or settings
try:
    cursor.execute('SELECT * FROM settings WHERE key LIKE "%tiebreaker%"')
    settings = cursor.fetchall()
    if settings:
        for setting in settings:
            print(f'Tiebreaker setting: {setting}')
    else:
        print('No tiebreaker settings found')
except:
    print('No settings table found')

conn.close()