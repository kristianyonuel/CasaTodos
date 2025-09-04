#!/usr/bin/env python3
"""
Quick test for current deadline status
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import pytz

# Test the deadline logic
ast_tz = pytz.timezone('America/Puerto_Rico')
now = datetime.now(ast_tz)

print("Current Deadline Test")
print("=" * 30)
print(f"Current time (AST): {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")

# Simulate game in 1 hour
game_in_1_hour = now + timedelta(hours=1)
print(f"Game starts in 1 hour: {game_in_1_hour.strftime('%Y-%m-%d %H:%M:%S %Z')}")

# Test different deadline offsets
offsets = [5, 15, 30, 60]
for offset in offsets:
    deadline = game_in_1_hour - timedelta(minutes=offset)
    is_open = now < deadline
    minutes_remaining = (deadline - now).total_seconds() / 60
    
    status = "OPEN" if is_open else "CLOSED"
    if is_open:
        print(f"  {offset:2d} min before: {status} ({minutes_remaining:+.1f} min remaining)")
    else:
        print(f"  {offset:2d} min before: {status} (passed {abs(minutes_remaining):.1f} min ago)")

print("\nWith new settings (5 min for TNF/MNF, 15 min for Sunday):")
print("- Thursday/Monday games: Deadline 5 minutes before = OPEN until 55 minutes from now")  
print("- Sunday games: Deadline 15 minutes before = OPEN until 45 minutes from now")
print("\nPicks should now be ALLOWED for the current game!")
