#!/usr/bin/env python3
"""
Monday Night Football Points Logic Example
This demonstrates how Monday Night games share the same deadline as Sunday games
"""

import sys
import os
from datetime import datetime, timedelta
import pytz

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def monday_night_logic_example():
    """
    Example of Monday Night Football deadline logic
    """
    
    print("🏈 MONDAY NIGHT FOOTBALL DEADLINE LOGIC")
    print("="*60)
    
    # Example NFL Week Schedule
    print("\n📅 EXAMPLE NFL WEEK SCHEDULE:")
    print("-" * 40)
    
    # Create example game times (AST timezone)
    ast_tz = pytz.timezone('America/Puerto_Rico')
    
    # Thursday Night Football
    thursday_game_time = ast_tz.localize(datetime(2025, 9, 11, 20, 15))  # 8:15 PM AST
    thursday_deadline = thursday_game_time - timedelta(minutes=30)  # 7:45 PM AST
    
    # Sunday Games (multiple)
    sunday_early_game = ast_tz.localize(datetime(2025, 9, 14, 13, 0))   # 1:00 PM AST
    sunday_late_game = ast_tz.localize(datetime(2025, 9, 14, 16, 25))   # 4:25 PM AST
    sunday_night_game = ast_tz.localize(datetime(2025, 9, 14, 20, 20))  # 8:20 PM AST
    
    # Monday Night Football
    monday_game_time = ast_tz.localize(datetime(2025, 9, 15, 20, 15))   # 8:15 PM AST
    
    # KEY LOGIC: Monday uses Sunday deadline
    # The deadline is 30 minutes before the FIRST Sunday game
    first_sunday_game = sunday_early_game  # 1:00 PM AST on Sunday
    shared_deadline = first_sunday_game - timedelta(minutes=30)  # 12:30 PM AST on Sunday
    
    print(f"Thursday Night: Chiefs @ Bills")
    print(f"  Game Time: {thursday_game_time.strftime('%A %B %d at %-I:%M %p AST')}")
    print(f"  Deadline:  {thursday_deadline.strftime('%A %B %d at %-I:%M %p AST')} (Individual)")
    print()
    
    print(f"Sunday Games:")
    print(f"  Early Game:  Saints @ Panthers   - {sunday_early_game.strftime('%-I:%M %p AST')}")
    print(f"  Late Game:   Cowboys @ Giants     - {sunday_late_game.strftime('%-I:%M %p AST')}")
    print(f"  Night Game:  Packers @ Bears      - {sunday_night_game.strftime('%-I:%M %p AST')}")
    print(f"  Shared Deadline: {shared_deadline.strftime('%A %B %d at %-I:%M %p AST')}")
    print("  (30 minutes before FIRST Sunday game)")
    print()
    
    print(f"Monday Night: Jets @ Dolphins")
    print(f"  Game Time: {monday_game_time.strftime('%A %B %d at %-I:%M %p AST')}")
    print(f"  Deadline:  {shared_deadline.strftime('%A %B %d at %-I:%M %p AST')} (SAME as Sunday)")
    print("  (Uses Sunday deadline, NOT individual deadline)")
    print()
    
    print("🔑 KEY POINTS:")
    print("-" * 40)
    print("1. Thursday games have INDIVIDUAL deadlines (30 min before each game)")
    print("2. Friday games have INDIVIDUAL deadlines (30 min before each game)")
    print("3. Saturday games have INDIVIDUAL deadlines (30 min before each game)")
    print("4. Sunday + Monday games SHARE the SAME deadline")
    print("5. Shared deadline = 30 minutes before FIRST Sunday game")
    print("6. Monday Night Football does NOT get its own deadline")
    print()
    
    print("⏰ DEADLINE TIMELINE:")
    print("-" * 40)
    print(f"Thu 7:45 PM AST - Thursday Night deadline")
    print(f"Sun 12:30 PM AST - Sunday/Monday shared deadline")
    print(f"                   (All Sunday games + Monday Night)")
    print()
    
    # Show the code logic
    print("💻 CODE LOGIC:")
    print("-" * 40)
    print("""
# 1. Separate games by day of week
sunday_monday_games = []  # Combined list for Sunday and Monday
for game in games:
    weekday = game_time.weekday()  # Monday=0, Sunday=6
    if weekday in [0, 6]:  # Monday or Sunday
        sunday_monday_games.append(game)

# 2. Find first Sunday game (earliest time)
first_sunday = min(sunday_monday_games, key=lambda x: x.game_time)

# 3. Calculate shared deadline (30 min before first Sunday)
shared_deadline = first_sunday.game_time - timedelta(minutes=30)

# 4. Apply shared deadline to ALL Sunday and Monday games
deadlines['sunday_games'] = {
    'deadline': shared_deadline,
    'game_time': first_sunday.game_time,
    'matchup': f"First Sunday Game: {first_sunday.away} @ {first_sunday.home}"
}

# 5. Monday Night uses the SAME deadline
deadlines['monday_night'] = {
    'deadline': shared_deadline,  # <-- SAME deadline
    'game_time': monday_game.game_time,
    'matchup': f"{monday_game.away} @ {monday_game.home}"
}
""")

def pick_submission_example():
    """
    Example of how pick submission works with Monday Night logic
    """
    
    print("\n" + "="*60)
    print("🎯 PICK SUBMISSION EXAMPLE")
    print("="*60)
    
    print("\n📝 USER PICK SCENARIOS:")
    print("-" * 40)
    
    # Times relative to deadlines
    ast_tz = pytz.timezone('America/Puerto_Rico')
    shared_deadline = ast_tz.localize(datetime(2025, 9, 14, 12, 30))  # Sunday 12:30 PM
    
    scenarios = [
        {
            'time': ast_tz.localize(datetime(2025, 9, 14, 11, 0)),  # Sunday 11:00 AM
            'description': "Sunday 11:00 AM - 1.5 hours before deadline",
            'allowed': True
        },
        {
            'time': ast_tz.localize(datetime(2025, 9, 14, 12, 45)),  # Sunday 12:45 PM
            'description': "Sunday 12:45 PM - 15 minutes after deadline",
            'allowed': False
        },
        {
            'time': ast_tz.localize(datetime(2025, 9, 15, 10, 0)),  # Monday 10:00 AM
            'description': "Monday 10:00 AM - Day of Monday Night game",
            'allowed': False
        },
        {
            'time': ast_tz.localize(datetime(2025, 9, 15, 19, 0)),  # Monday 7:00 PM
            'description': "Monday 7:00 PM - 1 hour before Monday Night game",
            'allowed': False
        }
    ]
    
    for scenario in scenarios:
        status = "✅ ALLOWED" if scenario['allowed'] else "❌ BLOCKED"
        print(f"{status} - {scenario['description']}")
        
        if scenario['allowed']:
            print("  → User can pick for Sunday games AND Monday Night game")
        else:
            hours_late = (scenario['time'] - shared_deadline).total_seconds() / 3600
            print(f"  → Deadline passed {hours_late:.1f} hours ago")
            print("  → NO picks allowed for Sunday or Monday games")
        print()
    
    print("🎲 PICK VALIDATION LOGIC:")
    print("-" * 40)
    print("""
def can_make_picks(week, year, game_date=None):
    deadlines = get_week_deadlines(week, year)
    now = datetime.now(ast_tz)
    
    if game_date:
        game_time = parse_game_date(game_date)
        weekday = game_time.weekday()
        
        if weekday == 0:  # Monday
            # Monday games use Sunday deadline
            deadline_info = deadlines.get('monday_night')
            return now < deadline_info['deadline']
        elif weekday == 6:  # Sunday
            # Sunday games use shared deadline
            deadline_info = deadlines.get('sunday_games')
            return now < deadline_info['deadline']
    
    # Both Sunday and Monday use the SAME deadline
    return now < shared_deadline
""")

def main():
    """Main example function"""
    monday_night_logic_example()
    pick_submission_example()
    
    print("\n" + "="*60)
    print("🏁 SUMMARY")
    print("="*60)
    print("Monday Night Football picks must be submitted by the Sunday deadline")
    print("(30 minutes before the first Sunday game of that week)")
    print("This prevents users from waiting to see Sunday results before")
    print("making their Monday Night Football picks.")

if __name__ == "__main__":
    main()
