#!/usr/bin/env python3
"""
Fix pick correctness calculation for all completed games.

This script recalculates the is_correct field for all user picks
where games are completed but pick correctness is NULL or incorrect.
"""

import sqlite3
import sys
import os

def fix_pick_correctness(database_path='nfl_fantasy.db'):
    """Fix pick correctness for all completed games"""
    
    print(f"🔧 Fixing pick correctness in database: {database_path}")
    
    if not os.path.exists(database_path):
        print(f"❌ Database file not found: {database_path}")
        return False
    
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        print("📊 Analyzing completed games...")
        
        # Get all completed games
        cursor.execute('''
            SELECT id, away_team, home_team, away_score, home_score, week, year
            FROM nfl_games 
            WHERE is_final = 1
            ORDER BY year, week, game_date
        ''')
        completed_games = cursor.fetchall()
        
        print(f"Found {len(completed_games)} completed games")
        
        fixed_count = 0
        total_picks_updated = 0
        
        for game in completed_games:
            game_id, away_team, home_team, away_score, home_score, week, year = game
            
            # Determine winner
            if home_score > away_score:
                winner = home_team
            elif away_score > home_score:
                winner = away_team
            else:
                winner = None  # Tie (rare in NFL)
            
            if winner:
                # Check how many picks need fixing for this game
                cursor.execute('''
                    SELECT COUNT(*) FROM user_picks 
                    WHERE game_id = ? AND (is_correct IS NULL OR is_correct != CASE WHEN selected_team = ? THEN 1 ELSE 0 END)
                ''', (game_id, winner))
                
                picks_to_fix = cursor.fetchone()[0]
                
                if picks_to_fix > 0:
                    # Update pick correctness for this game
                    cursor.execute('''
                        UPDATE user_picks 
                        SET is_correct = CASE WHEN selected_team = ? THEN 1 ELSE 0 END
                        WHERE game_id = ?
                    ''', (winner, game_id))
                    
                    updated_picks = cursor.rowcount
                    total_picks_updated += updated_picks
                    fixed_count += 1
                    
                    print(f"✅ Fixed Week {week} {away_team}@{home_team}: {away_score}-{home_score} (winner: {winner}) - {updated_picks} picks updated")
        
        # Commit all changes
        conn.commit()
        
        print(f"\n🎉 Fix completed!")
        print(f"📊 Games processed: {fixed_count}")
        print(f"📊 Total pick correctness values updated: {total_picks_updated}")
        
        # Verify the fix with sample data
        print("\n🔍 Verification - Sample leaderboard data:")
        cursor.execute('''
            SELECT u.username,
                   COUNT(p.id) as total_picks,
                   SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
                   SUM(CASE WHEN p.is_correct IS NULL THEN 1 ELSE 0 END) as null_picks
            FROM users u
            JOIN user_picks p ON u.id = p.user_id
            JOIN nfl_games g ON p.game_id = g.id
            WHERE g.is_final = 1 AND u.is_admin = 0
            GROUP BY u.id, u.username
            HAVING total_picks > 0
            ORDER BY correct_picks DESC
            LIMIT 5
        ''')
        
        sample_results = cursor.fetchall()
        for user in sample_results:
            username, total, correct, null_picks = user
            win_pct = round((correct / total * 100) if total > 0 else 0, 1)
            print(f"  {username}: {correct}/{total} correct ({win_pct}%) - {null_picks} NULL values remaining")
        
        conn.close()
        
        if total_picks_updated > 0:
            print(f"\n✅ Success! Pick correctness has been fixed.")
            print(f"📱 Users should now see accurate scoring in leaderboards.")
        else:
            print(f"\n✅ No fixes needed - pick correctness is already accurate.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing pick correctness: {e}")
        return False

if __name__ == "__main__":
    # Allow custom database path as command line argument
    database_path = sys.argv[1] if len(sys.argv) > 1 else 'nfl_fantasy.db'
    
    print("🏈 NFL Fantasy Pick Correctness Fixer")
    print("=" * 50)
    
    success = fix_pick_correctness(database_path)
    
    if success:
        print("🎉 Fix completed successfully!")
        sys.exit(0)
    else:
        print("❌ Fix failed!")
        sys.exit(1)
