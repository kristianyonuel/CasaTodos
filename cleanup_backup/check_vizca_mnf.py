import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('Checking VIZCA Monday Night Football pick...')

cursor.execute("""
    SELECT 
        up.selected_team,
        ng.away_team,
        ng.home_team,
        ng.away_score,
        ng.home_score,
        up.is_correct
    FROM user_picks up
    JOIN nfl_games ng ON up.game_id = ng.game_id
    WHERE up.user_id = 9 AND ng.home_team = 'Dallas Cowboys' AND ng.week = 9
""")

result = cursor.fetchone()
if result:
    selected, away, home, away_score, home_score, is_correct = result
    winner = away if away_score > home_score else home
    print(f'Game: {away} @ {home} ({away_score}-{home_score})')
    print(f'VIZCA picked: {selected}')
    print(f'Winner: {winner}')
    print(f'Database is_correct: {is_correct}')
    should_be_correct = (selected == winner)
    print(f'Should be correct: {should_be_correct}')
    
    if should_be_correct and not is_correct:
        print('FIXING: Updating VIZCA to correct...')
        cursor.execute("""
            UPDATE user_picks 
            SET is_correct = 1
            WHERE user_id = 9 AND game_id = (
                SELECT game_id FROM nfl_games 
                WHERE home_team = 'Dallas Cowboys' AND week = 9
            )
        """)
        conn.commit()
        print('✅ Fixed!')

# Check final totals
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

final_scores = cursor.fetchall()
print('\nFinal Scores:')
for username, correct in final_scores:
    print(f'{username.upper()}: {correct}/14')

conn.close()