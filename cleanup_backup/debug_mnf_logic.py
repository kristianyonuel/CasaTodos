#!/usr/bin/env python3
"""
Check the selected_team vs predicted scores to debug tiebreaker logic
"""

import sqlite3

def debug_mnf_logic():
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get Monday Night game
    cursor.execute('SELECT * FROM nfl_games WHERE week = 1 AND year = 2025 AND is_monday_night = 1')
    mnf_game = cursor.fetchone()
    
    print(f"Actual Game: MIN {mnf_game['away_score']} - CHI {mnf_game['home_score']}")
    print(f"Winner: MIN")
    
    # Check the picks for top users
    cursor.execute('''
        SELECT u.username, p.selected_team, p.predicted_away_score, p.predicted_home_score
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        JOIN nfl_games g ON p.game_id = g.id
        WHERE g.week = 1 AND g.year = 2025 AND g.is_monday_night = 1
        AND u.username IN ('coyote', 'raymond', 'vizca')
        ORDER BY u.username
    ''')
    
    picks = cursor.fetchall()
    print("\n=== CHECKING SELECTED_TEAM vs PREDICTED SCORES ===")
    
    for pick in picks:
        predicted_winner_by_score = 'MIN' if pick['predicted_away_score'] > pick['predicted_home_score'] else 'CHI'
        
        print(f"{pick['username']}:")
        print(f"  selected_team: {pick['selected_team']}")
        print(f"  predicted: MIN {pick['predicted_away_score']} - CHI {pick['predicted_home_score']}")
        print(f"  winner by score: {predicted_winner_by_score}")
        print(f"  Match? {pick['selected_team'] == predicted_winner_by_score}")
        print(f"  Correct winner? {pick['selected_team'] == 'MIN'}")
        print()
    
    conn.close()

if __name__ == "__main__":
    debug_mnf_logic()
