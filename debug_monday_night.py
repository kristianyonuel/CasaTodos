#!/usr/bin/env python3

import sqlite3

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print('=== Current Week Games ===')
cursor.execute('''
    SELECT id, game_date, away_team, home_team, is_monday_night,
           strftime('%w', game_date) as day_of_week
    FROM nfl_games 
    WHERE week = 1 AND year = 2025 
    ORDER BY game_date
''')

games = cursor.fetchall()
for game in games:
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_name = day_names[int(game['day_of_week'])]
    print(f'Game {game["id"]}: {game["away_team"]} @ {game["home_team"]} - {game["game_date"]} ({day_name}) - MNF Flag: {game["is_monday_night"]}')

print('\n=== Monday Night Football Detection Logic ===')
cursor.execute('''
    SELECT id, game_date, away_team, home_team 
    FROM nfl_games 
    WHERE week = 1 AND year = 2025 
    AND strftime('%w', game_date) = '1'
    ORDER BY game_date DESC, id DESC
    LIMIT 1
''')

monday_game = cursor.fetchone()
if monday_game:
    print(f'Detected MNF Game: {monday_game["away_team"]} @ {monday_game["home_team"]} (ID: {monday_game["id"]})')
else:
    print('No Monday games found!')

print('\n=== All Monday Games ===')
cursor.execute('''
    SELECT id, game_date, away_team, home_team 
    FROM nfl_games 
    WHERE week = 1 AND year = 2025 
    AND strftime('%w', game_date) = '1'
    ORDER BY game_date DESC, id DESC
''')

monday_games = cursor.fetchall()
for game in monday_games:
    print(f'Monday Game: {game["away_team"]} @ {game["home_team"]} (ID: {game["id"]}) - {game["game_date"]}')

conn.close()
