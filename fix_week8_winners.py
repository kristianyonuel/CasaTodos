#!/usr/bin/env python3
"""
Fix Week 8 Winners - Set Both KRISTIAN and RAMFIS as Winners
==========================================================

Week 8 is final with all 13 games completed.
KRISTIAN and RAMFIS are tied for first place with 11/13 correct picks.
Both should be marked as winners.

This gives:
- KRISTIAN: 3 total wins (Weeks 2, 3, 8)
- RAMFIS: 2 total wins (Weeks 6, 8)

Created: October 28, 2025
"""

import sqlite3
from datetime import datetime

def fix_week8_winners():
    print("🔧 Fixing Week 8 Winners - Setting Tie Winners")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check Week 8 current status
    cursor.execute("""
        SELECT u.username, wr.correct_picks, wr.total_picks, wr.is_winner
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.week = 8 AND wr.year = 2025
        ORDER BY wr.correct_picks DESC, u.username
    """)
    
    week8_results = cursor.fetchall()
    print("🔍 Week 8 Current Results:")
    max_correct = 0
    winners = []
    
    for username, correct, total, is_winner in week8_results:
        status = " 👑 WINNER" if is_winner else ""
        print(f"  {username.upper()}: {correct}/{total}{status}")
        if correct > max_correct:
            max_correct = correct
        if is_winner:
            winners.append(username.upper())
    
    print(f"\nAnalysis:")
    print(f"  Maximum correct picks: {max_correct}")
    print(f"  Current winners: {winners}")
    
    # Find who should be winners (those with max_correct)
    should_be_winners = []
    for username, correct, total, is_winner in week8_results:
        if correct == max_correct:
            should_be_winners.append(username.upper())
    
    print(f"  Should be winners: {should_be_winners}")
    
    # Clear Week 8 winners first
    cursor.execute("""
        UPDATE weekly_results 
        SET is_winner = 0 
        WHERE week = 8 AND year = 2025
    """)
    
    # Set both KRISTIAN and RAMFIS as Week 8 winners
    print(f"\n✅ Setting Week 8 tie winners:")
    for winner in should_be_winners:
        cursor.execute("""
            UPDATE weekly_results 
            SET is_winner = 1 
            WHERE user_id = (SELECT id FROM users WHERE username = ? COLLATE NOCASE) 
            AND week = 8 AND year = 2025
        """, (winner.lower(),))
        print(f"  {winner} set as Week 8 winner ✅")
    
    conn.commit()
    
    # Verify all weekly winners now
    print(f"\n🔍 All Weekly Winners (Updated):")
    cursor.execute("""
        SELECT wr.week, u.username, wr.correct_picks, wr.total_picks
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.year = 2025 AND wr.is_winner = 1
        ORDER BY wr.week, u.username
    """)
    
    all_winners = cursor.fetchall()
    winner_counts = {}
    
    for week, username, correct, total in all_winners:
        print(f"  Week {week}: {username.upper()} ({correct}/{total})")
        winner_counts[username.upper()] = winner_counts.get(username.upper(), 0) + 1
    
    print(f"\n📈 Updated Season Win Counts:")
    for username, wins in sorted(winner_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {username}: {wins} wins")
    
    # Update user_statistics table
    print(f"\n🔄 Updating user_statistics table...")
    for username in ['kristian', 'ramfis', 'robert', 'coyote', 'vizca', 'raymond']:
        actual_wins = winner_counts.get(username.upper(), 0)
        cursor.execute("""
            UPDATE user_statistics 
            SET total_wins = ?, updated_at = datetime('now')
            WHERE user_id = (SELECT id FROM users WHERE username = ?)
        """, (actual_wins, username))
        if actual_wins > 0:
            print(f"  {username.upper()}: {actual_wins} wins")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 WEEK 8 WINNERS FIXED!")
    print("=" * 50)
    print("✅ Correct season standings now:")
    print("   🏆 KRISTIAN: 3 wins (Weeks 2, 3, 8)")
    print("   🥈 RAMFIS: 2 wins (Weeks 6, 8)")  
    print("   🥉 ROBERT: 1 win (Week 4)")
    print("   🎯 COYOTE: 1 win (Week 1)")
    print("   ⭐ VIZCA: 1 win (Week 5)")
    print("   🎪 RAYMOND: 1 win (Week 7)")
    print()
    print("🏆 KRISTIAN and RAMFIS both won Week 8 with 11/13 correct picks!")

if __name__ == "__main__":
    fix_week8_winners()