import sqlite3
from datetime import datetime

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('=== ADDING MISSING THURSDAY NIGHT FOOTBALL GAME ===')

# First, let's fix the LAR @ JAX game back to Sunday
print('1. Fixing LAR @ JAX back to Sunday game...')
cursor.execute('''
    UPDATE nfl_games 
    SET 
        is_thursday_night = 0,
        game_date = '2025-10-19 09:30:00',
        away_score = NULL,
        home_score = NULL,
        is_final = 0,
        game_status = 'status_scheduled'
    WHERE id = 245
''')

# Now add the real Thursday Night Football game: PIT @ CIN
print('2. Adding PIT @ CIN Thursday Night Football game...')

# Get team IDs for Pittsburgh and Cincinnati
cursor.execute('SELECT id FROM nfl_teams WHERE abbreviation = "PIT"')
pit_id = cursor.fetchone()[0]

cursor.execute('SELECT id FROM nfl_teams WHERE abbreviation = "CIN"')
cin_id = cursor.fetchone()[0]

# Insert the TNF game
cursor.execute('''
    INSERT INTO nfl_games (
        season_id, week, year, game_id, 
        home_team_id, away_team_id, home_team, away_team,
        game_date, is_monday_night, is_thursday_night, is_sunday_night,
        is_playoff, is_final, away_score, home_score, game_status,
        created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    2025, 7, 2025, 'tnf_week7_2025',
    cin_id, pit_id, 'CIN', 'PIT',
    '2025-10-16 20:15:00',  # Thursday 8:15 PM ET
    0, 1, 0,  # TNF = 1
    0, 1,  # is_final = 1
    31, 33,  # PIT 31 - CIN 33
    'Final',
    datetime.now(), datetime.now()
))

# Get the new game ID
new_game_id = cursor.lastrowid
print(f'✅ Added Game {new_game_id}: PIT @ CIN (Thursday Night Football)')

# Verify the addition
cursor.execute('''
    SELECT id, away_team, home_team, game_date, is_thursday_night,
           is_final, away_score, home_score, game_status
    FROM nfl_games 
    WHERE id = ?
''', (new_game_id,))

new_game = cursor.fetchone()
if new_game:
    game_id, away, home, date, tnf, final, away_score, home_score, status = new_game
    print(f'   Game {game_id}: {away} @ {home}')
    print(f'   Date: {date}')
    print(f'   TNF: {tnf}, Final: {final}')
    print(f'   Score: {away} {away_score} - {home} {home_score}')
    print(f'   Status: {status}')

# Commit changes
conn.commit()

# Verify we now have completed games
cursor.execute('''
    SELECT COUNT(*) 
    FROM nfl_games 
    WHERE week = 7 AND year = 2025 AND is_final = 1 
    AND home_score IS NOT NULL AND away_score IS NOT NULL
''')

completed_count = cursor.fetchone()[0]
print(f'\n=== VERIFICATION ===')
print(f'Week 7 completed games: {completed_count}')

if completed_count > 0:
    print('🎉 SUCCESS! Winner Prediction Analysis should now work!')
    
    # Show completed games
    cursor.execute('''
        SELECT away_team, away_score, home_team, home_score
        FROM nfl_games 
        WHERE week = 7 AND year = 2025 AND is_final = 1
        ORDER BY game_date
    ''')
    
    completed_games = cursor.fetchall()
    print('\nCompleted Week 7 games:')
    for game in completed_games:
        away, away_score, home, home_score = game
        print(f'  {away} {away_score} - {home} {home_score}')

conn.close()

print('\n🏈 THURSDAY NIGHT FOOTBALL PROPERLY ADDED!')
print('   Real TNF game: PIT @ CIN with actual score')
print('   LAR @ JAX moved back to Sunday as preview')
print('   Winner Prediction Analysis should now show TNF results')