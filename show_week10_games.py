import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🏈 WEEK 10 GAMES IN DATABASE")
print("=" * 60)

cursor.execute('''
    SELECT game_id, away_team, home_team, game_date, tv_network, stadium
    FROM nfl_games 
    WHERE week = 10 AND year = 2025
    ORDER BY game_date
''')

games = cursor.fetchall()

print(f"Found {len(games)} Week 10 games:")
print("-" * 60)

for i, (game_id, away, home, date, tv, stadium) in enumerate(games, 1):
    print(f"{i:2d}. {away:20s} @ {home:20s}")
    print(f"    Date: {date}")
    print(f"    TV: {tv or 'TBD'} | Stadium: {stadium or 'TBD'}")
    print()

conn.close()