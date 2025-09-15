#!/usr/bin/env python3
"""
Fix Week 1 tiebreaker in weekly_results table.
Only coyote should be the winner based on Monday Night tiebreaker logic.
"""

import sqlite3
import sys
from datetime import datetime

def fix_week1_tiebreaker(db_path):
    """Fix Week 1 weekly_results to show only coyote as winner based on Monday Night tiebreaker"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("=== FIXING WEEK 1 TIEBREAKER ===")
        
        # Get current Week 1 results
        cursor.execute('''
            SELECT wr.id, u.username, wr.correct_picks, wr.is_winner
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            WHERE wr.week = 1 AND wr.year = 2025
            ORDER BY u.username
        ''')
        current_results = cursor.fetchall()
        
        print("Current Week 1 results:")
        for result in current_results:
            print(f"  {result[1]}: {result[2]} correct picks, Winner: {result[3]}")
        
        # Find coyote's user_id
        cursor.execute('SELECT id FROM users WHERE username = ?', ('coyote',))
        coyote_user = cursor.fetchone()
        if not coyote_user:
            print("ERROR: Could not find user 'coyote'")
            return False
        
        coyote_user_id = coyote_user[0]
        
        # Update weekly_results: only coyote is winner
        print("\nApplying Monday Night tiebreaker fix...")
        
        # Set all Week 1 entries to NOT winner
        cursor.execute('''
            UPDATE weekly_results 
            SET is_winner = 0
            WHERE week = 1 AND year = 2025
        ''')
        
        # Set only coyote as winner
        cursor.execute('''
            UPDATE weekly_results 
            SET is_winner = 1
            WHERE week = 1 AND year = 2025 AND user_id = ?
        ''', (coyote_user_id,))
        
        # Verify the fix
        cursor.execute('''
            SELECT wr.id, u.username, wr.correct_picks, wr.is_winner
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            WHERE wr.week = 1 AND wr.year = 2025
            ORDER BY wr.is_winner DESC, u.username
        ''')
        updated_results = cursor.fetchall()
        
        print("\nFixed Week 1 results:")
        for result in updated_results:
            status = "WINNER" if result[3] else "Tied"
            print(f"  {result[1]}: {result[2]} correct picks, {status}")
        
        # Commit changes
        conn.commit()
        print("\n✅ Week 1 tiebreaker fixed successfully!")
        print("   Only coyote is now marked as Week 1 winner based on Monday Night tiebreaker")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error fixing Week 1 tiebreaker: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "nfl_fantasy.db"
    success = fix_week1_tiebreaker(db_path)
    sys.exit(0 if success else 1)
