import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('🔍 CHECKING COLTS VS STEELERS GAME')
print('=' * 40)

# Check current score in database
cursor.execute("""
    SELECT 
        away_team,
        home_team,
        away_score,
        home_score
    FROM nfl_games 
    WHERE (home_team = 'Pittsburgh Steelers' AND away_team = 'Indianapolis Colts') 
    OR (home_team = 'Indianapolis Colts' AND away_team = 'Pittsburgh Steelers')
    AND week = 9
""")

result = cursor.fetchone()
if result:
    away, home, away_score, home_score = result
    print(f'Current database: {away} {away_score} - {home} {home_score}')
    
    if away_score > home_score:
        winner = away
    else:
        winner = home
    print(f'Current winner: {winner}')

print(f'\nYou said: Colts lost 27-20')
print('This means Steelers won 27-20 (or 20-27 depending on home/away)')
print('Need to correct this score and recalculate!')

# If Colts lost 27-20, then Steelers won
# Let's update the correct score
print(f'\n🔧 FIXING COLTS VS STEELERS SCORE...')

# Update to correct score - Steelers 27, Colts 20
cursor.execute("""
    UPDATE nfl_games 
    SET away_score = 20, home_score = 27
    WHERE away_team = 'Indianapolis Colts' AND home_team = 'Pittsburgh Steelers' AND week = 9
""")

conn.commit()

# Verify the update
cursor.execute("""
    SELECT 
        away_team,
        home_team,
        away_score,
        home_score
    FROM nfl_games 
    WHERE away_team = 'Indianapolis Colts' AND home_team = 'Pittsburgh Steelers' AND week = 9
""")

result = cursor.fetchone()
if result:
    away, home, away_score, home_score = result
    print(f'✅ Updated: {away} {away_score} - {home} {home_score}')
    winner = home if home_score > away_score else away
    print(f'Winner: {winner}')

# Now recalculate picks for this game
cursor.execute("""
    SELECT 
        u.username,
        up.selected_team,
        up.is_correct
    FROM users u
    JOIN user_picks up ON u.id = up.user_id
    JOIN nfl_games ng ON up.game_id = ng.game_id
    WHERE ng.away_team = 'Indianapolis Colts' AND ng.home_team = 'Pittsburgh Steelers' AND ng.week = 9
    AND u.username IN ('vizca', 'jean', 'rada')
    ORDER BY u.username
""")

picks = cursor.fetchall()
print(f'\nPicks for Colts @ Steelers (Steelers won 27-20):')
for username, selected_team, is_correct in picks:
    should_be_correct = (selected_team == 'Pittsburgh Steelers')
    status = "CORRECT" if should_be_correct else "WRONG"
    print(f'{username.upper()}: picked {selected_team} - {status}')
    
    # Update correctness
    cursor.execute("""
        UPDATE user_picks 
        SET is_correct = ?
        WHERE user_id = (SELECT id FROM users WHERE username = ?) 
        AND game_id = (SELECT game_id FROM nfl_games WHERE away_team = 'Indianapolis Colts' AND home_team = 'Pittsburgh Steelers' AND week = 9)
    """, (1 if should_be_correct else 0, username))

conn.commit()

# Check updated totals
cursor.execute("""
    SELECT 
        u.username,
        COUNT(CASE WHEN up.is_correct = 1 THEN 1 END) as correct_picks
    FROM users u
    LEFT JOIN user_picks up ON u.id = up.user_id
    LEFT JOIN nfl_games ng ON up.game_id = ng.game_id
    WHERE ng.week = 9 AND u.username IN ('vizca', 'jean', 'rada')
    GROUP BY u.id, u.username
    ORDER BY correct_picks DESC
""")

totals = cursor.fetchall()
print(f'\nUpdated Week 9 totals:')
for username, correct in totals:
    print(f'{username.upper()}: {correct}/14')

conn.close()