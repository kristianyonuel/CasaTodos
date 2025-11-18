#!/usr/bin/env python3
"""
Debug the Monday Night tiebreaker issue with coyote and ramfis
"""

import sqlite3

def debug_tiebreaker():
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=== USERS LOOKUP ===")
    cursor.execute("SELECT id, username FROM users WHERE username IN ('coyote', 'ramfis')")
    users = cursor.fetchall()
    for user in users:
        print(f"ID {user['id']}: {user['username']}")
    
    print("\n=== WEEKLY RESULTS FOR WEEK 1, 2025 ===")
    cursor.execute("""
        SELECT wr.*, u.username 
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.week = 1 AND wr.year = 2025
        ORDER BY wr.weekly_rank
    """)
    results = cursor.fetchall()
    
    for result in results:
        print(f"Rank {result['weekly_rank']}: {result['username']} - {result['correct_picks']} correct picks")
    
    print("\n=== MONDAY NIGHT GAME INFO ===")
    cursor.execute("""
        SELECT * FROM nfl_games 
        WHERE week = 1 AND year = 2025 AND is_monday_night = 1
    """)
    mnf_game = cursor.fetchone()
    
    if mnf_game:
        print(f"Monday Night Game: {mnf_game['away_team']} @ {mnf_game['home_team']}")
        print(f"Score: {mnf_game['away_team']} {mnf_game['away_score']} - {mnf_game['home_team']} {mnf_game['home_score']}")
        print(f"Final: {mnf_game['is_final']}")
        
        print("\n=== MONDAY NIGHT PICKS ===")
        cursor.execute("""
            SELECT p.*, u.username, p.predicted_away_score, p.predicted_home_score
            FROM user_picks p
            JOIN users u ON p.user_id = u.id
            WHERE p.game_id = ? AND u.username IN ('coyote', 'ramfis')
        """, (mnf_game['id'],))
        
        picks = cursor.fetchall()
        for pick in picks:
            print(f"{pick['username']}: predicted {mnf_game['away_team']} {pick['predicted_away_score']} - {mnf_game['home_team']} {pick['predicted_home_score']}")
            home_diff = abs((pick['predicted_home_score'] or 0) - (mnf_game['home_score'] or 0))
            away_diff = abs((pick['predicted_away_score'] or 0) - (mnf_game['away_score'] or 0))
            total_diff = abs(((pick['predicted_home_score'] or 0) + (pick['predicted_away_score'] or 0)) - ((mnf_game['home_score'] or 0) + (mnf_game['away_score'] or 0)))
            print(f"  Home diff: {home_diff}, Away diff: {away_diff}, Total diff: {total_diff}")
    
    conn.close()

if __name__ == "__main__":
    debug_tiebreaker()
