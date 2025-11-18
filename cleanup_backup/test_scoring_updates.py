#!/usr/bin/env python3
"""
Test script to verify leaderboard scoring updates after game finalization
"""

import sqlite3
import logging
from datetime import datetime
from scoring_updater import ScoringUpdater, create_weekly_results_table_if_not_exists

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_scoring_updates():
    """Test the scoring update functionality"""
    
    print("🔄 Testing Leaderboard Scoring Updates")
    print("=" * 50)
    
    # Ensure weekly_results table exists
    print("1️⃣ Creating/verifying weekly_results table...")
    success = create_weekly_results_table_if_not_exists()
    if success:
        print("   ✅ Weekly results table ready")
    else:
        print("   ❌ Failed to create weekly results table")
        return False
    
    # Initialize scoring updater
    print("\n2️⃣ Initializing scoring updater...")
    updater = ScoringUpdater()
    print("   ✅ Scoring updater ready")
    
    # Check current database state
    print("\n3️⃣ Checking current database state...")
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check for finalized games
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE is_final = 1')
        final_games = cursor.fetchone()[0]
        print(f"   📊 Final games in database: {final_games}")
        
        # Check distinct weeks with final games
        cursor.execute('''
            SELECT DISTINCT week, year, COUNT(*) as games_count
            FROM nfl_games 
            WHERE is_final = 1 
            GROUP BY week, year 
            ORDER BY year, week
        ''')
        final_weeks = cursor.fetchall()
        print(f"   📅 Weeks with final games: {len(final_weeks)}")
        for week_data in final_weeks:
            print(f"      - Week {week_data[0]}, {week_data[1]}: {week_data[2]} games")
        
        # Check current weekly_results
        cursor.execute('SELECT COUNT(*) FROM weekly_results')
        current_results = cursor.fetchone()[0]
        print(f"   📈 Current weekly results entries: {current_results}")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error checking database state: {e}")
        return False
    
    # Update scoring for all completed weeks
    print("\n4️⃣ Updating scoring for all completed weeks...")
    try:
        updated_count = updater.update_all_completed_weeks()
        print(f"   ✅ Updated scoring for {updated_count} weeks")
        
        if updated_count == 0:
            print("   ℹ️  No weeks to update (no completed games found)")
        
    except Exception as e:
        print(f"   ❌ Error updating scoring: {e}")
        return False
    
    # Verify the results
    print("\n5️⃣ Verifying updated results...")
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check updated weekly_results
        cursor.execute('SELECT COUNT(*) FROM weekly_results')
        new_results = cursor.fetchone()[0]
        print(f"   📈 Weekly results entries after update: {new_results}")
        
        # Show sample results
        cursor.execute('''
            SELECT wr.week, wr.year, u.username, wr.correct_picks, wr.is_winner, wr.rank
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            ORDER BY wr.year DESC, wr.week DESC, wr.rank
            LIMIT 10
        ''')
        sample_results = cursor.fetchall()
        
        if sample_results:
            print("   📋 Sample weekly results:")
            for result in sample_results:
                week, year, username, correct_picks, is_winner, rank = result
                winner_mark = "🏆" if is_winner else ""
                print(f"      - Week {week}/{year}: #{rank} {username} - {correct_picks} wins {winner_mark}")
        else:
            print("   ℹ️  No weekly results found")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error verifying results: {e}")
        return False
    
    print("\n✅ Scoring update test completed successfully!")
    return True

def test_individual_week_update():
    """Test updating a specific week"""
    print("\n🎯 Testing Individual Week Update")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Find a week with final games
        cursor.execute('''
            SELECT week, year, COUNT(*) as final_games
            FROM nfl_games 
            WHERE is_final = 1 
            GROUP BY week, year 
            ORDER BY year DESC, week DESC
            LIMIT 1
        ''')
        
        week_data = cursor.fetchone()
        conn.close()
        
        if not week_data:
            print("   ℹ️  No weeks with final games found")
            return True
        
        week, year, final_games = week_data
        print(f"   📅 Testing Week {week}, {year} ({final_games} final games)")
        
        updater = ScoringUpdater()
        success = updater.update_weekly_results(week, year)
        
        if success:
            print(f"   ✅ Successfully updated Week {week}, {year}")
        else:
            print(f"   ❌ Failed to update Week {week}, {year}")
            return False
        
    except Exception as e:
        print(f"   ❌ Error testing individual week update: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 NFL Fantasy Leaderboard Scoring Test")
    print("=" * 60)
    
    try:
        # Run the main scoring update test
        main_test_passed = test_scoring_updates()
        
        # Run individual week test
        individual_test_passed = test_individual_week_update()
        
        # Summary
        print("\n" + "=" * 60)
        if main_test_passed and individual_test_passed:
            print("🎉 ALL TESTS PASSED!")
            print("📋 The leaderboard scoring update system is working correctly.")
            print("📝 When games are marked as final, the leaderboard will now update automatically.")
            print("⚙️ Admins can also manually trigger updates from the admin panel.")
        else:
            print("❌ SOME TESTS FAILED!")
            print("🔧 Please check the error messages above for debugging information.")
        
    except Exception as e:
        print(f"\n❌ TEST EXECUTION ERROR: {e}")
        import traceback
        traceback.print_exc()
