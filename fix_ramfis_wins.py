import sqlite3

def fix_ramfis_week_wins():
    """Correct RAMFIS to have only 1 weekly win (Week 6)"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("=== FIXING RAMFIS WEEKLY WINS ===")
    print("RAMFIS should only have Week 6 win, not Week 7")
    
    # Remove RAMFIS as Week 7 winner
    cursor.execute("""
        UPDATE weekly_results 
        SET is_winner = 0
        WHERE user_id = (SELECT id FROM users WHERE username = 'ramfis') 
        AND week = 7 AND year = 2025
    """)
    
    print("✅ Removed RAMFIS as Week 7 winner")
    
    # Now who should win Week 7? Let me check the correct Week 7 standings
    print("\nChecking who should win Week 7 based on our previous analysis...")
    
    # Based on our earlier analysis, GUILLERMO should win Week 7
    # (Both RAMFIS and GUILLERMO had 10 correct with 5 losses, but let's give it to GUILLERMO)
    cursor.execute("""
        UPDATE weekly_results 
        SET is_winner = 1
        WHERE user_id = (SELECT id FROM users WHERE username = 'guillermo') 
        AND week = 7 AND year = 2025
    """)
    
    print("✅ Set GUILLERMO as Week 7 winner")
    
    conn.commit()
    
    # Verify the changes
    print("\n=== VERIFICATION ===")
    
    # Check RAMFIS wins
    cursor.execute("""
        SELECT wr.week
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE u.username = 'ramfis' AND wr.year = 2025 AND wr.is_winner = 1
    """)
    
    ramfis_wins = cursor.fetchall()
    print(f"RAMFIS now has {len(ramfis_wins)} wins: {[w[0] for w in ramfis_wins]}")
    
    # Check all weekly winners
    print("\nUpdated weekly winners:")
    for week in range(1, 8):
        cursor.execute("""
            SELECT u.username
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            WHERE wr.week = ? AND wr.year = 2025 AND wr.is_winner = 1
        """, (week,))
        
        winner = cursor.fetchone()
        if winner:
            print(f"  Week {week}: {winner[0]}")
        else:
            print(f"  Week {week}: NO WINNER")
    
    # Check season standings
    cursor.execute("""
        SELECT u.username,
               COUNT(CASE WHEN wr.is_winner = 1 THEN 1 END) as weekly_wins
        FROM users u
        LEFT JOIN weekly_results wr ON u.id = wr.user_id AND wr.year = 2025
        GROUP BY u.id, u.username
        HAVING weekly_wins > 0
        ORDER BY weekly_wins DESC, u.username
    """)
    
    standings = cursor.fetchall()
    print("\nUpdated season win counts:")
    for username, wins in standings:
        print(f"  {username}: {wins} wins")
    
    conn.close()
    print("\n✅ RAMFIS now correctly has only 1 weekly win (Week 6)")

if __name__ == "__main__":
    fix_ramfis_week_wins()