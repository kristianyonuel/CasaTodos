#!/usr/bin/env python3
"""
Test the updated deadline logic:
- Thursday games: 30 minutes before kickoff
- Sunday/Monday games: 30 minutes before first Sunday game
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deadline_manager import DeadlineManager
from datetime import datetime

def test_deadline_logic():
    """Test the new deadline system"""
    
    dm = DeadlineManager()
    
    print("🕐 Testing NFL Game Deadline Logic")
    print("=" * 50)
    
    # Test with current week
    week = 1
    year = 2025
    
    print(f"📅 Testing Week {week}, {year}")
    print()
    
    deadlines = dm.get_week_deadlines(week, year)
    
    print("🏈 Deadline Configuration:")
    print(f"   Thursday Night: {dm.deadline_offsets['thursday_night']} minutes before kickoff")
    print(f"   Sunday Games: {dm.deadline_offsets['sunday_games']} minutes before first Sunday game")
    print(f"   Monday Night: Uses same deadline as Sunday games")
    print()
    
    print("📋 Week Deadlines:")
    
    for game_type, info in deadlines.items():
        if info:
            print(f"   {game_type.replace('_', ' ').title()}:")
            print(f"      Matchup: {info['matchup']}")
            print(f"      Game Time: {info['game_time'].strftime('%A %B %d, %I:%M %p AST')}")
            print(f"      Deadline: {info['deadline'].strftime('%A %B %d, %I:%M %p AST')}")
            print(f"      Status: {info['status']['status']}")
            if 'hours_remaining' in info['status']:
                hours = info['status']['hours_remaining']
                if hours > 0:
                    print(f"      Time Remaining: {hours:.1f} hours")
                else:
                    print(f"      Deadline Passed: {abs(hours):.1f} hours ago")
            print()
    
    # Verify Monday uses Sunday deadline
    if deadlines.get('sunday_games') and deadlines.get('monday_night'):
        sunday_deadline = deadlines['sunday_games']['deadline']
        monday_deadline = deadlines['monday_night']['deadline']
        
        if sunday_deadline == monday_deadline:
            print("✅ CORRECT: Monday games use the same deadline as Sunday games")
        else:
            print("❌ ERROR: Monday games have different deadline than Sunday games")
            print(f"   Sunday deadline: {sunday_deadline}")
            print(f"   Monday deadline: {monday_deadline}")
    
    print()
    print("🎯 Summary:")
    print(f"   This system ensures that:")
    print(f"   - Thursday games have individual 30-minute deadlines")
    print(f"   - All Sunday and Monday games share one deadline:")
    print(f"     30 minutes before the first Sunday game")
    print(f"   - Players must submit all Sunday/Monday picks before the")
    print(f"     first Sunday game starts")

if __name__ == '__main__':
    test_deadline_logic()
