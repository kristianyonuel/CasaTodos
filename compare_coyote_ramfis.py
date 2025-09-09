#!/usr/bin/env python3
"""
Compare coyote vs ramfis tiebreaker
"""

import sqlite3

def compare_coyote_ramfis():
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get Monday Night game
    cursor.execute('SELECT * FROM nfl_games WHERE week = 1 AND year = 2025 AND is_monday_night = 1')
    mnf_game = cursor.fetchone()
    
    print(f"Actual Game: {mnf_game['away_team']} {mnf_game['away_score']} - {mnf_game['home_team']} {mnf_game['home_score']}")
    
    # Get picks for coyote and raymond specifically
    cursor.execute('''
        SELECT p.*, u.username 
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        WHERE p.game_id = ? AND u.username IN ('coyote', 'raymond')
        ORDER BY u.username
    ''', (mnf_game['id'],))

    picks = cursor.fetchall()
    print("\n=== COYOTE vs RAYMOND TIEBREAKER ===")
    
    for pick in picks:
        correct_winner = pick['selected_team'] == 'MIN'  # MIN won
        
        print(f"\n{pick['username']}:")
        print(f"  Selected team: {pick['selected_team']} {'✓' if correct_winner else '✗'}")
        print(f"  Predicted: {mnf_game['away_team']} {pick['predicted_away_score']} - {mnf_game['home_team']} {pick['predicted_home_score']}")
        
        # Calculate differences
        home_diff = abs(pick['predicted_home_score'] - mnf_game['home_score'])
        away_diff = abs(pick['predicted_away_score'] - mnf_game['away_score'])
        
        print(f"  Home team (CHI) diff: |{pick['predicted_home_score']} - {mnf_game['home_score']}| = {home_diff}")
        print(f"  Away team (MIN) diff: |{pick['predicted_away_score']} - {mnf_game['away_score']}| = {away_diff}")
    
    print("\n=== TIEBREAKER ANALYSIS ===")
    print("Step 1: Who picked the correct winner (MIN)?")
    print("Step 2: Among correct pickers, closest to home team score")
    print("Step 3: If tied on home, closest to away team score")
    
    conn.close()

if __name__ == "__main__":
    compare_coyote_ramfis()
