import sqlite3
from datetime import datetime

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('=== WEEK 7 GAME STATUS ANALYSIS ===')

# Check all Week 7 games and their status
cursor.execute('''
    SELECT id, away_team, home_team, game_date, game_status, 
           is_final, home_score, away_score, is_thursday_night,
           is_sunday_night, is_monday_night
    FROM nfl_games 
    WHERE week = 7 AND year = 2025
    ORDER BY game_date
''')

games = cursor.fetchall()

print(f'Week 7 Games Status ({len(games)} total):')
current_time = datetime.now()
print(f'Current time: {current_time}')
print()

completed_games = 0
thursday_games = 0

for game in games:
    game_id, away, home, date, status, is_final, home_score, away_score, tnf, snf, mnf = game
    
    # Count Thursday games
    if tnf:
        thursday_games += 1
    
    # Determine game type
    game_type = ''
    if tnf: game_type = ' (TNF)'
    elif snf: game_type = ' (SNF)'  
    elif mnf: game_type = ' (MNF)'
    
    print(f'Game {game_id}: {away} @ {home}{game_type}')
    print(f'  Date: {date}')
    print(f'  Status: {status if status else "Not set"}')
    print(f'  Final: {is_final}')
    
    if home_score is not None and away_score is not None:
        print(f'  Score: {away} {away_score} - {home} {home_score}')
        completed_games += 1
    else:
        print(f'  Score: Not available')
    print()

print(f'=== SUMMARY ===')
print(f'Completed games with scores: {completed_games}/{len(games)}')
print(f'Thursday Night Football games: {thursday_games}')

if thursday_games == 0:
    print('\n❌ ISSUE FOUND: NO THURSDAY NIGHT FOOTBALL GAMES!')
    print('Week 7 should have at least 1 TNF game.')
    print('This explains why no completed games are showing.')
    
    print('\n🔍 CHECKING TNF SETUP:')
    # Check if any games are scheduled for Thursday
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_thursday_night
        FROM nfl_games 
        WHERE week = 7 AND year = 2025 AND game_date LIKE '%-10-17%'
        ORDER BY game_date
    ''')
    
    thursday_scheduled = cursor.fetchall()
    if thursday_scheduled:
        print('Games scheduled for Thursday (10/17):')
        for game in thursday_scheduled:
            tnf_flag = 'YES' if game[4] else 'NO'
            print(f'  Game {game[0]}: {game[1]} @ {game[2]} - TNF: {tnf_flag}')
    else:
        print('No games found scheduled for Thursday 10/17')

elif completed_games == 0:
    print(f'\n❌ ISSUE: {thursday_games} TNF games found but none completed!')
    print('Games may need scores updated or status changed to final.')

conn.close()