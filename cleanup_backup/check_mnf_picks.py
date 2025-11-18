#!/usr/bin/env python3
"""
Check actual Monday Night picks for coyote and ramfis
"""

import sqlite3

def check_mnf_picks():
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get Monday Night game
    cursor.execute('SELECT * FROM nfl_games WHERE week = 1 AND year = 2025 AND is_monday_night = 1')
    mnf_game = cursor.fetchone()
    
    print(f"Monday Night Game: {mnf_game['away_team']} @ {mnf_game['home_team']}")
    print(f"Actual Result: {mnf_game['away_team']} {mnf_game['away_score']} - {mnf_game['home_team']} {mnf_game['home_score']}")
    
    # Determine actual winner
    if mnf_game['home_score'] > mnf_game['away_score']:
        actual_winner = mnf_game['home_team']
    else:
        actual_winner = mnf_game['away_team']
    print(f"Actual Winner: {actual_winner}")
    
    # Get picks for coyote and ramfis
    cursor.execute('''
        SELECT p.*, u.username 
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        WHERE p.game_id = ? AND u.username IN ('coyote', 'ramfis')
    ''', (mnf_game['id'],))
    
    picks = cursor.fetchall()
    print("\n=== MONDAY NIGHT PICKS ===")
    for pick in picks:
        # Determine who they predicted to win
        if pick['predicted_home_score'] > pick['predicted_away_score']:
            predicted_winner = mnf_game['home_team']
        else:
            predicted_winner = mnf_game['away_team']
        
        correct_winner = predicted_winner == actual_winner
        
        print(f"{pick['username']}: predicted {mnf_game['away_team']} {pick['predicted_away_score']} - {mnf_game['home_team']} {pick['predicted_home_score']}")
        print(f"  Predicted Winner: {predicted_winner} {'✓' if correct_winner else '✗'}")
        
        # Calculate tiebreaker differences
        home_diff = abs(pick['predicted_home_score'] - mnf_game['home_score'])
        away_diff = abs(pick['predicted_away_score'] - mnf_game['away_score'])
        total_diff = abs((pick['predicted_home_score'] + pick['predicted_away_score']) - (mnf_game['home_score'] + mnf_game['away_score']))
        
        print(f"  Tiebreaker: Home ±{home_diff}, Away ±{away_diff}, Total ±{total_diff}")
        print()
    
    conn.close()

if __name__ == "__main__":
    check_mnf_picks()
