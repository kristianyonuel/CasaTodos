"""
Check Background Updater Status
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from background_updater import get_updater_status
import logging

# Set up logging to see detailed output
logging.basicConfig(level=logging.DEBUG)

def check_updater_status():
    """Check the current status of the background updater"""
    print("=== Background Updater Status Check ===")
    
    try:
        status = get_updater_status()
        print(f"Status: {status}")
        
        print(f"Running: {status['running']}")
        print(f"Update Interval: {status['update_interval_minutes']} minutes")
        print(f"Current Week: {status['current_week']}")
        print(f"Next Update In: {status['next_update_in_seconds']} seconds")
        
        # Also check if we're in a game day
        from datetime import datetime
        current_day = datetime.now().weekday()  # 0=Monday, 1=Tuesday, ..., 6=Sunday
        game_days = [3, 6, 0, 1]  # Thursday, Sunday, Monday, Tuesday
        
        print(f"\nCurrent Day: {current_day} ({'Monday' if current_day == 0 else 'Tuesday' if current_day == 1 else 'Wednesday' if current_day == 2 else 'Thursday' if current_day == 3 else 'Friday' if current_day == 4 else 'Saturday' if current_day == 5 else 'Sunday'})")
        print(f"Is Game Day: {current_day in game_days}")
        
        # Check API rate limit status
        from api_rate_limiter import check_api_rate_limit, get_rate_limit_status
        api_ok = check_api_rate_limit()
        rate_status = get_rate_limit_status()
        
        print(f"\nAPI Rate Limit OK: {api_ok}")
        print(f"Rate Limit Status: {rate_status}")
        
    except Exception as e:
        print(f"Error checking updater status: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_updater_status()
