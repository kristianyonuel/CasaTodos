import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('=== Week 2 Leaderboard Test ===')

# Check completed games count
cursor.execute('''
    SELECT COUNT(*) as completed_count FROM nfl_games 
    WHERE week = 2 AND year = 2025 AND is_final = 1
''')
completed_count = cursor.fetchone()[0]
print(f'Completed games for Week 2: {completed_count}')

if completed_count > 0:
    print('✅ Weekly leaderboard should now be available!')
    
    # Test the leaderboard query
    cursor.execute('''
        SELECT u.id, u.username,
               COUNT(p.id) as total_picks,
               SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks
        FROM users u
        JOIN user_picks p ON u.id = p.user_id
        JOIN nfl_games g ON p.game_id = g.id
        WHERE g.week = 2 AND g.year = 2025 AND g.is_final = 1 AND u.is_admin = 0
        GROUP BY u.id, u.username
        HAVING total_picks > 0
        ORDER BY correct_picks DESC, u.username
    ''')
    
    results = cursor.fetchall()
    if results:
        print(f'\nLeaderboard preview ({len(results)} users):')
        for i, (user_id, username, total_picks, correct_picks) in enumerate(results, 1):
            print(f'{i}. {username}: {correct_picks}/{total_picks} correct')
    else:
        print('\n❌ No users with picks for completed games')

    # Check who picked what for the completed game
    print('\n=== WSH @ GB Pick Details ===')
    cursor.execute('''
        SELECT u.username, p.selected_team, p.is_correct,
               p.predicted_away_score, p.predicted_home_score
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        JOIN nfl_games g ON p.game_id = g.id
        WHERE g.week = 2 AND g.year = 2025 
        AND g.away_team = 'WSH' AND g.home_team = 'GB'
        ORDER BY u.username
    ''')
    
    picks = cursor.fetchall()
    for username, selected_team, is_correct, pred_away, pred_home in picks:
        result = '✅' if is_correct else '❌'
        pred_score = f'(predicted: WSH {pred_away or "?"} - GB {pred_home or "?"})'
        print(f'{username}: picked {selected_team} {result} {pred_score}')

else:
    print('❌ Still no completed games')

conn.close()
