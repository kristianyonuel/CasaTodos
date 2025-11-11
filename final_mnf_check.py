import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('Monday Night Football Final Analysis:')
print('=' * 40)

# Check both users MNF picks
for username, user_id in [('JEAN', 12), ('VIZCA', 9)]:
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
        WHERE up.user_id = ? AND ng.home_team = 'Dallas Cowboys' AND ng.week = 9
    """, (user_id,))
    
    result = cursor.fetchone()
    if result:
        selected, away, home, away_score, home_score, is_correct = result
        winner = away if away_score > home_score else home
        
        print(f'{username}:')
        print(f'  Picked: {selected}')
        print(f'  Actual result: {away} {away_score} - {home} {home_score}')
        print(f'  Winner: {winner}')
        print(f'  Marked correct: {bool(is_correct)}')
        print(f'  Should be correct: {selected == winner}')
        
        # Get total score
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