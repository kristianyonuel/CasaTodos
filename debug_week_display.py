#!/usr/bin/env python3
"""
Debug Week Display Issue
Check various sources of week information
"""

from datetime import datetime
import pytz
from nfl_week_calculator import get_current_nfl_week, get_calendar_week_with_boundaries
import sqlite3

# Current time
est_tz = pytz.timezone('US/Eastern')
current_time = datetime.now(est_tz)

print(f"🕐 Current time: {current_time}")
print(f"📅 Weekday: {current_time.weekday()} (0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday)")
print()

# Test week calculations
print("🏈 Week Calculator Results:")
current_week = get_current_nfl_week()
print(f"   get_current_nfl_week(): {current_week}")

calendar_week = get_calendar_week_with_boundaries(current_time)
print(f"   get_calendar_week_with_boundaries(): {calendar_week}")
print()

# Check database weeks
print("💾 Database Week Status:")
try:
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get all weeks with game counts
    cursor.execute('SELECT week, COUNT(*) as games FROM nfl_games WHERE year = 2025 GROUP BY week ORDER BY week')
    weeks = cursor.fetchall()
    
    for week, count in weeks:
        status = "✅" if count > 0 else "❌"
        print(f"   Week {week}: {status} {count} games")
    
    # Check what week has the most recent games
    cursor.execute('''
        SELECT week, MAX(game_date) as latest_game 
        FROM nfl_games 
        WHERE year = 2025 AND game_date <= ? 
        GROUP BY week 
        ORDER BY week DESC 
        LIMIT 3
    ''', (current_time.strftime('%Y-%m-%d %H:%M:%S'),))
    
    recent_weeks = cursor.fetchall()
    print()
    print("📊 Recent weeks with games:")
    for week, latest_game in recent_weeks:
        print(f"   Week {week}: Latest game on {latest_game}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error checking database: {e}")

print()
print("🎯 Expected: Week 6 (Thursday, October 10, 2025)")
print("💡 If you're seeing Week 5 somewhere, it might be:")
print("   - Cached data in your browser")
print("   - Old server code not updated")
print("   - Different calculation logic somewhere else")