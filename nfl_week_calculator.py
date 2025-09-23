#!/usr/bin/env python3
"""
NFL Week Calculation Utility
Calculates the current NFL week based on game completion status and dates
"""

import sqlite3
from datetime import datetime, timedelta
import pytz


def get_current_nfl_week(year=2025):
    """
    Calculate the current NFL week based on game completion and dates
    
    Logic:
    1. If it's before the first NFL game, return Week 1
    2. If all games for a week are complete, advance to next week
    3. Otherwise, return the week with incomplete games
    """
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get the current date in AST
        ast_tz = pytz.timezone('America/Puerto_Rico')
        current_time = datetime.now(ast_tz)
        
        # Get season start date from first game
        cursor.execute('''
            SELECT MIN(game_date) as season_start 
            FROM nfl_games 
            WHERE year = ?
        ''', (year,))
        
        result = cursor.fetchone()
        if not result or not result['season_start']:
            # No games in database, use calendar calculation
            return get_calendar_week(current_time, year)
        
        season_start_str = result['season_start']
        try:
            # Try ISO format first (with T)
            season_start = datetime.fromisoformat(season_start_str.replace('T', ' '))
        except ValueError:
            # Fallback to original format
            season_start = datetime.strptime(season_start_str, '%Y-%m-%d %H:%M:%S')
        
        # Convert to AST if naive
        if season_start.tzinfo is None:
            season_start_ast = ast_tz.localize(season_start)
        else:
            season_start_ast = season_start.astimezone(ast_tz)
        
        # If we're before the season starts, return Week 1
        if current_time < season_start_ast:
            conn.close()
            return 1
        
        # Check each week to find the current one
        # Logic: Return the first week with incomplete games, 
        # or advance past all complete weeks
        for week in range(1, 19):  # NFL has 18 weeks
            cursor.execute('''
                SELECT COUNT(*) as total_games,
                       COUNT(CASE WHEN is_final = 1 THEN 1 END) as completed_games
                FROM nfl_games 
                WHERE week = ? AND year = ?
            ''', (week, year))
            
            week_data = cursor.fetchone()
            
            if not week_data or week_data['total_games'] == 0:
                # No games this week, move to next
                continue
            
            total_games = week_data['total_games']
            completed_games = week_data['completed_games']
            
            # If not all games are complete, this is the current week
            if completed_games < total_games:
                conn.close()
                return week
            
            # All games are complete - this week is done, continue to next week
        
        # If we get here, all weeks with games are complete
        # Return the next week after the last week with games
        cursor.execute('''
            SELECT MAX(week) as last_week
            FROM nfl_games 
            WHERE year = ?
        ''', (year,))
        
        last_week_result = cursor.fetchone()
        if last_week_result and last_week_result['last_week']:
            last_week = last_week_result['last_week']
            next_week = min(last_week + 1, 18)
            conn.close()
            return next_week
        
        # Fallback
        conn.close()
        return 1
        
    except Exception as e:
        print(f"Error calculating NFL week: {e}")
        # Fallback to calendar calculation
        current_time = datetime.now(pytz.timezone('America/Puerto_Rico'))
        return get_calendar_week(current_time, year)


def get_calendar_week(current_time, year=2025):
    """
    Fallback calendar-based week calculation
    """
    try:
        # NFL season typically starts first Thursday of September
        season_start = datetime(year, 9, 5)  # September 5, 2025 (Thursday)
        
        # If before season start
        if current_time.replace(tzinfo=None) < season_start:
            return 1
        
        # Calculate weeks since start
        days_since_start = (current_time.replace(tzinfo=None) - season_start).days
        week = max(1, min(18, (days_since_start // 7) + 1))
        
        return week
        
    except Exception as e:
        print(f"Error in calendar calculation: {e}")
        return 1


if __name__ == "__main__":
    # Test the function
    week = get_current_nfl_week()
    print(f"Current NFL Week: {week}")
    
    # Test with database check
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT week, 
                   COUNT(*) as total,
                   COUNT(CASE WHEN is_final = 1 THEN 1 END) as completed
            FROM nfl_games 
            WHERE year = 2025 
            GROUP BY week 
            ORDER BY week
        ''')
        
        print("\nWeek Status:")
        for row in cursor.fetchall():
            week_num, total, completed = row
            status = "✅ Complete" if completed == total else f"⏳ {completed}/{total} done"
            print(f"Week {week_num}: {status}")
        
        conn.close()
        
    except Exception as e:
        print(f"Database check error: {e}")
