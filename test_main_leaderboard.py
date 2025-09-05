#!/usr/bin/env python3
"""
Test Main Leaderboard Fix
Verifies that the season/main leaderboard shows correct data
"""

import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_main_leaderboard_query():
    """Test the main leaderboard query directly"""
    print("🏆 TESTING MAIN LEADERBOARD QUERY")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Test the new leaderboard query
        cursor.execute('''
            SELECT u.username,
                   COUNT(DISTINCT CASE WHEN wr.is_winner = 1 THEN wr.week || '-' || wr.year END) as weekly_wins,
                   SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as total_games_won,
                   COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week || '-' || g.year END) as weeks_played,
                   COUNT(CASE WHEN g.is_final = 1 THEN 1 END) as total_games_played,
                   ROUND(
                       CASE 
                           WHEN COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week || '-' || g.year END) > 0
                           THEN CAST(SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / 
                                COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week || '-' || g.year END)
                           ELSE 0 
                       END, 1
                   ) as avg_games_won_per_week
            FROM users u
            LEFT JOIN user_picks p ON u.id = p.user_id
            LEFT JOIN nfl_games g ON p.game_id = g.id
            LEFT JOIN weekly_results wr ON u.id = wr.user_id
            WHERE u.is_admin = 0
            GROUP BY u.id, u.username
            HAVING COUNT(CASE WHEN g.is_final = 1 THEN 1 END) > 0 OR COUNT(CASE WHEN wr.is_winner = 1 THEN 1 END) > 0
            ORDER BY weekly_wins DESC, total_games_won DESC, avg_games_won_per_week DESC, u.username
        ''')
        
        leaderboard_results = cursor.fetchall()
        
        print(f"📊 Main leaderboard results: {len(leaderboard_results)} players")
        
        if leaderboard_results:
            print("🏆 Season Leaderboard:")
            print("Rank | Player | Weekly Wins | Total Games Won | Weeks Played | Avg Per Week")
            print("-" * 75)
            
            for i, result in enumerate(leaderboard_results, 1):
                username, weekly_wins, total_games_won, weeks_played, total_games, avg_per_week = result
                print(f"{i:4} | {username:15} | {weekly_wins:11} | {total_games_won:15} | {weeks_played:12} | {avg_per_week:11}")
        else:
            print("❌ No results found")
            
            # Diagnostic queries
            print("\n🔍 DIAGNOSTIC INFO:")
            
            # Check users
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
            user_count = cursor.fetchone()[0]
            print(f"Non-admin users: {user_count}")
            
            # Check picks with correctness
            cursor.execute('''
                SELECT COUNT(*) as total_picks,
                       COUNT(CASE WHEN p.is_correct = 1 THEN 1 END) as correct_picks,
                       COUNT(CASE WHEN p.is_correct = 0 THEN 1 END) as incorrect_picks,
                       COUNT(CASE WHEN p.is_correct IS NULL THEN 1 END) as null_picks
                FROM user_picks p
                JOIN nfl_games g ON p.game_id = g.id
                WHERE g.is_final = 1
            ''')
            pick_stats = cursor.fetchone()
            print(f"Picks on final games: {pick_stats[0]} total, {pick_stats[1]} correct, {pick_stats[2]} incorrect, {pick_stats[3]} null")
            
            # Check weekly results
            cursor.execute('SELECT COUNT(*) FROM weekly_results')
            weekly_results_count = cursor.fetchone()[0]
            print(f"Weekly results records: {weekly_results_count}")
        
        conn.close()
        return leaderboard_results
        
    except Exception as e:
        print(f"❌ Error testing leaderboard query: {e}")
        return None

def compare_weekly_vs_main_leaderboard():
    """Compare the weekly leaderboard logic vs main leaderboard logic"""
    print("\n📊 COMPARING WEEKLY VS MAIN LEADERBOARD")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Test for a specific week (if available)
        cursor.execute('''
            SELECT DISTINCT week, year 
            FROM nfl_games 
            WHERE is_final = 1
            ORDER BY year DESC, week DESC
            LIMIT 1
        ''')
        
        week_data = cursor.fetchone()
        if not week_data:
            print("No completed weeks found for comparison")
            conn.close()
            return
        
        week, year = week_data
        print(f"Testing with Week {week}, {year}")
        
        # Weekly leaderboard query (like in app.py)
        cursor.execute('''
            SELECT u.id, u.username,
                   COUNT(p.id) as total_picks,
                   SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks
            FROM users u
            JOIN user_picks p ON u.id = p.user_id
            JOIN nfl_games g ON p.game_id = g.id
            WHERE g.week = ? AND g.year = ? AND g.is_final = 1 AND u.is_admin = 0
            GROUP BY u.id, u.username
            HAVING total_picks > 0
            ORDER BY correct_picks DESC, u.username
        ''', (week, year))
        
        weekly_results = cursor.fetchall()
        
        print(f"\n📋 Weekly leaderboard for Week {week}:")
        for result in weekly_results:
            user_id, username, total_picks, correct_picks = result
            print(f"   {username}: {correct_picks}/{total_picks} correct")
        
        # Check if these users show up in main leaderboard
        print(f"\n🔍 Checking if these users appear in main leaderboard...")
        user_ids = [str(r[0]) for r in weekly_results]
        if user_ids:
            placeholders = ','.join('?' * len(user_ids))
            cursor.execute(f'''
                SELECT u.username,
                       SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as total_games_won
                FROM users u
                LEFT JOIN user_picks p ON u.id = p.user_id
                LEFT JOIN nfl_games g ON p.game_id = g.id
                WHERE u.id IN ({placeholders}) AND g.is_final = 1
                GROUP BY u.id, u.username
                ORDER BY total_games_won DESC
            ''', user_ids)
            
            main_results = cursor.fetchall()
            print(f"📊 Same users in main leaderboard logic:")
            for result in main_results:
                username, total_games_won = result
                print(f"   {username}: {total_games_won} total games won")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error comparing leaderboards: {e}")

def verify_fix_needed():
    """Check if we need to run the pick correctness fix"""
    print("\n🔧 CHECKING IF PICK CORRECTNESS FIX IS NEEDED")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check for picks with null correctness on final games
        cursor.execute('''
            SELECT COUNT(*) as null_correctness,
                   COUNT(CASE WHEN p.is_correct = 1 THEN 1 END) as correct_picks,
                   COUNT(CASE WHEN p.is_correct = 0 THEN 1 END) as incorrect_picks
            FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            WHERE g.is_final = 1 AND p.is_correct IS NULL
        ''')
        
        result = cursor.fetchone()
        null_count, correct_count, incorrect_count = result
        
        if null_count > 0:
            print(f"❌ Found {null_count} picks with NULL correctness on final games")
            print("   → Run 'Fix Pick Correctness' in admin panel")
            return True
        else:
            print(f"✅ No NULL correctness found")
            print(f"   Correct picks: {correct_count}, Incorrect picks: {incorrect_count}")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking pick correctness: {e}")
        return False

if __name__ == "__main__":
    print("🧪 MAIN LEADERBOARD DIAGNOSIS AND TEST")
    print("=" * 60)
    
    # Step 1: Check if pick correctness fix is needed
    needs_fix = verify_fix_needed()
    
    if needs_fix:
        print("\n🚨 PICK CORRECTNESS FIX REQUIRED!")
        print("Go to Admin Panel → 'Fix Pick Correctness' → 'Recalculate All Scoring'")
    
    # Step 2: Test main leaderboard query
    results = test_main_leaderboard_query()
    
    # Step 3: Compare with weekly leaderboard logic
    compare_weekly_vs_main_leaderboard()
    
    # Summary
    print("\n" + "=" * 60)
    if results:
        print("✅ Main leaderboard should now show data!")
        print("The season leaderboard has been fixed to calculate directly from picks.")
    else:
        print("❌ Main leaderboard still shows no data")
        if needs_fix:
            print("→ Run the pick correctness fix in admin panel first")
        else:
            print("→ Check that users have made picks on completed games")
    
    print("\n📋 NEXT STEPS:")
    print("1. Go to Admin Panel")
    print("2. Click 'Fix Pick Correctness' (if needed)")
    print("3. Click 'Recalculate All Scoring'")
    print("4. Check both weekly and main leaderboards")
    print("5. Main leaderboard should show: Weekly Wins | Total Games Won | Avg Per Week")
