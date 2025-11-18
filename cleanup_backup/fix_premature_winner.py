#!/usr/bin/env python3
"""Fix premature weekly winner declaration"""

import sqlite3

def fix_premature_winner():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🔧 FIXING PREMATURE WEEKLY WINNER...")
    
    # Remove weekly winner status for incomplete Week 1
    cursor.execute('''
        UPDATE weekly_results 
        SET is_winner = FALSE 
        WHERE week = 1 AND year = 2025
    ''')
    
    updated_count = cursor.rowcount
    print(f"Updated {updated_count} weekly_results records")
    
    conn.commit()
    
    # Verify the fix
    cursor.execute('''
        SELECT COUNT(*) as winners 
        FROM weekly_results 
        WHERE week = 1 AND year = 2025 AND is_winner = TRUE
    ''')
    
    winners_count = cursor.fetchone()[0]
    print(f"Weekly winners for Week 1: {winners_count} (should be 0)")
    
    if winners_count == 0:
        print("✅ Fix successful: No premature weekly winners")
    else:
        print("❌ Fix failed: Still has weekly winners")
    
    conn.close()

if __name__ == "__main__":
    fix_premature_winner()
