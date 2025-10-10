#!/usr/bin/env python3
"""
Debug the NFL week calculation step by step
"""

from datetime import datetime
import pytz

# Current time
est_tz = pytz.timezone('US/Eastern')
current_time = datetime.now(est_tz)

print(f"Current time: {current_time}")
print(f"Weekday: {current_time.weekday()} (0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday)")

# Manual calculation using the same logic as the function
season_start = datetime(2025, 9, 5)  # September 5, 2025 (Thursday)
print(f"Season start: {season_start}")

# Calculate days since season start
days_since_start = (current_time.replace(tzinfo=None) - season_start).days
print(f"Days since season start: {days_since_start}")

# Get the current weekday (0=Monday, 1=Tuesday, ..., 6=Sunday)
current_weekday = current_time.weekday()
print(f"Current weekday: {current_weekday}")

# Calculate base week (Thursday to Monday Night = 1 week)
base_week = (days_since_start // 7) + 1
print(f"Base week (days//7 + 1): {base_week}")

# NFL Week Advancement Logic:
week_day_offset = days_since_start % 7
print(f"Week day offset (days % 7): {week_day_offset}")

print(f"\nLogic check:")
print(f"- Is today Tuesday or Wednesday? {current_weekday in [1, 2]}")
print(f"- Week day offset >= 4? {week_day_offset >= 4}")

if current_weekday in [1, 2]:  # Tuesday or Wednesday
    if week_day_offset >= 4:  # Tuesday (4) or Wednesday (5)
        final_week = base_week + 1
        print(f"-> Advancing to next week: {final_week}")
    else:
        final_week = base_week
        print(f"-> Staying in current week: {final_week}")
else:
    final_week = base_week
    print(f"-> Using base week: {final_week}")

print(f"\n🏈 Final calculated week: {final_week}")