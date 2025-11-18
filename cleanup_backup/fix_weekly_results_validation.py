#!/usr/bin/env python3
"""
Fix weekly results validation to prevent calculating winners for incomplete weeks.

This script:
1. Removes any winners for incomplete weeks
2. Ensures only fully completed weeks (all games final) have winners
"""

import sqlite3
import sys
import os

def fix_weekly_results_validation(database_path='nfl_fantasy.db'):
    """Fix weekly results to only show winners for completed weeks"""
    
    print(f"🔧 Fixing weekly results validation in database: {database_path}")
    
    if not os.path.exists(database_path):
        print(f"❌ Database file not found: {database_path}")
        return False
    
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        print("📊 Analyzing weekly completion status...")
        
        # Find weeks with incomplete games that have winners
        cursor.execute('''
            SELECT DISTINCT wr.week, wr.year,
                   COUNT(DISTINCT CASE WHEN wr.is_winner = 1 THEN wr.user_id END) as current_winners,
                   (SELECT COUNT(*) FROM nfl_games WHERE week = wr.week AND year = wr.year) as total_games,
                   (SELECT COUNT(*) FROM nfl_games WHERE week = wr.week AND year = wr.year AND is_final = 1) as completed_games
            FROM weekly_results wr
            WHERE wr.is_winner = 1
            GROUP BY wr.week, wr.year
            ORDER BY wr.year, wr.week
        ''')
        
        weeks_with_winners = cursor.fetchall()
        
        incomplete_weeks_fixed = 0
        
        for week_data in weeks_with_winners:
            week, year, winners, total_games, completed_games = week_data
            
            if completed_games < total_games:
                # Week is incomplete but has winners - remove them
                print(f"🚫 Week {week}, {year}: {completed_games}/{total_games} games completed - removing {winners} premature winners")
                
                cursor.execute('''
                    DELETE FROM weekly_results 
                    WHERE week = ? AND year = ?
                ''', (week, year))
                
                incomplete_weeks_fixed += 1
            else:
                print(f"✅ Week {week}, {year}: {completed_games}/{total_games} games completed - {winners} winners valid")
        
        # Rebuild any missing results for completed weeks
        print("\n🔄 Rebuilding results for completed weeks...")
        
        cursor.execute('''
            SELECT DISTINCT week, year
            FROM nfl_games 
            WHERE is_final = 1
            GROUP BY week, year
            HAVING COUNT(*) = (
                SELECT COUNT(*) FROM nfl_games g2 
                WHERE g2.week = nfl_games.week AND g2.year = nfl_games.year
            )
            ORDER BY year, week
        ''')
        
        completed_weeks = cursor.fetchall()
        
        for week, year in completed_weeks:
            # Check if this week already has results
            cursor.execute('''
                SELECT COUNT(*) FROM weekly_results 
                WHERE week = ? AND year = ?
            ''', (week, year))
            
            existing_results = cursor.fetchone()[0]
            
            if existing_results == 0:
                print(f"🔧 Rebuilding results for completed Week {week}, {year}")
                
                # Calculate results for this completed week
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
                
                week_results = cursor.fetchall()
                
                if week_results:
                    top_score = week_results[0][3]  # Highest correct picks
                    
                    for result in week_results:
                        user_id, username, total, correct = result
                        is_winner = 1 if correct == top_score else 0
                        
                        cursor.execute('''
                            INSERT INTO weekly_results (user_id, week, year, correct_picks, total_picks, is_winner)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (user_id, week, year, correct, total, is_winner))
        
        # Commit all changes
        conn.commit()
        
        print(f"\n🎉 Validation fix completed!")
        print(f"📊 Weeks with premature winners fixed: {incomplete_weeks_fixed}")
        
        # Verify the fix with current standings
        print("\n🔍 Verification - Current season standings:")
        cursor.execute('''
            SELECT u.username, COUNT(*) as weekly_wins
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            WHERE wr.is_winner = 1
            GROUP BY u.id, u.username
            ORDER BY weekly_wins DESC, u.username
        ''')
        
        standings = cursor.fetchall()
        for standing in standings:
            username, wins = standing
            print(f"  {username}: {wins} weekly wins")
        
        # Show week completion status
        print("\n📋 Week completion status:")
        cursor.execute('''
            SELECT week, year,
                   COUNT(*) as total_games,
                   SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as completed_games,
                   (SELECT COUNT(*) FROM weekly_results wr WHERE wr.week = g.week AND wr.year = g.year AND wr.is_winner = 1) as winners
            FROM nfl_games g
            WHERE year = 2025
            GROUP BY week, year
            ORDER BY week
        ''')
        
        week_status = cursor.fetchall()
        for week_info in week_status:
            week, year, total, completed, winners = week_info
            status = "COMPLETE" if completed == total else f"INCOMPLETE ({completed}/{total})"
            print(f"  Week {week}: {status} - {winners} winners")
        
        conn.close()
        
        print(f"\n✅ Success! Weekly results validation has been fixed.")
        print(f"📱 Only completed weeks now show winners.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing weekly results validation: {e}")
        return False

if __name__ == "__main__":
    # Allow custom database path as command line argument
    database_path = sys.argv[1] if len(sys.argv) > 1 else 'nfl_fantasy.db'
    
    print("🏈 NFL Fantasy Weekly Results Validation Fixer")
    print("=" * 55)
    
    success = fix_weekly_results_validation(database_path)
    
    if success:
        print("🎉 Fix completed successfully!")
        sys.exit(0)
    else:
        print("❌ Fix failed!")
        sys.exit(1)
