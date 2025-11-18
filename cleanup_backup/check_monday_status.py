#!/usr/bin/env python3
"""
Check Monday games status for Week 4
"""

import sqlite3

def check_monday_games():
    print("=== WEEK 4 MONDAY GAMES STATUS ===")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get all Monday games for Week 4
    cursor.execute('''
        SELECT away_team, home_team, game_date, is_final, 
               strftime('%w', game_date) as day_of_week
        FROM nfl_games 
        WHERE week = 4 AND year = 2025 
        AND strftime('%w', game_date) = '1'
        ORDER BY game_date
    ''')
    
    monday_games = cursor.fetchall()
    
    print(f"Total Monday games found: {len(monday_games)}")
    print()
    
    for i, (away, home, date, is_final, dow) in enumerate(monday_games, 1):
        status = "FINAL" if is_final else "Scheduled"
        print(f"{i}. {away} @ {home}")
        print(f"   Date: {date}")
        print(f"   Status: {status}")
        print()
    
    # Check what games are still pending
    remaining_games = [game for game in monday_games if not game[3]]
    print(f"Games still to be played: {len(remaining_games)}")
    
    for away, home, date, _, _ in remaining_games:
        print(f"  • {away} @ {home} - {date}")
    
    conn.close()

if __name__ == "__main__":
    check_monday_games()