import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🏈 WEEK 9 GAME RESULTS IN DATABASE")
print("=" * 80)

cursor.execute('''
    SELECT game_id, home_team, away_team, home_score, away_score, game_date, is_final
    FROM nfl_games 
    WHERE week = 9 
    ORDER BY game_date
''')

games = cursor.fetchall()

for i, game in enumerate(games, 1):
    game_id, home_team, away_team, home_score, away_score, game_date, is_final = game
    
    # Determine winner
    if home_score > away_score:
        winner = home_team
        winner_score = home_score
        loser_score = away_score
    else:
        winner = away_team
        winner_score = away_score
        loser_score = home_score
    
    print(f"Game {i}: {away_team} {away_score} - {home_team} {home_score}")
    print(f"  Winner: {winner} ({winner_score}-{loser_score})")
    print(f"  Date: {game_date}")
    print(f"  Final: {'Yes' if is_final else 'No'}")
    print()

conn.close()