#!/usr/bin/env python3
"""
Test the sync season safety mechanism
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from database_sync import sync_season_from_api


def test_sync_safety():
    """Test that sync is blocked when picks exist"""
    print("🔒 Testing Sync Season Safety Mechanism")
    print("=" * 45)
    
    try:
        # Check current state
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM user_picks up 
            JOIN nfl_games g ON up.game_id = g.id 
            WHERE g.year = 2025
        ''')
        existing_picks = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE year = 2025')
        existing_games = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📊 Current state:")
        print(f"   Games for 2025: {existing_games}")
        print(f"   User picks for 2025: {existing_picks}")
        
        # Test sync behavior
        print(f"\n🧪 Testing sync_season_from_api(2025)...")
        result = sync_season_from_api(2025)
        
        if existing_picks > 0:
            if result == 0:
                print("✅ SAFETY TEST PASSED!")
                print("   Sync was correctly BLOCKED due to existing picks")
                print("   User data is PROTECTED from deletion")
                return True
            else:
                print("❌ SAFETY TEST FAILED!")
                print("   Sync proceeded despite existing picks - DATA LOSS RISK!")
                return False
        else:
            print(f"ℹ️  No existing picks found, sync returned: {result}")
            if result > 0:
                print("✅ Sync completed successfully (no picks to protect)")
                return True
            else:
                print("❌ Sync failed (API issue)")
                return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_sync_safety()
    if success:
        print("\n🛡️  Sync Season safety mechanism is working!")
        print("   User picks are protected from accidental deletion.")
    else:
        print("\n⚠️  Sync Season safety mechanism may have issues!")
    
    exit(0 if success else 1)
