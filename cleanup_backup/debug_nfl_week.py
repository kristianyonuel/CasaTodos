#!/usr/bin/env python3
"""
Debug NFL Week Calculation
"""

import sqlite3
from datetime import datetime
import pytz

# Current time
est_tz = pytz.timezone('US/Eastern')
current_time = datetime.now(est_tz)

print(f"Current time: {current_time}")
print(f"Weekday: {current_time.weekday()} (0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday)")

# Season start 
season_start = datetime(2025, 9, 5)  # September 5, 2025 - First game KC vs LAC
print(f"Season start: {season_start}")

# Calculate days since start
days_since_start = (current_time.replace(tzinfo=None) - season_start).days
print(f"Days since season start: {days_since_start}")

# Base week calculation
base_week = (days_since_start // 7) + 1
print(f"Base week (days/7 + 1): {base_week}")

# Week offset within current week
week_offset = days_since_start % 7
print(f"Week offset (days % 7): {week_offset}")
print(f"This means we're {week_offset} days into the current week")

# Check database
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
    
    print(f"\nDatabase Week Status:")
    for row in cursor.fetchall():
        week_num, total, completed = row
        status = "✅ Complete" if completed == total else f"⏳ {completed}/{total} done"
        print(f"Week {week_num}: {status}")
    
    conn.close()
    
except Exception as e:
    print(f"Database check error: {e}")

# Manual week 6 check
print(f"\nShould we advance to Week 6?")
print(f"Today is Tuesday (weekday {current_time.weekday()})")
print(f"NFL weeks run Thursday to Monday Night")
print(f"Tuesday should be prep for next week = Week 6")