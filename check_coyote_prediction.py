#!/usr/bin/env python3
"""
Check coyote's exact database prediction
"""

import sqlite3

def check_coyote_prediction():
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get Monday Night game details
    cursor.execute('SELECT id, away_team, home_team, away_score, home_score FROM nfl_games WHERE week = 1 AND year = 2025 AND is_monday_night = 1')
    game = cursor.fetchone()
    
    print(f"Game: {game['away_team']} @ {game['home_team']}")
    print(f"Actual Result: {game['away_team']} {game['away_score']} - {game['home_team']} {game['home_score']}")
    
    # Get coyote's exact prediction
    cursor.execute('''
        SELECT u.username, p.selected_team, p.predicted_away_score, p.predicted_home_score, p.created_at
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        WHERE p.game_id = ? AND u.username IN ('coyote', 'raymond')
        ORDER BY u.username
    ''', (game['id'],))
    
    pick = cursor.fetchone()
    picks = cursor.fetchall()
    
    print("\n=== DATABASE RECORDS ===")
    for pick in picks:
        print(f"\n{pick['username']} Database Record:")
        print(f"  Selected Team: {pick['selected_team']}")
        print(f"  Predicted Away Score ({game['away_team']}): {pick['predicted_away_score']}")
        print(f"  Predicted Home Score ({game['home_team']}): {pick['predicted_home_score']}")
        print(f"  Full Prediction: {game['away_team']} {pick['predicted_away_score']} - {game['home_team']} {pick['predicted_home_score']}")
        
        # Calculate differences
        away_diff = abs(pick['predicted_away_score'] - game['away_score'])
        home_diff = abs(pick['predicted_home_score'] - game['home_score'])
        print(f"  Away Difference: |{pick['predicted_away_score']} - {game['away_score']}| = {away_diff}")
        print(f"  Home Difference: |{pick['predicted_home_score']} - {game['home_score']}| = {home_diff}")
    
    if not picks:
        print('No picks found')
    
    conn.close()

if __name__ == "__main__":
    check_coyote_prediction()
