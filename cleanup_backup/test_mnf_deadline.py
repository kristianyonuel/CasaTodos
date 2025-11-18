"""
Test MNF Deadline Logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deadline_manager import DeadlineManager
from datetime import datetime

def test_mnf_deadline_logic():
    """Test the Monday Night Football deadline logic"""
    print("=== MNF Deadline Logic Test ===")
    
    try:
        deadline_manager = DeadlineManager()
        
        # Test for current week
        current_week = 2
        current_year = 2025
        
        deadline_data = deadline_manager.get_week_deadlines(current_week, current_year)
        print(f"Deadline data for Week {current_week}: {deadline_data}")
        
        # Check Sunday deadline status
        sunday_data = deadline_data.get('sunday_games', {})
        if sunday_data and isinstance(sunday_data, dict):
            sunday_status = sunday_data.get('status', {})
            sunday_deadline_passed = sunday_status.get('is_closed', False)
            
            print(f"\nSunday Games:")
            print(f"  Deadline: {sunday_data.get('deadline', 'N/A')}")
            print(f"  Deadline Passed: {sunday_deadline_passed}")
            print(f"  Hours Until: {sunday_status.get('hours_until_deadline', 'N/A')}")
            
            # Test MNF logic
            print(f"\nMNF Score Predictions Should Be Shown: {sunday_deadline_passed}")
            
            if sunday_deadline_passed:
                print("✅ MNF score predictions will be shown (Sunday deadline passed)")
            else:
                print("🚫 MNF score predictions will be hidden (Sunday deadline not passed)")
        else:
            print("❌ Could not get Sunday deadline data")
            
    except Exception as e:
        print(f"Error testing MNF deadline logic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mnf_deadline_logic()
