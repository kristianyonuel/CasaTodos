#!/usr/bin/env python3
"""
Test Pick Correctness Fix
Diagnoses and fixes the leaderboard scoring issue where users show 0 points
"""

import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def diagnose_scoring_issue():
    """Diagnose why users are showing 0 points on leaderboard"""
    print("🔍 DIAGNOSING LEADERBOARD SCORING ISSUE")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check for final games
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE is_final = 1')
        final_games = cursor.fetchone()[0]
        print(f"📊 Final games in database: {final_games}")
        
        # Check for picks on final games
        cursor.execute('''
            SELECT COUNT(DISTINCT p.id) as total_picks, 
                   COUNT(DISTINCT p.user_id) as users_with_picks,
                   COUNT(CASE WHEN p.is_correct = 1 THEN 1 END) as correct_picks,
                   COUNT(CASE WHEN p.is_correct = 0 THEN 1 END) as incorrect_picks,
                   COUNT(CASE WHEN p.is_correct IS NULL THEN 1 END) as null_correctness
            FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            WHERE g.is_final = 1
        ''')
        
        pick_stats = cursor.fetchone()
        total_picks, users_with_picks, correct_picks, incorrect_picks, null_correctness = pick_stats
        
        print(f"📋 Picks on final games:")
        print(f"   • Total picks: {total_picks}")
        print(f"   • Users with picks: {users_with_picks}")
        print(f"   • Correct picks: {correct_picks}")
        print(f"   • Incorrect picks: {incorrect_picks}")
        print(f"   • NULL correctness: {null_correctness}")
        
        # Show specific examples
        print(f"\n🔍 Sample pick data:")
        cursor.execute('''
            SELECT u.username, p.selected_team, g.home_team, g.away_team, 
                   g.home_score, g.away_score, p.is_correct, g.week, g.year
            FROM user_picks p
            JOIN users u ON p.user_id = u.id
            JOIN nfl_games g ON p.game_id = g.id
            WHERE g.is_final = 1
            ORDER BY g.week, g.year, u.username
            LIMIT 10
        ''')
        
        sample_picks = cursor.fetchall()
        for pick in sample_picks:
            username, selected_team, home_team, away_team, home_score, away_score, is_correct, week, year = pick
            
            # Determine actual winner
            if home_score is not None and away_score is not None:
                if home_score > away_score:
                    actual_winner = home_team
                elif away_score > home_score:
                    actual_winner = away_team
                else:
                    actual_winner = "TIE"
            else:
                actual_winner = "NO_SCORE"
            
            should_be_correct = "YES" if selected_team == actual_winner else "NO"
            correctness_status = "✅" if is_correct == 1 else "❌" if is_correct == 0 else "❓"
            
            print(f"   {correctness_status} Week {week}: {username} picked {selected_team}")
            print(f"      Game: {away_team} @ {home_team} ({away_score}-{home_score})")
            print(f"      Winner: {actual_winner}, Should be correct: {should_be_correct}, DB says: {is_correct}")
        
        conn.close()
        
        # Analysis
        print(f"\n📋 ANALYSIS:")
        if null_correctness > 0:
            print(f"❌ ISSUE FOUND: {null_correctness} picks have NULL correctness")
            print("   The is_correct field is not being calculated when games are finalized.")
            print("   Solution: Run 'Fix Pick Correctness' in admin panel")
        elif correct_picks == 0 and incorrect_picks > 0:
            print(f"❌ ISSUE FOUND: All picks are marked incorrect ({incorrect_picks} picks)")
            print("   There may be a logic error in pick correctness calculation")
        elif total_picks == 0:
            print(f"ℹ️  No picks found on final games")
            print("   Users may not have made picks, or games may not be marked as final")
        else:
            print(f"✅ Pick correctness looks good")
            print(f"   {correct_picks} correct, {incorrect_picks} incorrect")
        
        return {
            'final_games': final_games,
            'total_picks': total_picks,
            'correct_picks': correct_picks,
            'null_correctness': null_correctness
        }
        
    except Exception as e:
        print(f"❌ Error diagnosing scoring issue: {e}")
        return None

def test_pick_correctness_fix():
    """Test the pick correctness fix function"""
    print("\n🔧 TESTING PICK CORRECTNESS FIX")
    print("=" * 60)
    
    try:
        from database_sync import recalculate_all_pick_correctness
        
        print("Running pick correctness recalculation...")
        picks_updated = recalculate_all_pick_correctness()
        print(f"✅ Updated correctness for {picks_updated} picks")
        
        return picks_updated
        
    except Exception as e:
        print(f"❌ Error testing pick correctness fix: {e}")
        return 0

def test_scoring_update():
    """Test the scoring update after fixing correctness"""
    print("\n📊 TESTING SCORING UPDATE")
    print("=" * 60)
    
    try:
        from scoring_updater import ScoringUpdater
        
        updater = ScoringUpdater()
        weeks_updated = updater.update_all_completed_weeks()
        print(f"✅ Updated scoring for {weeks_updated} weeks")
        
        return weeks_updated
        
    except Exception as e:
        print(f"❌ Error testing scoring update: {e}")
        return 0

def verify_fix():
    """Verify that the fix worked by re-diagnosing"""
    print("\n✅ VERIFYING FIX")
    print("=" * 60)
    
    # Re-run diagnosis
    results = diagnose_scoring_issue()
    
    if results:
        if results['null_correctness'] == 0 and results['correct_picks'] > 0:
            print("\n🎉 SUCCESS! Leaderboard should now show correct scores.")
        else:
            print("\n⚠️  Issue may still exist. Check the diagnosis above.")
    
    return results

def show_final_weekly_results():
    """Show sample weekly results to verify leaderboard will work"""
    print("\n📋 SAMPLE WEEKLY RESULTS")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check weekly_results table
        cursor.execute('''
            SELECT wr.week, wr.year, u.username, wr.correct_picks, wr.total_picks, wr.is_winner
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            ORDER BY wr.year DESC, wr.week DESC, wr.correct_picks DESC
            LIMIT 10
        ''')
        
        weekly_results = cursor.fetchall()
        
        if weekly_results:
            print("Recent weekly results:")
            for result in weekly_results:
                week, year, username, correct_picks, total_picks, is_winner = result
                winner_mark = "🏆" if is_winner else ""
                print(f"   Week {week}/{year}: {username} - {correct_picks}/{total_picks} {winner_mark}")
        else:
            print("No weekly results found. Run scoring update to populate.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error showing weekly results: {e}")

if __name__ == "__main__":
    print("🔧 NFL FANTASY LEADERBOARD SCORING FIX")
    print("=" * 60)
    print("This script will diagnose and fix the '0 points' issue on leaderboards")
    print()
    
    # Step 1: Diagnose the issue
    diagnosis = diagnose_scoring_issue()
    
    if diagnosis and (diagnosis['null_correctness'] > 0 or diagnosis['correct_picks'] == 0):
        print("\n🚨 ISSUE DETECTED - Attempting to fix...")
        
        # Step 2: Fix pick correctness
        picks_fixed = test_pick_correctness_fix()
        
        # Step 3: Update scoring
        weeks_updated = test_scoring_update()
        
        # Step 4: Verify the fix
        verify_fix()
        
        # Step 5: Show sample results
        show_final_weekly_results()
        
        print(f"\n🎉 REPAIR COMPLETE!")
        print(f"✅ Fixed {picks_fixed} picks")
        print(f"✅ Updated {weeks_updated} weeks")
        print(f"📊 Leaderboard should now show correct scores")
        
    else:
        print("\n✅ No issues detected or insufficient data for testing")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"1. Go to Admin Panel > 'Fix Pick Correctness' if more issues arise")
    print(f"2. Use 'Recalculate All Scoring' to refresh leaderboards")
    print(f"3. Check weekly leaderboard to verify scores display correctly")
    print(f"4. The system will auto-update when new games are finalized")
