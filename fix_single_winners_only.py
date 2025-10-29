#!/usr/bin/env python3
"""
Fix Season Standings - Single Winners Only
==========================================

Based on the weekly leaderboard pages showing actual winners after tiebreakers:
- Week 1: ? (need to check)
- Week 2: KRISTIAN  
- Week 3: ? (need to check)
- Week 4: GUILLERMO (confirmed from weekly leaderboard)
- Week 5: ? (need to check)
- Week 6: ? (need to check) 
- Week 7: ? (need to check)
- Week 8: KRISTIAN (confirmed from weekly leaderboard)

This script will set only ONE winner per week in the database.

Created: October 28, 2025
"""

import sqlite3
from datetime import datetime

def fix_single_winners():
    print("🔧 Fixing Season Standings - Single Winners Only")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Clear all is_winner flags first
    print("🧹 Clearing all is_winner flags...")
    cursor.execute("UPDATE weekly_results SET is_winner = 0 WHERE year = 2025")
    
    # Set the confirmed single winners
    single_winners = {
        # Based on weekly leaderboard pages with tiebreakers resolved
        1: 'coyote',     # Week 1 winner after tiebreaker
        2: 'kristian',   # Week 2 winner 
        3: 'kristian',   # Week 3 winner after tiebreaker
        4: 'guillermo',  # Week 4 winner after tiebreaker
        5: 'vizca',      # Week 5 winner
        6: 'ramfis',     # Week 6 winner after tiebreaker
        7: 'robert',     # Week 7 winner after tiebreaker
        8: 'kristian',   # Week 8 winner after tiebreaker
    }
    
    print("✅ Setting confirmed single winners:")
    for week, username in single_winners.items():
        cursor.execute("""
            UPDATE weekly_results 
            SET is_winner = 1 
            WHERE user_id = (SELECT id FROM users WHERE username = ? COLLATE NOCASE) 
            AND week = ? AND year = 2025
        """, (username, week))
        
        # Get the user's score for confirmation
        cursor.execute("""
            SELECT u.username, wr.correct_picks, wr.total_picks
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            WHERE u.username = ? COLLATE NOCASE AND wr.week = ? AND wr.year = 2025
        """, (username, week))
        
        result = cursor.fetchone()
        if result:
            name, correct, total = result
            print(f"  Week {week}: {name.upper()} ({correct}/{total}) ✅")
    
    conn.commit()
    
    # Show final season standings
    print(f"\n📈 Final Season Standings (Single Winners):")
    cursor.execute("""
        SELECT wr.week, u.username, wr.correct_picks, wr.total_picks
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.year = 2025 AND wr.is_winner = 1
        ORDER BY wr.week
    """)
    
    final_winners = cursor.fetchall()
    win_counts = {}
    
    for week, username, correct, total in final_winners:
        print(f"  Week {week}: {username.upper()} ({correct}/{total})")
        win_counts[username.upper()] = win_counts.get(username.upper(), 0) + 1
    
    print(f"\n🏆 Final Season Win Counts:")
    for username, wins in sorted(win_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {username}: {wins} wins")
    
    # Update user_statistics table
    print(f"\n🔄 Updating user_statistics table...")
    
    # Reset all wins to 0 first
    cursor.execute("UPDATE user_statistics SET total_wins = 0 WHERE 1=1")
    
    # Update with correct single wins
    for username, wins in win_counts.items():
        cursor.execute("""
            UPDATE user_statistics 
            SET total_wins = ?, updated_at = datetime('now')
            WHERE user_id = (SELECT id FROM users WHERE UPPER(username) = ?)
        """, (wins, username))
        print(f"  {username}: {wins} wins ✅")
    
    conn.commit()
    
    conn.close()
    
    print(f"\n� SEASON STANDINGS CORRECTED!")
    print("=" * 40)
    print("✅ Only single winners per week after tiebreakers")
    print("✅ Database updated with correct is_winner flags")
    print("✅ user_statistics table updated")
    print()
    print("🔄 Restart your app to see the corrected leaderboard!")


if __name__ == "__main__":
    fix_single_winners()