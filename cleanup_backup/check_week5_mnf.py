#!/usr/bin/env python3
"""
Check Week 5 games and Monday Night detection issue
"""

import sqlite3
from datetime import datetime

def check_week5_games():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("=== WEEK 5 GAMES ANALYSIS ===")
    
    # Check Week 5 games
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_final, 
               home_score, away_score, is_monday_night
        FROM nfl_games 
        WHERE week = 5 AND year = 2025 
        ORDER BY game_date, id
    ''')
    games = cursor.fetchall()
    
    print(f'Found {len(games)} Week 5 games:')
    for game in games:
        game_id, away, home, game_date, is_final, h_score, a_score, is_mnf = game
        
        # Parse the date to see what day it is
        try:
            if isinstance(game_date, str):
                if 'T' in game_date:
                    dt = datetime.fromisoformat(game_date.replace('T', ' '))
                else:
                    dt = datetime.strptime(game_date, '%Y-%m-%d %H:%M:%S')
            else:
                dt = game_date
            
            day_of_week = dt.strftime('%A')
            formatted_date = dt.strftime('%m/%d %I:%M %p')
            weekday_num = dt.weekday()  # Monday = 0, Sunday = 6
        except Exception as e:
            day_of_week = 'Unknown'
            formatted_date = str(game_date)
            weekday_num = -1
        
        status = 'FINAL' if is_final else 'SCHEDULED'
        mnf_flag = ' (MNF in DB)' if is_mnf else ''
        
        if is_final and h_score is not None:
            score = f'{away} {a_score} - {h_score} {home}'
        else:
            score = f'{away} @ {home}'
            
        print(f'  {game_id}: {score}')
        print(f'    Date: {day_of_week} {formatted_date} (weekday: {weekday_num})')
        print(f'    Status: {status}{mnf_flag}')
        print()
    
    print("=== MONDAY NIGHT DETECTION CHECK ===")
    
    # Check what the system thinks is the Monday Night game using SQL weekday
    cursor.execute('''
        SELECT id, away_team, home_team, game_date FROM nfl_games 
        WHERE week = 5 AND year = 2025 
        AND strftime('%w', game_date) = '1'  -- Monday (0=Sunday, 1=Monday)
        ORDER BY game_date DESC, id DESC
        LIMIT 1
    ''')
    
    monday_night_game = cursor.fetchone()
    if monday_night_game:
        game_id, away, home, game_date = monday_night_game
        print(f'System detected Monday Night game:')
        print(f'  ID: {game_id}')
        print(f'  Game: {away} @ {home}')
        print(f'  Date: {game_date}')
    else:
        print('No Monday game detected by strftime method')
    
    # Check all games by actual day of week
    print("\n=== GAMES BY DAY OF WEEK ===")
    for game in games:
        game_id, away, home, game_date, is_final, h_score, a_score, is_mnf = game
        
        try:
            if isinstance(game_date, str):
                if 'T' in game_date:
                    dt = datetime.fromisoformat(game_date.replace('T', ' '))
                else:
                    dt = datetime.strptime(game_date, '%Y-%m-%d %H:%M:%S')
            
            # Check if it's actually Monday
            if dt.weekday() == 0:  # Monday = 0
                print(f'  ACTUAL MONDAY: {away} @ {home} on {dt}')
            elif dt.weekday() == 6:  # Sunday = 6
                print(f'  Sunday: {away} @ {home} on {dt}')
        except:
            print(f'  Could not parse date for game {game_id}')
    
    conn.close()

if __name__ == "__main__":
    check_week5_games()