#!/usr/bin/env python3
"""
NFL Week Calculation Utility
Calculates the current NFL week based on game completion status and dates
"""

import sqlite3
from datetime import datetime, timedelta
import pytz


def get_current_nfl_week(year=2025):
    return 10  # FORCED TO WEEK 10

def get_current_nfl_week_original(year=2025):
    """
    Calculate the current NFL week based on calendar dates and NFL week cycle
    
    NFL Week Cycle Logic:
    - NFL weeks run Thursday to Monday Night
    - Tuesday/Wednesday = Next week's prep (advance to next week)
    - Thursday-Monday = Current week's games
    
    Logic:
    1. Use calendar-based calculation with NFL week boundaries
    2. Check for Tuesday/Wednesday advancement rule
    3. Validate against database games if available
    """
    
    try:
        # Get the current date in EST (NFL operates on Eastern Time)
        est_tz = pytz.timezone('US/Eastern')
        current_time = datetime.now(est_tz)
        
        # Get calendar-based week first (this respects the Thursday start)
        calendar_week = get_calendar_week_with_boundaries(current_time, year)
        
        # Connect to database to validate
        conn = sqlite3.connect('nfl_fantasy.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if we have games for the calendar week
        cursor.execute('''
            SELECT COUNT(*) as total_games,
                   COUNT(CASE WHEN is_final = 1 THEN 1 END) as completed_games,
                   MAX(game_date) as latest_game
            FROM nfl_games 
            WHERE week = ? AND year = ?
        ''', (calendar_week, year))
        
        week_data = cursor.fetchone()
        
        if week_data and week_data['total_games'] > 0:
            # We have games for this week
            total_games = week_data['total_games']
            completed_games = week_data['completed_games']
            
            # Tuesday/Wednesday: only advance if current week is complete
            if current_time.weekday() in [1, 2]:  # Tuesday = 1, Wednesday = 2
                # Check if current week is complete before advancing
                if completed_games >= total_games - 1:  # Allow 1 pending game
                    # Current week done, advance to next calendar week
                    next_week = calendar_week + 1
                    if next_week <= 18:
                        conn.close()
                        return next_week
                
                # Current week has games remaining, stay on current week
                conn.close()
                return calendar_week
            
            conn.close()
            return calendar_week
        
        # No games for calendar week, check if we need to look ahead
        if calendar_week < 18:
            # Check if next week has games
            cursor.execute('''
                SELECT COUNT(*) as total_games
                FROM nfl_games 
                WHERE week = ? AND year = ?
            ''', (calendar_week + 1, year))
            
            next_week_data = cursor.fetchone()
            if next_week_data and next_week_data['total_games'] > 0:
                conn.close()
                return calendar_week + 1
        
        conn.close()
        return calendar_week
        
    except Exception as e:
        print(f"Error calculating NFL week: {e}")
        # Fallback to calendar calculation
        current_time = datetime.now(pytz.timezone('US/Eastern'))
        return get_calendar_week_with_boundaries(current_time, year)


def get_calendar_week_with_boundaries(current_time, year=2025):
    """
    Calendar-based week calculation with NFL week boundaries
    NFL weeks run Thursday to Monday Night
    Tuesday/Wednesday = prep for next week
    """
    try:
        # NFL season starts September 5, 2025 (Thursday)
        season_start = datetime(year, 9, 5)  # September 5, 2025 (Thursday)
        
        # If before season start
        if current_time.replace(tzinfo=None) < season_start:
            return 1
        
        # Calculate days since season start
        days_since_start = (current_time.replace(tzinfo=None) - season_start).days
        
        # Get the current weekday (0=Monday, 1=Tuesday, ..., 6=Sunday)
        current_weekday = current_time.weekday()
        
        # Calculate base week (Thursday to Monday Night = 1 week)
        base_week = (days_since_start // 7) + 1
        
        # NFL Week Advancement Logic:
        # - Thursday to Monday Night = Current week
        # - Tuesday/Wednesday = Next week (prep period)
        
        # If it's Tuesday (1) or Wednesday (2), advance to next week
        if current_weekday in [1, 2]:  # Tuesday or Wednesday
            # We're in the "between weeks" prep period
            # Check if enough days have passed to be in next week
            week_day_offset = days_since_start % 7
            
            # Season started Friday Sept 5, so:
            # Fri=0, Sat=1, Sun=2, Mon=3, Tue=4, Wed=5, Thu=6
            # Tuesday (4) and Wednesday (5) should advance to next week
            if week_day_offset >= 4:  # Tuesday (4) or Wednesday (5)
                base_week += 1
        
        return max(1, min(18, base_week))
        
    except Exception as e:
        print(f"Error in calendar calculation: {e}")
        return 1


def get_calendar_week(current_time, year=2025):
    """
    Fallback calendar-based week calculation (original)
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
