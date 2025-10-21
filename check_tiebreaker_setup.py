import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('=== DATABASE SCHEMA CHECK ===')

# Check nfl_games table structure
cursor.execute('PRAGMA table_info(nfl_games)')
columns = cursor.fetchall()
print('nfl_games table columns:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

print('\n=== WEEK 7 MNF TIEBREAKER STATUS ===')

# Check Week 7 MNF games
cursor.execute('''
    SELECT id, home_team, away_team, game_date, is_monday_night, 
           home_score, away_score, is_tiebreaker
    FROM nfl_games 
    WHERE week = 7 AND year = 2025 AND is_monday_night = 1
    ORDER BY game_date
''')

mnf_games = cursor.fetchall()

print(f'Week 7 Monday Night Football games ({len(mnf_games)} total):')
for game in mnf_games:
    game_id, home, away, date, mnf, home_score, away_score, is_tie = game
    print(f'  Game {game_id}: {away} @ {home}')
    print(f'    Date: {date}')
    print(f'    MNF: {mnf}, Tiebreaker: {is_tie}')
    score_display = f'{away_score or "None"}-{home_score or "None"}'
    print(f'    Scores: {score_display}')

# Check tiebreaker predictions
print('\n=== TIEBREAKER PREDICTIONS ===')
for game in mnf_games:
    game_id = game[0]
    cursor.execute('''
        SELECT COUNT(*) FROM user_picks 
        WHERE game_id = ? AND tiebreaker_total IS NOT NULL
    ''', (game_id,))
    
    tie_count = cursor.fetchone()[0]
    away_team = game[2]
    home_team = game[1]
    print(f'Game {game_id} ({away_team} @ {home_team}): {tie_count} tiebreaker predictions')

print('\n=== TIEBREAKER CONFIGURATION CHECK ===')
# Check if there's a designated tiebreaker game for Week 7
cursor.execute('''
    SELECT id, home_team, away_team, is_tiebreaker
    FROM nfl_games 
    WHERE week = 7 AND year = 2025 AND is_tiebreaker = 1
''')

tiebreaker_games = cursor.fetchall()
if tiebreaker_games:
    print(f'Found {len(tiebreaker_games)} designated tiebreaker games:')
    for tb_game in tiebreaker_games:
        print(f'  Game {tb_game[0]}: {tb_game[2]} @ {tb_game[1]}')
else:
    print('❌ No tiebreaker games found for Week 7!')

conn.close()