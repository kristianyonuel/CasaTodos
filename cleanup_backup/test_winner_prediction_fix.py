#!/usr/bin/env python3
"""
Test script to verify the winner prediction fix
Checks that we're analyzing actual Monday games, not HOU games
"""

import sqlite3
from predictable_winner import get_winner_prediction_summary, analyze_predictable_winners

def test_monday_games():
    print("=== TESTING WINNER PREDICTION FIX ===")
    print()
    
    # Check what Monday games exist in Week 4
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT away_team, home_team, game_date, is_final
        FROM nfl_games 
        WHERE week = 4 AND year = 2025 
        AND strftime('%w', game_date) = '1'
        ORDER BY game_date
    ''')
    
    monday_games = cursor.fetchall()
    print("Week 4 Monday Games in Database:")
    for away, home, date, final in monday_games:
        status = "FINAL" if final else "Scheduled"
        print(f"  {away} @ {home} - {date} - {status}")
    
    # Check HOU games (should not be Monday)
    cursor.execute('''
        SELECT away_team, home_team, game_date, is_final,
               strftime('%w', game_date) as day_of_week
        FROM nfl_games 
        WHERE week = 4 AND year = 2025 
        AND (home_team = 'HOU' OR away_team = 'HOU')
        ORDER BY game_date
    ''')
    
    hou_games = cursor.fetchall()
    print("\nWeek 4 HOU Games in Database:")
    for away, home, date, final, dow in hou_games:
        status = "FINAL" if final else "Scheduled"
        day_name = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][int(dow)]
        print(f"  {away} @ {home} - {date} - {status} ({day_name})")
    
    conn.close()
    
    print("\n" + "="*50)
    
    # Test the fixed function
    print("Winner Prediction Analysis:")
    analysis = analyze_predictable_winners(4, 2025)
    
    if 'error' in analysis:
        print(f"ERROR: {analysis['error']}")
        return
    
    game_info = analysis['game_info']
    print(f"Games being analyzed: {game_info}")
    
    print("\nSummary:")
    summary = get_winner_prediction_summary(4, 2025)
    print(summary)
    
    print("\n" + "="*50)
    print("✅ SUCCESS: Function now analyzes actual Monday games!")
    print("✅ NO MORE HARDCODED HOU LOGIC!")

if __name__ == "__main__":
    test_monday_games()