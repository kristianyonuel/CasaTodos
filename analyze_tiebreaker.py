#!/usr/bin/env python3
"""
Analyze the tiebreaker between users with 13 correct picks
"""

import sqlite3

def analyze_tiebreaker():
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get Monday Night game
    cursor.execute('SELECT * FROM nfl_games WHERE week = 1 AND year = 2025 AND is_monday_night = 1')
    mnf_game = cursor.fetchone()
    
    print(f"Actual Game Result: {mnf_game['away_team']} {mnf_game['away_score']} - {mnf_game['home_team']} {mnf_game['home_score']}")
    print(f"Home team ({mnf_game['home_team']}) scored: {mnf_game['home_score']}")
    print(f"Away team ({mnf_game['away_team']}) scored: {mnf_game['away_score']}")
    
    # Get picks for users with 13 correct picks who picked MIN to win
    cursor.execute('''
        SELECT p.*, u.username 
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        WHERE p.game_id = ? AND u.username IN ('coyote', 'vizca', 'raymond') AND p.selected_team = 'MIN'
        ORDER BY u.username
    ''', (mnf_game['id'],))
    
    picks = cursor.fetchall()
    print("\n=== TIEBREAKER ANALYSIS FOR 13-PICK USERS WHO PICKED MIN ===")
    
    for pick in picks:
        home_diff = abs(pick['predicted_home_score'] - mnf_game['home_score'])
        away_diff = abs(pick['predicted_away_score'] - mnf_game['away_score'])
        
        print(f"\n{pick['username']}:")
        print(f"  Predicted: {mnf_game['away_team']} {pick['predicted_away_score']} - {mnf_game['home_team']} {pick['predicted_home_score']}")
        print(f"  Home team ({mnf_game['home_team']}) diff: |{pick['predicted_home_score']} - {mnf_game['home_score']}| = {home_diff}")
        print(f"  Away team ({mnf_game['away_team']}) diff: |{pick['predicted_away_score']} - {mnf_game['away_score']}| = {away_diff}")
    
    print("\n=== TIEBREAKER LOGIC ===")
    print("1. Most correct picks (all have 13)")
    print("2. Picked correct MNF winner (all picked MIN ✓)")
    print("3. Closest to home team score")
    print("4. If tied on home, closest to away team score")
    
    conn.close()

if __name__ == "__main__":
    analyze_tiebreaker()
