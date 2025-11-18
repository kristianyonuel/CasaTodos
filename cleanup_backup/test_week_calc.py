#!/usr/bin/env python3
"""
Test the updated NFL week calculator
"""

from datetime import datetime
import pytz
from nfl_week_calculator import get_current_nfl_week, get_calendar_week_with_boundaries

# Current time
est_tz = pytz.timezone('US/Eastern')
current_time = datetime.now(est_tz)

print(f"Current time: {current_time}")
print(f"Weekday: {current_time.weekday()} (0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday)")

# Test current NFL week
current_week = get_current_nfl_week()
print(f"\n🏈 Current NFL Week: {current_week}")

# Test calendar week calculation
calendar_week = get_calendar_week_with_boundaries(current_time)
print(f"📅 Calendar Week: {calendar_week}")

print(f"\nExpected: Week 6 (Tuesday should advance to next week)")