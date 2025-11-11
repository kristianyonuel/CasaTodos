import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('Week 9 Scores Before vs After Monday Night Football:')
print('=' * 55)

# Check scores for VIZCA, JEAN, and RADA
users_to_check = [
    ('VIZCA', 9),
    ('JEAN', 12), 
    ('RADA', 16)
]

for username, user_id in users_to_check:
    print(f'\n{username}:')
    
    # Get total Week 9 picks (including MNF)
    cursor.execute("""
        SELECT COUNT(CASE WHEN up.is_correct = 1 THEN 1 END)
        FROM user_picks up
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE up.user_id = ? AND ng.week = 9
    """, (user_id,))
    
    total_with_mnf = cursor.fetchone()[0]
    
    # Get picks excluding Monday Night Football
    cursor.execute("""
        SELECT COUNT(CASE WHEN up.is_correct = 1 THEN 1 END)
        FROM user_picks up
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE up.user_id = ? AND ng.week = 9 
        AND NOT (ng.home_team = 'Dallas Cowboys' AND ng.away_team = 'Arizona Cardinals')
    """, (user_id,))
    
    total_before_mnf = cursor.fetchone()[0]
    
    # Get Monday Night Football pick
    cursor.execute("""
        SELECT 
            up.selected_team,
            up.is_correct,
            ng.away_score,
            ng.home_score
        FROM user_picks up
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE up.user_id = ? AND ng.home_team = 'Dallas Cowboys' AND ng.week = 9
    """, (user_id,))
    
    mnf_result = cursor.fetchone()
    if mnf_result:
        mnf_pick, mnf_correct, away_score, home_score = mnf_result
        mnf_points = 1 if mnf_correct else 0
        
        print(f'  Before MNF: {total_before_mnf}/13')
        print(f'  MNF Pick: {mnf_pick} - {"CORRECT" if mnf_correct else "WRONG"} (+{mnf_points})')
        print(f'  After MNF: {total_with_mnf}/14')
        print(f'  Cardinals won {away_score}-{home_score}')

print(f'\nSummary:')
print('=' * 20)
print('If they were tied BEFORE Monday Night Football, then:')
print('- VIZCA (picked Cardinals) should have gained +1 point')  
print('- JEAN (picked Cowboys) should have gained +0 points')
print('- RADA (picked Cowboys) should have gained +0 points')
print('\nSo VIZCA should now lead by 1 point over JEAN and RADA.')

conn.close()