#!/usr/bin/env python3
"""
Fix Weekly Winners in Database
==============================

The downloaded database from the server has incorrect is_winner flags
set by the automated scheduler. This script fixes them to match reality.

Corrections needed:
- Week 7: Remove ROBERT as winner, set RAYMOND as winner  
- Week 8: Remove KRISTIAN as winner (was a tie, no winner)

Created: October 28, 2025
"""

import sqlite3
from datetime import datetime

def fix_weekly_winners():
    print("🔧 Fixing Weekly Winners in Database")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🔍 Current incorrect weekly winners:")
    cursor.execute("""
        SELECT wr.week, u.username, wr.correct_picks, wr.total_picks
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.year = 2025 AND wr.is_winner = 1
        ORDER BY wr.week
    """)
    
    current_winners = cursor.fetchall()
    for week, username, correct, total in current_winners:
        print(f"  Week {week}: {username.upper()} ({correct}/{total})")
    
    print("\n🚨 Issues identified:")
    print("  - Week 7: ROBERT marked as winner (should be RAYMOND)")
    print("  - Week 8: KRISTIAN marked as winner (should be no winner - tie)")
    
    # Reset all is_winner flags first
    print("\n🧹 Clearing all is_winner flags...")
    cursor.execute("""
        UPDATE weekly_results 
        SET is_winner = 0 
        WHERE year = 2025
    """)
    
    # Set correct winners
    print("✅ Setting correct weekly winners...")
    
    # Week 1: COYOTE (13/16)
    cursor.execute("""
        UPDATE weekly_results 
        SET is_winner = 1 
        WHERE user_id = (SELECT id FROM users WHERE username = 'coyote') 
        AND week = 1 AND year = 2025
    """)
    print("  Week 1: COYOTE ✅")
    
    # Week 2: KRISTIAN (13/16) 
    cursor.execute("""
        UPDATE weekly_results 
        SET is_winner = 1 
        WHERE user_id = (SELECT id FROM users WHERE username = 'kristian') 
        AND week = 2 AND year = 2025
    """)
    print("  Week 2: KRISTIAN ✅")
    
    # Week 3: KRISTIAN (12/16)
    cursor.execute("""
        UPDATE weekly_results 
        SET is_winner = 1 
        WHERE user_id = (SELECT id FROM users WHERE username = 'kristian') 
        AND week = 3 AND year = 2025
    """)
    print("  Week 3: KRISTIAN ✅")
    
    # Week 4: ROBERT (12/16)
    cursor.execute("""
        UPDATE weekly_results 
        SET is_winner = 1 
        WHERE user_id = (SELECT id FROM users WHERE username = 'robert') 
        AND week = 4 AND year = 2025
    """)
    print("  Week 4: ROBERT ✅")
    
    # Week 5: VIZCA (10/14)
    cursor.execute("""
        UPDATE weekly_results 
        SET is_winner = 1 
        WHERE user_id = (SELECT id FROM users WHERE username = 'vizca') 
        AND week = 5 AND year = 2025
    """)
    print("  Week 5: VIZCA ✅")
    
    # Week 6: RAMFIS (11/15)
    cursor.execute("""
        UPDATE weekly_results 
        SET is_winner = 1 
        WHERE user_id = (SELECT id FROM users WHERE username = 'ramfis') 
        AND week = 6 AND year = 2025
    """)
    print("  Week 6: RAMFIS ✅")
    
    # Week 7: RAYMOND (12/14) - This was wrong on server
    cursor.execute("""
        UPDATE weekly_results 
        SET is_winner = 1 
        WHERE user_id = (SELECT id FROM users WHERE username = 'raymond') 
        AND week = 7 AND year = 2025
    """)
    print("  Week 7: RAYMOND ✅ (corrected from ROBERT)")
    
    # Week 8: NO WINNER (tie between KRISTIAN and RAMFIS at 10/13)
    print("  Week 8: NO WINNER ✅ (tie - KRISTIAN/RAMFIS both 10/13)")
    
    # Commit the changes
    conn.commit()
    
    print("\n🔍 Verifying fixes...")
    cursor.execute("""
        SELECT wr.week, u.username, wr.correct_picks, wr.total_picks
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.year = 2025 AND wr.is_winner = 1
        ORDER BY wr.week
    """)
    
    fixed_winners = cursor.fetchall()
    print("✅ Corrected weekly winners:")
    winner_counts = {}
    for week, username, correct, total in fixed_winners:
        print(f"  Week {week}: {username.upper()} ({correct}/{total})")
        winner_counts[username.upper()] = winner_counts.get(username.upper(), 0) + 1
    
    print(f"\n📈 Corrected season standings:")
    for username, wins in sorted(winner_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {username}: {wins} wins")
    
    # Update user_statistics table to match
    print(f"\n🔄 Updating user_statistics table...")
    for username in ['kristian', 'robert', 'ramfis', 'coyote', 'vizca', 'raymond']:
        actual_wins = winner_counts.get(username.upper(), 0)
        cursor.execute("""
            UPDATE user_statistics 
            SET total_wins = ?, updated_at = datetime('now')
            WHERE user_id = (SELECT id FROM users WHERE username = ?)
        """, (actual_wins, username))
        print(f"  {username.upper()}: {actual_wins} wins")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 DATABASE FIXED!")
    print("=" * 50)
    print("✅ Correct season standings now:")
    print("   🏆 KRISTIAN: 2 wins (Weeks 2, 3)")
    print("   🥈 ROBERT: 1 win (Week 4)")  
    print("   🥉 RAMFIS: 1 win (Week 6)")
    print("   🎯 COYOTE: 1 win (Week 1)")
    print("   ⭐ VIZCA: 1 win (Week 5)")
    print("   🎪 RAYMOND: 1 win (Week 7)")
    print()
    print("🔄 Your leaderboard should now show correct data!")
    print("   (Restart app and refresh browser if needed)")

if __name__ == "__main__":
    fix_weekly_winners()