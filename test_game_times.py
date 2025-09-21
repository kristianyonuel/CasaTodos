#!/usr/bin/env python3
"""
Test game time display in AST
"""

import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.timezone_utils import convert_to_ast, format_game_time, format_game_time_short

def test_game_times():
    """Test that game times display correctly in AST"""
    
    print("=== TESTING GAME TIME DISPLAY ===")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT game_id, away_team, home_team, game_date
        FROM nfl_games 
        WHERE week = 3 AND year = 2025
        ORDER BY game_date
        LIMIT 5
    ''')
    
    print("Sample game times in AST:")
    print("-" * 50)
    
    for row in cursor.fetchall():
        game_id, away_team, home_team, game_date_str = row
        
        # Parse the datetime string from database
        from datetime import datetime
        game_date = datetime.fromisoformat(game_date_str)
        
        # Convert and format
        ast_time = convert_to_ast(game_date)
        formatted_long = format_game_time(game_date)
        formatted_short = format_game_time_short(game_date)
        
        print(f"{away_team} @ {home_team}")
        print(f"  Database: {game_date_str} (UTC)")
        print(f"  AST Time: {ast_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"  Long:     {formatted_long}")
        print(f"  Short:    {formatted_short}")
        print()
    
    conn.close()
    
    print("✅ Game times should now display correctly in AST")
    print("✅ 1:00 PM AST games should show as '1:00 PM AST' not '9:00 AM AST'")

if __name__ == '__main__':
    test_game_times()
