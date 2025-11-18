import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('RADA Week 9 Analysis:')
print('=' * 25)

# Get RADA's user ID
cursor.execute("SELECT id FROM users WHERE UPPER(username) = 'RADA'")
rada_id_result = cursor.fetchone()
if rada_id_result:
    rada_id = rada_id_result[0]
    print(f'RADA user ID: {rada_id}')
else:
    print('RADA user not found!')
    exit()

# Check RADA's Monday Night Football pick
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
""", (rada_id,))

mnf_result = cursor.fetchone()
if mnf_result:
    selected, away, home, away_score, home_score, is_correct = mnf_result
    winner = away if away_score > home_score else home
    
    print(f'\nMonday Night Football:')
    print(f'  Game: {away} @ {home} ({away_score}-{home_score})')
    print(f'  RADA picked: {selected}')
    print(f'  Winner: {winner}')
    print(f'  RADA correct: {"YES" if is_correct else "NO"}')

# Get RADA's total Week 9 score
cursor.execute("""
    SELECT COUNT(CASE WHEN up.is_correct = 1 THEN 1 END)
    FROM user_picks up
    JOIN nfl_games ng ON up.game_id = ng.game_id
    WHERE up.user_id = ? AND ng.week = 9
""", (rada_id,))

rada_total = cursor.fetchone()[0]
print(f'\nRADA Week 9 Total: {rada_total}/14')

# Show all of RADA's Week 9 picks
cursor.execute("""
    SELECT 
        ng.away_team,
        ng.home_team,
        ng.away_score,
        ng.home_score,
        up.selected_team,
        up.is_correct
    FROM user_picks up
    JOIN nfl_games ng ON up.game_id = ng.game_id
    WHERE up.user_id = ? AND ng.week = 9
    ORDER BY ng.game_id
""", (rada_id,))

all_picks = cursor.fetchall()
print(f'\nRADA\'s All Week 9 Picks:')
print('=' * 35)

correct_count = 0
for away, home, away_score, home_score, selected, is_correct in all_picks:
    if is_correct:
        correct_count += 1
    winner = away if away_score > home_score else home
    result_symbol = "✅" if is_correct else "❌"
    
    print(f'{away} @ {home} ({away_score}-{home_score})')
    print(f'  RADA picked: {selected} {result_symbol}')
    if home == 'Dallas Cowboys':
        print('  🏈 MONDAY NIGHT FOOTBALL')

print(f'\nVerification: {correct_count}/14 correct picks')

# Compare with other top users
cursor.execute("""
    SELECT 
        u.username,
        COUNT(CASE WHEN up.is_correct = 1 THEN 1 END) as correct_picks
    FROM users u
    LEFT JOIN user_picks up ON u.id = up.user_id
    LEFT JOIN nfl_games ng ON up.game_id = ng.game_id
    WHERE ng.week = 9 AND u.username IN ('rada', 'jean', 'vizca')
    GROUP BY u.id, u.username
    ORDER BY correct_picks DESC
""")

comparison = cursor.fetchall()
print(f'\nComparison with Top Users:')
print('=' * 30)
for username, correct in comparison:
    print(f'{username.upper()}: {correct}/14')

conn.close()