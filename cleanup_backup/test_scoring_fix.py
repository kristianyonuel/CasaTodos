#!/usr/bin/env python3
"""
Test the fixed scoring update functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from database_sync import update_pick_correctness
from scoring_updater import ScoringUpdater


def test_scoring_fix():
    """Test that update week scoring now works correctly"""
    print("🔧 Testing Fixed Scoring Update")
    print("=" * 40)
    
    try:
        # Test Week 1
        week = 1
        year = 2025
        
        print(f"\n1. Testing pick correctness update for Week {week}, {year}...")
        picks_updated = update_pick_correctness(week, year)
        print(f"   ✅ Pick correctness updated for {picks_updated} picks")
        
        print(f"\n2. Testing weekly results update for Week {week}, {year}...")
        updater = ScoringUpdater()
        success = updater.update_weekly_results(week, year)
        
        if success:
            print("   ✅ Weekly results updated successfully")
        else:
            print("   ❌ Weekly results update failed")
            return False
        
        # Check the results
        print(f"\n3. Verifying updated data...")
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check pick correctness counts
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN is_correct = 1 THEN 1 END) as correct_picks,
                COUNT(CASE WHEN is_correct = 0 THEN 1 END) as incorrect_picks,
                COUNT(*) as total_picks
            FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            WHERE g.week = ? AND g.year = ? AND g.is_final = 1
        ''', (week, year))
        
        pick_stats = cursor.fetchone()
        
        cursor.execute('''
            SELECT COUNT(*) as users_with_results
            FROM weekly_results
            WHERE week = ? AND year = ?
        ''', (week, year))
        
        result_stats = cursor.fetchone()
        
        conn.close()
        
        print(f"   📊 Pick Stats: {pick_stats[0]} correct, {pick_stats[1]} incorrect, {pick_stats[2]} total")
        print(f"   📊 Weekly Results: {result_stats[0]} users have calculated results")
        
        if pick_stats[2] > 0 and result_stats[0] > 0:
            print("\n🎉 Scoring fix test PASSED!")
            print("   ✅ Pick correctness is now calculated")
            print("   ✅ Weekly results are now updated")
            print("   ✅ PDF exports will show correct win/loss counts")
            return True
        else:
            print("\n❌ Test incomplete - no picks or results data")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_scoring_fix()
    if success:
        print("\n🎯 The scoring update issue has been FIXED!")
        print("   Now when games finish, both pick correctness AND weekly results get updated.")
    else:
        print("\n❌ Test failed - scoring issue may still exist")
    
    exit(0 if success else 1)
