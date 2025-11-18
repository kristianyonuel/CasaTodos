#!/usr/bin/env python3
"""
Debug script to check deadline calculations and game times
"""
from __future__ import annotations

import sys
import os
import sqlite3
from datetime import datetime, timedelta
import pytz

# Add the current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from deadline_manager import DeadlineManager
    from utils.timezone_utils import convert_to_ast
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def debug_deadlines():
    """Debug deadline calculations"""
    print("Debugging Deadline Calculations")
    print("=" * 50)
    
    # Initialize timezone
    ast_tz = pytz.timezone('America/Puerto_Rico')
    now = datetime.now(ast_tz)
    
    print(f"Current time (AST): {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Current date: September 4, 2025")
    print()
    
    # Check database for games
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get today's games
        cursor.execute('''
            SELECT id, week, year, home_team, away_team, game_date, 
                   is_thursday_night, is_sunday_night, is_monday_night
            FROM nfl_games 
            WHERE date(game_date) = date('now')
            ORDER BY game_date
        ''')
        
        today_games = cursor.fetchall()
        
        if today_games:
            print(f"Found {len(today_games)} games for today:")
            print("-" * 30)
            
            for game in today_games:
                print(f"Game ID: {game['id']}")
                print(f"  Teams: {game['away_team']} @ {game['home_team']}")
                print(f"  Week {game['week']}, {game['year']}")
                print(f"  Raw game_date: {game['game_date']}")
                
                # Parse and convert game time
                try:
                    if isinstance(game['game_date'], str):
                        game_time = datetime.strptime(game['game_date'], '%Y-%m-%d %H:%M:%S')
                        print(f"  Parsed time (UTC): {game_time}")
                        
                        # Convert to AST
                        game_time_ast = convert_to_ast(game_time)
                        print(f"  Game time (AST): {game_time_ast.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                        
                        # Calculate deadline
                        deadline_offset = 30  # 30 minutes before
                        deadline = game_time_ast - timedelta(minutes=deadline_offset)
                        print(f"  Deadline (30 min before): {deadline.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                        
                        # Check status
                        hours_until_deadline = (deadline - now).total_seconds() / 3600
                        print(f"  Hours until deadline: {hours_until_deadline:.2f}")
                        
                        if hours_until_deadline > 0:
                            print(f"  Status: ✓ OPEN (deadline in {hours_until_deadline:.1f} hours)")
                        else:
                            print(f"  Status: ✗ CLOSED (deadline passed {abs(hours_until_deadline):.1f} hours ago)")
                        
                except Exception as e:
                    print(f"  Error parsing time: {e}")
                
                print()
        else:
            print("No games found for today")
            
            # Check for games this week
            cursor.execute('''
                SELECT id, week, year, home_team, away_team, game_date
                FROM nfl_games 
                WHERE week = 1 AND year = 2025
                ORDER BY game_date
                LIMIT 5
            ''')
            
            week_games = cursor.fetchall()
            if week_games:
                print(f"\nFound {len(week_games)} games for Week 1, 2025:")
                for i, game in enumerate(week_games, 1):
                    print(f"  {i}. {game['away_team']} @ {game['home_team']} - {game['game_date']}")
        
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")
        return False
    
    # Test deadline manager
    print("\nTesting DeadlineManager:")
    print("-" * 30)
    
    try:
        deadline_manager = DeadlineManager()
        summary = deadline_manager.get_deadline_summary(1, 2025)
        
        print("Deadline Summary:")
        for key, value in summary.items():
            if value and isinstance(value, dict):
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"DeadlineManager error: {e}")
        import traceback
        traceback.print_exc()
    
    return True

if __name__ == "__main__":
    debug_deadlines()
