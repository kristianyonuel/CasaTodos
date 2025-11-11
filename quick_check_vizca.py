import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Check VIZCA's MNF pick
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
    WHERE up.user_id = 9 AND ng.home_team = 'Dallas Cowboys' AND ng.week = 9
""")

result = cursor.fetchone()
if result:
    selected, home, away, home_score, away_score, is_correct = result
    winner = away if away_score > home_score else home
    print(f'MNF: {away} @ {home} ({away_score}-{home_score})')
    print(f'VIZCA picked: {selected}')
    print(f'Winner: {winner}')
    print(f'VIZCA is_correct: {is_correct}')
    
    if selected == 'Arizona Cardinals' and not is_correct:
        print('VIZCA picked Cardinals correctly but database shows wrong!')

conn.close()