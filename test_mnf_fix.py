#!/usr/bin/env python3
"""
Test the fixed Monday Night Football detection for Week 5
"""

import sqlite3

def test_mnf_detection():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("=== TESTING MONDAY NIGHT FOOTBALL DETECTION FIX ===")
    
    # Test the old method (strftime)
    cursor.execute('''
        SELECT id, away_team, home_team FROM nfl_games 
        WHERE week = 5 AND year = 2025 
        AND strftime('%w', game_date) = '1'  -- Monday
        ORDER BY game_date DESC, id DESC
        LIMIT 1
    ''')
    
    old_method_result = cursor.fetchone()
    if old_method_result:
        print(f"OLD METHOD (strftime): Game {old_method_result[0]} - {old_method_result[1]} @ {old_method_result[2]}")
    else:
        print("OLD METHOD: No Monday game found")
    
    # Test the new method (is_monday_night flag)
    cursor.execute('''
        SELECT id, away_team, home_team FROM nfl_games 
        WHERE week = 5 AND year = 2025 
        AND is_monday_night = 1
        ORDER BY game_date DESC, id DESC
        LIMIT 1
    ''')
    
    new_method_result = cursor.fetchone()
    if new_method_result:
        print(f"NEW METHOD (is_monday_night): Game {new_method_result[0]} - {new_method_result[1]} @ {new_method_result[2]}")
    else:
        print("NEW METHOD: No Monday Night Football game found")
    
    print()
    print("=== COMPARISON ===")
    if old_method_result and new_method_result:
        if old_method_result[0] == new_method_result[0]:
            print("✅ SAME GAME: Both methods return the same game")
        else:
            print("❌ DIFFERENT GAMES: Methods return different games!")
            print(f"   Old: {old_method_result[1]} @ {old_method_result[2]} (ID: {old_method_result[0]})")
            print(f"   New: {new_method_result[1]} @ {new_method_result[2]} (ID: {new_method_result[0]})")
    elif not old_method_result and not new_method_result:
        print("⚠️  NO GAMES: Neither method found a Monday Night game")
    else:
        print("❌ INCONSISTENT: One method found a game, the other didn't")
    
    print()
    print("=== ALL WEEK 5 GAMES WITH MNF FLAG ===")
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_monday_night 
        FROM nfl_games 
        WHERE week = 5 AND year = 2025 
        ORDER BY game_date, id
    ''')
    
    all_games = cursor.fetchall()
    for game in all_games:
        game_id, away, home, game_date, is_mnf = game
        mnf_flag = " (🏈 MNF)" if is_mnf else ""
        print(f"  Game {game_id}: {away} @ {home} - {game_date}{mnf_flag}")
    
    conn.close()

if __name__ == "__main__":
    test_mnf_detection()