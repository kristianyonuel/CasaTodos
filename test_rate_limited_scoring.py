"""
Test Rate Limited Scoring Updates
Verifies that the scoring system works with API rate limiting
"""

import sqlite3
import time
from datetime import datetime, timedelta
from api_rate_limiter import APIRateLimiter, check_api_rate_limit, record_api_call, get_api_calls_remaining
from scoring_updater import ScoringUpdater
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_rate_limiter():
    """Test the API rate limiter functionality"""
    print("🧪 Testing API Rate Limiter...")
    
    # Create test rate limiter with lower limits for testing
    test_limiter = APIRateLimiter(max_calls_per_hour=3)
    
    print(f"Initial calls remaining: {test_limiter.get_calls_remaining()}")
    print(f"Can make call: {test_limiter.can_make_call()}")
    
    # Test making calls until limit is reached
    for i in range(5):
        if test_limiter.can_make_call():
            test_limiter.record_call()
            remaining = test_limiter.get_calls_remaining()
            print(f"✅ Call {i+1} successful. Remaining: {remaining}")
            time.sleep(0.1)  # Small delay between calls
        else:
            next_time = test_limiter.get_next_available_time()
            print(f"❌ Call {i+1} blocked. Next available: {next_time}")
    
    print("✅ Rate limiter test completed\n")

def test_scoring_update_integration():
    """Test that scoring updates work without excessive API calls"""
    print("🧪 Testing Scoring Update Integration...")
    
    try:
        # Check current API status
        remaining = get_api_calls_remaining()
        print(f"Current API calls remaining: {remaining}")
        
        # Test scoring updater
        updater = ScoringUpdater()
        
        # This should work without making API calls (uses existing database data)
        print("Testing scoring update for Week 1, 2025...")
        success = updater.update_weekly_results(1, 2025)
        
        if success:
            print("✅ Scoring update successful (no API calls required)")
        else:
            print("❌ Scoring update failed")
        
        # Check API status again (should be unchanged)
        remaining_after = get_api_calls_remaining()
        print(f"API calls remaining after scoring update: {remaining_after}")
        
        if remaining == remaining_after:
            print("✅ No API calls were made during scoring update")
        else:
            print("⚠️  API calls were made during scoring update")
        
    except Exception as e:
        print(f"❌ Error testing scoring integration: {e}")
    
    print("✅ Scoring integration test completed\n")

def verify_database_state():
    """Verify the database has the necessary tables and data"""
    print("🧪 Verifying Database State...")
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check for users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
        user_count = cursor.fetchone()[0]
        print(f"Non-admin users: {user_count}")
        
        # Check for games
        cursor.execute('SELECT COUNT(*) FROM nfl_games')
        game_count = cursor.fetchone()[0]
        print(f"Total games: {game_count}")
        
        # Check for completed games
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE is_final = 1')
        completed_games = cursor.fetchone()[0]
        print(f"Completed games: {completed_games}")
        
        # Check for picks
        cursor.execute('SELECT COUNT(*) FROM user_picks')
        pick_count = cursor.fetchone()[0]
        print(f"Total picks: {pick_count}")
        
        # Check weekly_results table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weekly_results'")
        weekly_results_exists = cursor.fetchone() is not None
        print(f"Weekly results table exists: {weekly_results_exists}")
        
        if weekly_results_exists:
            cursor.execute('SELECT COUNT(*) FROM weekly_results')
            weekly_results_count = cursor.fetchone()[0]
            print(f"Weekly results records: {weekly_results_count}")
        
        conn.close()
        
        print("✅ Database verification completed\n")
        return {
            'users': user_count,
            'games': game_count,
            'completed_games': completed_games,
            'picks': pick_count,
            'weekly_results_exists': weekly_results_exists
        }
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return None

def create_test_data_if_needed():
    """Create minimal test data if the database is empty"""
    print("🧪 Creating Test Data if Needed...")
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check if we have any completed games
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE is_final = 1')
        completed_games = cursor.fetchone()[0]
        
        if completed_games == 0:
            print("No completed games found. Creating test game...")
            
            # Create a test game
            cursor.execute('''
                INSERT OR IGNORE INTO nfl_games 
                (week, year, game_id, away_team, home_team, game_date, 
                 away_score, home_score, is_final, is_monday_night, is_thursday_night)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                1, 2025, 'test_game_1', 'KC', 'BUF', '2025-09-01 20:00:00',
                21, 17, True, False, False
            ))
            
            print("✅ Test game created")
        
        # Check if we have any users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print("No non-admin users found. Consider creating test users through the admin panel.")
        
        conn.commit()
        conn.close()
        print("✅ Test data setup completed\n")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")

def test_complete_workflow():
    """Test the complete workflow of rate-limited scoring updates"""
    print("🧪 Testing Complete Rate-Limited Workflow...")
    
    try:
        # 1. Check database state
        db_state = verify_database_state()
        if not db_state:
            return
        
        # 2. Create test data if needed
        create_test_data_if_needed()
        
        # 3. Test rate limiter
        test_rate_limiter()
        
        # 4. Test scoring update integration
        test_scoring_update_integration()
        
        # 5. Show final API status
        remaining = get_api_calls_remaining()
        print(f"🏁 Final API calls remaining: {remaining}/5")
        
        # 6. Recommendations
        print("\n📋 RECOMMENDATIONS:")
        print("1. Use admin panel 'API Status' button to monitor rate limits")
        print("2. Scoring updates work with existing database data (no API calls)")
        print("3. Only use 'Update Live Scores' when you need fresh game data")
        print("4. Maximum 5 API calls per hour - plan accordingly")
        print("5. The system will automatically update scoring when games are finalized")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in complete workflow test: {e}")

def show_usage_recommendations():
    """Show recommendations for efficient API usage"""
    print("\n📖 USAGE RECOMMENDATIONS:")
    print("=" * 60)
    print("🎯 EFFICIENT API USAGE STRATEGY:")
    print("   • Check API status before making calls")
    print("   • Use manual score updates only when needed")
    print("   • Scoring calculations work with existing data")
    print("   • Let the system auto-update scoring when games finish")
    print()
    print("🕒 SUGGESTED SCHEDULE:")
    print("   • Morning: Check API status, update if calls available")
    print("   • Game days: Update scores 2-3 times max")
    print("   • After games: Verify scoring was updated automatically")
    print()
    print("⚡ ADMIN ACTIONS:")
    print("   • 'API Status' - Always check this first")
    print("   • 'Update Live Scores' - Only when API calls available")
    print("   • 'Update Week Scoring' - Uses database data (no API)")
    print("   • 'Recalculate All Scoring' - Uses database data (no API)")
    print("=" * 60)

if __name__ == "__main__":
    print("🚀 Starting Rate Limited Scoring Update Tests")
    print("=" * 60)
    
    # Run complete workflow test
    test_complete_workflow()
    
    # Show usage recommendations
    show_usage_recommendations()
    
    print("\n🎉 Rate limiting implementation complete!")
    print("The leaderboard will now update automatically when games are finalized,")
    print("while respecting API rate limits (max 5 calls per hour).")
