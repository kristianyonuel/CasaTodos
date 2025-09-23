#!/usr/bin/env python3
"""
Server fix for timezone display issue
Fixes Sunday 1pm AST games that were showing as 9am AST
"""

import sqlite3
import sys
import os

def fix_game_times():
    """Fix game times from 13:00 UTC to 17:00 UTC for proper AST display"""
    
    db_path = 'nfl_fantasy.db'
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Finding games with incorrect timezone...")
        
        # Find all Sunday 1pm games that are stored as 13:00 UTC
        cursor.execute('''
            SELECT COUNT(*)
            FROM nfl_games 
            WHERE game_date LIKE '%13:00:00'
            AND year = 2025
        ''')
        
        games_to_fix = cursor.fetchone()[0]
        print(f"Found {games_to_fix} games showing 9am AST that should show 1pm AST")
        
        if games_to_fix == 0:
            print("✅ No games need fixing - timezone display is already correct!")
            conn.close()
            return True
        
        print("🔧 Fixing game times...")
        
        # Update all 13:00:00 games to 17:00:00 
        # This changes UTC storage so they display as 1pm AST instead of 9am AST
        cursor.execute('''
            UPDATE nfl_games 
            SET game_date = REPLACE(game_date, '13:00:00', '17:00:00')
            WHERE game_date LIKE '%13:00:00'
            AND year = 2025
        ''')
        
        updated_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"✅ Successfully fixed {updated_count} games")
        print("✅ Sunday 1pm games will now display as '1:00 PM AST' instead of '9:00 AM AST'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing game times: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("CASA TODOS - TIMEZONE DISPLAY FIX")
    print("=" * 50)
    print()
    
    success = fix_game_times()
    
    if success:
        print()
        print("🎉 TIMEZONE FIX COMPLETED SUCCESSFULLY!")
        print("The app should now show correct game times:")
        print("• Sunday 1pm games: '1:00 PM AST' ✅")
        print("• No more '9:00 AM AST' for afternoon games ✅")
        sys.exit(0)
    else:
        print()
        print("❌ TIMEZONE FIX FAILED")
        print("Please check the error messages above and try again.")
        sys.exit(1)
