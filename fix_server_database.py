#!/usr/bin/env python3
"""
Server Database Fix Script
Run this on Ubuntu server to apply the same fixes without code changes
"""

import sqlite3
import sys
import os

def fix_server_database():
    """Apply all database fixes to server"""
    
    # Check if database exists
    if not os.path.exists('nfl_fantasy.db'):
        print("❌ Database 'nfl_fantasy.db' not found in current directory")
        print("Make sure you're in the correct directory with the database file")
        return False
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        print("=== APPLYING SERVER DATABASE FIXES ===")
        
        # Fix 1: Update game times (13:00 UTC → 17:00 UTC for Sunday games)
        print("\n1. Fixing game times...")
        
        cursor.execute("""
            UPDATE nfl_games 
            SET game_time = '17:00:00'
            WHERE game_date = '2025-09-21' 
            AND game_time = '13:00:00'
        """)
        
        game_time_fixes = cursor.rowcount
        print(f"   Updated {game_time_fixes} Sunday games from 13:00 to 17:00 UTC")
        
        # Fix 2: Clear premature Week 3 winners
        print("\n2. Clearing premature Week 3 winners...")
        
        # Check current Week 3 winners
        cursor.execute("""
            SELECT u.username 
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            WHERE wr.week = 3 AND wr.year = 2025 AND wr.is_winner = 1
        """)
        
        current_winners = [row[0] for row in cursor.fetchall()]
        if current_winners:
            print(f"   Found premature winners: {current_winners}")
            
            # Clear the premature winners
            cursor.execute("""
                UPDATE weekly_results 
                SET is_winner = 0 
                WHERE week = 3 AND year = 2025 AND is_winner = 1
            """)
            
            cleared_winners = cursor.rowcount
            print(f"   Cleared winner status for {cleared_winners} users in Week 3")
        else:
            print("   No premature winners found - already fixed")
        
        # Commit all changes
        conn.commit()
        
        # Verification
        print("\n=== VERIFICATION ===")
        
        # Check Sunday game times
        cursor.execute("""
            SELECT COUNT(*) 
            FROM nfl_games 
            WHERE game_date = '2025-09-21' AND game_time = '17:00:00'
        """)
        correct_times = cursor.fetchone()[0]
        print(f"✅ Sunday games with correct 17:00 UTC time: {correct_times}")
        
        # Check Week 3 winners
        cursor.execute("""
            SELECT COUNT(*) 
            FROM weekly_results 
            WHERE week = 3 AND year = 2025 AND is_winner = 1
        """)
        week3_winners = cursor.fetchone()[0]
        print(f"✅ Week 3 premature winners: {week3_winners} (should be 0)")
        
        # Show current legitimate winners
        cursor.execute("""
            SELECT u.username, wr.week
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            WHERE wr.is_winner = 1 AND wr.year = 2025
            ORDER BY wr.week
        """)
        
        legitimate_winners = cursor.fetchall()
        print(f"✅ Legitimate weekly winners:")
        for username, week in legitimate_winners:
            print(f"   Week {week}: {username}")
        
        conn.close()
        
        print(f"\n🎉 All database fixes applied successfully!")
        print(f"   - Game times corrected")
        print(f"   - Premature winners cleared")
        print(f"   - Server ready to display correct times and leaderboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        return False

if __name__ == "__main__":
    print("Server Database Fix Script")
    print("=" * 40)
    
    if fix_server_database():
        print("\n✅ SUCCESS: Database fixes completed")
        print("Your server will now show:")
        print("  - Sunday games at 1:00 PM AST (not 9:00 AM)")
        print("  - Correct deadline status for past games")
        print("  - Only legitimate winners in season leaderboard")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Database fixes incomplete")
        sys.exit(1)
