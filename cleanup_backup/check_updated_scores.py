import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('📊 UPDATED ANALYSIS WITH CORRECT COLTS SCORE')
print('=' * 50)

# Check scores before and after Monday Night Football
users_to_check = [('VIZCA', 9), ('JEAN', 12), ('RADA', 16)]

for username, user_id in users_to_check:
    # Get total excluding Monday Night Football
    cursor.execute("""
        SELECT COUNT(CASE WHEN up.is_correct = 1 THEN 1 END)
        FROM user_picks up
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE up.user_id = ? AND ng.week = 9 
        AND NOT (ng.home_team = 'Dallas Cowboys' AND ng.away_team = 'Arizona Cardinals')
    """, (user_id,))
    
    before_mnf = cursor.fetchone()[0]
    
    # Get Monday Night Football pick
    cursor.execute("""
        SELECT up.selected_team, up.is_correct
        FROM user_picks up
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE up.user_id = ? AND ng.home_team = 'Dallas Cowboys' AND ng.week = 9
    """, (user_id,))
    
    mnf_result = cursor.fetchone()
    mnf_pick, mnf_correct = mnf_result if mnf_result else ('None', 0)
    
    # Total after MNF
    cursor.execute("""
        SELECT COUNT(CASE WHEN up.is_correct = 1 THEN 1 END)
        FROM user_picks up
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE up.user_id = ? AND ng.week = 9
    """, (user_id,))
    
    total_after = cursor.fetchone()[0]
    
    print(f'{username}:')
    print(f'  Before MNF: {before_mnf}/13')
    print(f'  MNF pick: {mnf_pick} ({"WON" if mnf_correct else "LOST"})')
    print(f'  After MNF: {total_after}/14')
    print()

print('Key Changes with Correct Colts Score:')
print('- Steelers beat Colts 27-20 (not Colts 32-27)')
print('- VIZCA picked Colts → WRONG (lost a point)')
print('- JEAN picked Colts → WRONG (lost a point)')  
print('- RADA picked Steelers → CORRECT (gained a point)')

print('\nNow checking if they were tied before MNF...')

conn.close()