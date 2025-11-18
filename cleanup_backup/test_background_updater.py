"""
Manual Background Updater Test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from background_updater import start_background_updater, get_updater_status
from api_rate_limiter import check_api_rate_limit

# Set up logging to see detailed output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_background_updater():
    """Test starting the background updater manually"""
    print("=== Manual Background Updater Test ===")
    
    try:
        # Check initial status
        print("Initial status:")
        status = get_updater_status()
        print(f"  Running: {status['running']}")
        print(f"  Current Week: {status['current_week']}")
        
        # Check API rate limit
        api_ok = check_api_rate_limit()
        print(f"  API Rate Limit OK: {api_ok}")
        
        # Try to start the updater
        print("\nStarting background updater...")
        start_background_updater()
        
        # Check status after starting
        print("\nStatus after starting:")
        status = get_updater_status()
        print(f"  Running: {status['running']}")
        
        if status['running']:
            print("✅ Background updater started successfully!")
        else:
            print("❌ Background updater failed to start")
            
        # Let it run for a bit and check the update process
        print("\nLet's also try a manual update to see if the logic works...")
        from database_sync import update_live_scores
        from datetime import datetime
        
        current_week = status['current_week']
        print(f"Attempting to update Week {current_week} scores...")
        
        updated_count = update_live_scores(current_week, 2025)
        print(f"Updated {updated_count} games")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_background_updater()
