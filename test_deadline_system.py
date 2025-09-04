#!/usr/bin/env python3
"""
Test script to verify the deadline system integration.
"""
from __future__ import annotations

import sys
import os
from datetime import datetime, timedelta

# Add the current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from deadline_manager import DeadlineManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure deadline_manager.py and utils/timezone_utils.py exist")
    sys.exit(1)

def test_deadline_system():
    """Test the deadline system functionality."""
    print("Testing Deadline System Integration")
    print("=" * 50)
    
    try:
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
        
        if not deadlines:
            print("  No deadline data available - this may be normal if no games are in database")
            return True
            
        for key, value in deadlines.items():
            if value and isinstance(value, dict):
                deadline = value.get('deadline')
                matchup = value.get('matchup', 'Unknown')
                if deadline:
                    print(f"  {key}: {deadline.strftime('%A, %B %d at %I:%M %p AST')} - {matchup}")
        
        # Test pick availability
        print(f"\nPick Availability Test:")
        can_pick = deadline_manager.can_make_picks(current_week, current_year)
        print(f"  Can make picks for week {current_week}: {'✓ Yes' if can_pick else '✗ No'}")
        
        print("\n" + "=" * 50)
        print("Deadline System Test Complete!")
        
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_deadline_system()
    sys.exit(0 if success else 1)
