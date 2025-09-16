#!/usr/bin/env python3
"""
Fix scoring for remote server - Rescore all final games where picks are marked as NULL
This script fixes the issue where the tiebreaker logic change broke automatic pick scoring.
"""
import sqlite3
import sys
from datetime import datetime

def fix_pick_scoring():
    """Fix pick scoring for all final games where picks are marked as NULL"""
    
    try:
        # Connect to database
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        print("🔍 Checking for NULL picks in final games...")
        
        # Find all picks for final games that are marked as NULL
        cursor.execute('''
            SELECT p.id, p.user_id, p.game_id, p.selected_team,
                   g.home_team, g.away_team, g.home_score, g.away_score,
                   g.is_final, u.username
            FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            JOIN users u ON p.user_id = u.id
            WHERE g.is_final = 1 AND p.is_correct IS NULL
            ORDER BY g.week, g.game_date, u.username
        ''')
        
        null_picks = cursor.fetchall()
        
        if not null_picks:
            print("✅ No NULL picks found for final games. Scoring is up to date.")
            conn.close()
            return
        
        print(f"⚠️  Found {len(null_picks)} NULL picks for final games that need rescoring")
        
        # Group by game for easier processing
        picks_by_game = {}
        for pick in null_picks:
            pick_id, user_id, game_id, selected_team, home_team, away_team, home_score, away_score, is_final, username = pick
            
            if game_id not in picks_by_game:
                picks_by_game[game_id] = {
                    'home_team': home_team,
                    'away_team': away_team, 
                    'home_score': home_score,
                    'away_score': away_score,
                    'picks': []
                }
            
            picks_by_game[game_id]['picks'].append({
                'pick_id': pick_id,
                'user_id': user_id,
                'username': username,
                'selected_team': selected_team
            })
        
        fixed_count = 0
        
        print("\n🔧 Rescoring picks...")
        
        for game_id, game_data in picks_by_game.items():
            home_team = game_data['home_team']
            away_team = game_data['away_team']
            home_score = game_data['home_score']
            away_score = game_data['away_score']
            
            # Determine winning team
            if home_score > away_score:
                winning_team = home_team
            elif away_score > home_score:
                winning_team = away_team
            else:
                # Tie - mark all as correct (rare in NFL)
                winning_team = None
            
            print(f"\n📊 Game {game_id}: {away_team} {away_score} - {home_score} {home_team}")
            if winning_team:
                print(f"   Winner: {winning_team}")
            else:
                print(f"   Result: TIE")
            
            # Update each pick for this game
            for pick in game_data['picks']:
                pick_id = pick['pick_id']
                username = pick['username'] 
                selected_team = pick['selected_team']
                
                if winning_team is None:
                    # Tie game - mark as correct
                    is_correct = 1
                    result_text = "CORRECT (TIE)"
                elif selected_team == winning_team:
                    is_correct = 1
                    result_text = "CORRECT"
                else:
                    is_correct = 0
                    result_text = "WRONG"
                
                # Update the pick
                cursor.execute('UPDATE user_picks SET is_correct = ? WHERE id = ?', (is_correct, pick_id))
                print(f"   - {username}: {selected_team} → {result_text}")
                fixed_count += 1
        
        # Commit all changes
        conn.commit()
        
        print(f"\n✅ Successfully rescored {fixed_count} picks")
        
        # Verify the fix by checking Kristian's Week 2 status
        print("\n🔍 Verifying fix - Kristian's Week 2 status:")
        cursor.execute('''
            SELECT 
                COUNT(*) as total_picks,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
                SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as wrong_picks,
                SUM(CASE WHEN is_correct IS NULL THEN 1 ELSE 0 END) as null_picks
            FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            JOIN users u ON p.user_id = u.id  
            WHERE u.username = 'kristian' AND g.week = 2 AND g.year = 2025
        ''')
        
        result = cursor.fetchone()
        if result:
            total, correct, wrong, null_picks = result
            print(f"   Total picks: {total}")
            print(f"   Correct: {correct}")
            print(f"   Wrong: {wrong}")
            print(f"   NULL: {null_picks}")
            
            if wrong == 3:
                print("✅ Kristian now has 3 wrong picks - fix successful!")
            else:
                print(f"⚠️  Kristian has {wrong} wrong picks (expected 3)")
        
        conn.close()
        
        print(f"\n🎉 Fix completed! {fixed_count} picks have been rescored.")
        print("The remote server should now show the correct scores.")
        
    except Exception as e:
        print(f"❌ Error fixing pick scoring: {e}")
        return False
    
    return True

def show_current_status():
    """Show current pick scoring status"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check for NULL picks in final games
        cursor.execute('''
            SELECT COUNT(*) FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            WHERE g.is_final = 1 AND p.is_correct IS NULL
        ''')
        null_count = cursor.fetchone()[0]
        
        # Check Kristian's Week 2 status
        cursor.execute('''
            SELECT 
                COUNT(*) as total_picks,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
                SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as wrong_picks,
                SUM(CASE WHEN is_correct IS NULL THEN 1 ELSE 0 END) as null_picks
            FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            JOIN users u ON p.user_id = u.id  
            WHERE u.username = 'kristian' AND g.week = 2 AND g.year = 2025
        ''')
        
        result = cursor.fetchone()
        
        print("📊 Current Database Status:")
        print(f"   NULL picks for final games: {null_count}")
        
        if result:
            total, correct, wrong, null_picks = result
            print(f"\n👤 Kristian's Week 2 Status:")
            print(f"   Total picks: {total}")
            print(f"   Correct: {correct}")
            print(f"   Wrong: {wrong}")
            print(f"   NULL: {null_picks}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")

if __name__ == '__main__':
    print("🏈 NFL Fantasy Pick Scoring Fix")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--status':
        show_current_status()
    else:
        print("This script will fix NULL pick scoring for final games.")
        print("Run with --status to check current database status.")
        print()
        
        # Show current status first
        show_current_status()
        
        print("\n🔧 Starting fix...")
        fix_pick_scoring()
