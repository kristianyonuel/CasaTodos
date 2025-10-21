import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('=== WEEK 7 2025 THURSDAY NIGHT FOOTBALL ANALYSIS ===')

# October 19, 2025 is a Sunday, so let's find what Thursday would be
sunday_oct_19 = datetime(2025, 10, 19)
print(f'Sunday October 19, 2025: {sunday_oct_19.strftime("%A, %B %d, %Y")}')

# Thursday of that week would be October 16, 2025 
thursday_week7 = sunday_oct_19 - timedelta(days=3)
print(f'Thursday of Week 7: {thursday_week7.strftime("%A, %B %d, %Y")}')

# Check if we have any games on Thursday October 16
thursday_date = thursday_week7.strftime('%Y-%m-%d')
print(f'\nLooking for games on {thursday_date}...')

cursor.execute('''
    SELECT id, away_team, home_team, game_date, is_thursday_night
    FROM nfl_games 
    WHERE week = 7 AND year = 2025 AND game_date LIKE ? || '%'
    ORDER BY game_date
''', (thursday_date,))

thursday_games = cursor.fetchall()

if thursday_games:
    print(f'Found {len(thursday_games)} games on Thursday:')
    for game in thursday_games:
        tnf_status = 'YES' if game[4] else 'NO'
        print(f'  Game {game[0]}: {game[1]} @ {game[2]} - TNF: {tnf_status}')
        print(f'    Date/Time: {game[3]}')
else:
    print('❌ No games found on Thursday!')
    print('\nChecking if Week 7 might be a bye week for TNF...')
    
    # Maybe the Thursday game is actually on a different Thursday
    # Let's check October 17 (the day before Friday)
    alt_thursday = datetime(2025, 10, 17)
    alt_date = alt_thursday.strftime('%Y-%m-%d')
    print(f'Checking {alt_date} ({alt_thursday.strftime("%A")})...')
    
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_thursday_night
        FROM nfl_games 
        WHERE week = 7 AND year = 2025 AND game_date LIKE ? || '%'
        ORDER BY game_date
    ''', (alt_date,))
    
    alt_thursday_games = cursor.fetchall()
    if alt_thursday_games:
        print(f'Found {len(alt_thursday_games)} games on October 17:')
        for game in alt_thursday_games:
            tnf_status = 'YES' if game[4] else 'NO'
            print(f'  Game {game[0]}: {game[1]} @ {game[2]} - TNF: {tnf_status}')

# In any case, let's see which game should logically be TNF
print(f'\n=== IDENTIFYING POTENTIAL TNF GAME ===')

# Typically TNF is the first/earliest game of the week
cursor.execute('''
    SELECT id, away_team, home_team, game_date, game_status, is_final, home_score, away_score
    FROM nfl_games 
    WHERE week = 7 AND year = 2025 
    ORDER BY game_date
    LIMIT 1
''')

earliest_game = cursor.fetchone()
if earliest_game:
    game_id, away, home, date, status, is_final, home_score, away_score = earliest_game
    print(f'Earliest Week 7 game: {away} @ {home}')
    print(f'  Date: {date}')
    print(f'  Status: {status}')
    print(f'  Final: {is_final}')
    print(f'  Score: {away_score if away_score else 0} - {home_score if home_score else 0}')
    
    if status == 'status_final' and not (home_score or away_score):
        print('  ❌ ISSUE: Game shows final but no scores!')
        print('  💡 This should be the TNF game that needs scores updated')

conn.close()

print(f'\n🎯 RECOMMENDATION:')
print(f'1. Designate the earliest game as Thursday Night Football')
print(f'2. Update that game with actual final scores') 
print(f'3. Set is_thursday_night = 1 and is_final = 1')
print(f'4. This will make "Winner Prediction Analysis" show completed games')