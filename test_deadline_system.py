#!/usr/bin/env python3
"""
Test script to verify the deadline system integration.
"""
from __future__ import annotations

import sys
import os
from datetime import datetime, timedelta
from deadline_manager import DeadlineManager

def test_deadline_system():
    """Test the deadline system functionality."""
    print("Testing Deadline System Integration")
    print("=" * 50)
    
    # Initialize deadline manager
    deadline_manager = DeadlineManager()
    
    # Test current week
    current_week = 1
    current_year = 2025
    
    print(f"\nTesting Week {current_week}, {current_year}")
    print("-" * 30)
    
    # Get deadlines
    deadlines = deadline_manager.get_week_deadlines(current_week, current_year)
    print(f"Deadlines for Week {current_week}:")
    if deadlines.thursday:
        print(f"  Thursday Night: {deadlines.thursday.strftime('%A, %B %d at %I:%M %p AST')}")
    if deadlines.sunday:
        print(f"  Sunday Games:   {deadlines.sunday.strftime('%A, %B %d at %I:%M %p AST')}")
    if deadlines.monday:
        print(f"  Monday Night:   {deadlines.monday.strftime('%A, %B %d at %I:%M %p AST')}")
    
    # Get deadline status
    status = deadline_manager.get_deadline_status(current_week, current_year)
    print(f"\nDeadline Status:")
    if status.thursday:
        print(f"  Thursday Night: {'PASSED' if status.thursday.passed else 'OPEN'} "
              f"({status.thursday.hours_until:.1f} hours)")
    if status.sunday:
        print(f"  Sunday Games:   {'PASSED' if status.sunday.passed else 'OPEN'} "
              f"({status.sunday.hours_until:.1f} hours)")
    if status.monday:
        print(f"  Monday Night:   {'PASSED' if status.monday.passed else 'OPEN'} "
              f"({status.monday.hours_until:.1f} hours)")
    
    # Test pick availability for different game types
    print(f"\nPick Availability Test:")
    
    # Test Thursday game (simulate game time)
    thursday_game_time = deadlines.thursday if deadlines.thursday else datetime.now()
    can_pick_thursday = deadline_manager.can_make_picks(current_week, current_year, thursday_game_time)
    print(f"  Thursday Night Game: {'✓ Can pick' if can_pick_thursday else '✗ Cannot pick'}")
    
    # Test Sunday game (simulate game time)
    sunday_game_time = deadlines.sunday if deadlines.sunday else datetime.now()
    can_pick_sunday = deadline_manager.can_make_picks(current_week, current_year, sunday_game_time)
    print(f"  Sunday Game:         {'✓ Can pick' if can_pick_sunday else '✗ Cannot pick'}")
    
    # Test Monday game (simulate game time)
    monday_game_time = deadlines.monday if deadlines.monday else datetime.now()
    can_pick_monday = deadline_manager.can_make_picks(current_week, current_year, monday_game_time)
    print(f"  Monday Night Game:   {'✓ Can pick' if can_pick_monday else '✗ Cannot pick'}")
    
    print("\n" + "=" * 50)
    print("Deadline System Test Complete!")
    
    return True

if __name__ == "__main__":
    try:
        test_deadline_system()
    except Exception as e:
        print(f"Error testing deadline system: {e}")
        sys.exit(1)
