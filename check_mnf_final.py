import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('Monday Night Football Check:')
print('=' * 35)

# Check MNF picks for JEAN and VIZCA
for user_id, username in [(12, 'JEAN'), (9, 'VIZCA')]:
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
    
    result = cursor.fetchone()
    if result:
        selected, home, away, home_score, away_score, is_correct = result
        winner = away if away_score > home_score else home
        
        print(f'{username}:')
        print(f'  Picked: {selected}')
        print(f'  Winner: {winner}')
        print(f'  MNF Correct: {"YES" if is_correct else "NO"}')
        
        # Get total correct for this user
        cursor.execute("""
            SELECT COUNT(CASE WHEN up.is_correct = 1 THEN 1 END)
            FROM user_picks up
            JOIN nfl_games ng ON up.game_id = ng.game_id
            WHERE up.user_id = ? AND ng.week = 9
        """, (user_id,))
        
        total = cursor.fetchone()[0]
        print(f'  Total Week 9: {total}/14')
        print()

conn.close()