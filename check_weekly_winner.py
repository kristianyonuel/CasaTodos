#!/usr/bin/env python3
"""Check why coyote is marked as weekly winner"""

import sqlite3

def check_weekly_winner():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🔍 CHECKING WEEKLY RESULTS FOR WEEK 1:")
    cursor.execute('''
        SELECT wr.user_id, u.username, wr.week, wr.year, 
               wr.is_winner, wr.total_points, wr.created_at
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.week = 1 AND wr.year = 2025
        ORDER BY wr.is_winner DESC, wr.total_points DESC
    ''')
    
    results = cursor.fetchall()
    print("User ID | Username | Week | Year | Is Winner | Total Points | Created At")
    print("-" * 75)
    
    for user_id, username, week, year, is_winner, total_points, created_at in results:
        winner_status = "YES" if is_winner else "No"
        print(f"{user_id:7} | {username:8} | {week:4} | {year:4} | {winner_status:9} | {total_points:12} | {created_at}")
    
    print(f"\n🎮 CHECKING GAME STATUS FOR WEEK 1:")
    cursor.execute('''
        SELECT COUNT(*) as total_games,
               COUNT(CASE WHEN is_final = 1 THEN 1 END) as final_games,
               COUNT(CASE WHEN is_final = 0 THEN 1 END) as pending_games
        FROM nfl_games 
        WHERE week = 1 AND year = 2025
    ''')
    
    total, final, pending = cursor.fetchone()
    print(f"Total games: {total}, Final: {final}, Pending: {pending}")
    
    if pending > 0:
        print("❌ Week 1 is NOT complete - weekly winner should not be declared!")
        print("📝 Recommendation: Remove is_winner=TRUE until all games are final")
    else:
        print("✅ Week 1 is complete - weekly winner declaration is valid")
    
    conn.close()

if __name__ == "__main__":
    check_weekly_winner()
