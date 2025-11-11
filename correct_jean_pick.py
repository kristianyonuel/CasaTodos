import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('Correcting JEAN\'s Monday Night Football pick...')
print('=' * 45)

# Update JEAN's pick to Dallas Cowboys for MNF
cursor.execute("""
    UPDATE user_picks 
    SET selected_team = 'Dallas Cowboys', is_correct = 0
    WHERE user_id = 12 
    AND game_id = (SELECT game_id FROM nfl_games WHERE home_team = 'Dallas Cowboys' AND week = 9)
""")

conn.commit()
print('✅ Updated JEAN to pick Dallas Cowboys (who lost)')

# Now check both users' final scores
print('\nFinal Monday Night Football Results:')
print('=' * 40)

for user_id, username in [(12, 'JEAN'), (9, 'VIZCA')]:
    # Get MNF pick
    cursor.execute("""
        SELECT 
            up.selected_team,
            ng.home_team,
            ng.away_team,
            ng.home_score,
            ng.away_score,
            up.is_correct
        FROM user_picks up
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE up.user_id = ? AND ng.home_team = 'Dallas Cowboys' AND ng.week = 9
    """, (user_id,))
    
    mnf_result = cursor.fetchone()
    
    # Get total correct for Week 9
    cursor.execute("""
        SELECT COUNT(CASE WHEN up.is_correct = 1 THEN 1 END)
        FROM user_picks up
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE up.user_id = ? AND ng.week = 9
    """, (user_id,))
    
    total_correct = cursor.fetchone()[0]
    
    if mnf_result:
        selected, home, away, home_score, away_score, is_correct = mnf_result
        winner = away if away_score > home_score else home
        
        print(f'{username}:')
        print(f'  MNF Pick: {selected}')
        print(f'  MNF Result: {"CORRECT" if is_correct else "WRONG"} (Cardinals won 30-26)')
        print(f'  Week 9 Total: {total_correct}/14')
        print()

# Show final standings
print('Week 9 Final Standings:')
print('=' * 25)
cursor.execute("""
    SELECT 
        u.username,
        COUNT(CASE WHEN up.is_correct = 1 THEN 1 END) as correct_picks
    FROM users u
    LEFT JOIN user_picks up ON u.id = up.user_id
    LEFT JOIN nfl_games ng ON up.game_id = ng.game_id
    WHERE ng.week = 9 AND u.username IN ('jean', 'vizca')
    GROUP BY u.id, u.username
    ORDER BY correct_picks DESC
""")

standings = cursor.fetchall()
for username, correct in standings:
    print(f'{username.upper()}: {correct}/14')

conn.close()