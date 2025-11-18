#!/usr/bin/env python3
"""
Check actual team selections for Monday Night Football
"""

import sqlite3

def check_mnf_team_picks():
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
    
    # Get ALL picks for Monday Night game, not just coyote and ramfis
    cursor.execute('''
        SELECT p.*, u.username 
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        WHERE p.game_id = ? AND u.is_admin = 0
        ORDER BY u.username
    ''', (mnf_game['id'],))
    
    picks = cursor.fetchall()
    print("\n=== ALL MONDAY NIGHT TEAM SELECTIONS ===")
    
    min_pickers = []
    chi_pickers = []
    
    for pick in picks:
        # Check the selected_team field - this is the actual team pick
        selected_team = pick['selected_team']
        correct_pick = selected_team == actual_winner
        
        if selected_team == 'MIN':
            min_pickers.append(pick['username'])
        else:
            chi_pickers.append(pick['username'])
        
        print(f"{pick['username']}: selected {selected_team} {'✓' if correct_pick else '✗'}")
        print(f"  Score prediction: {mnf_game['away_team']} {pick['predicted_away_score']} - {mnf_game['home_team']} {pick['predicted_home_score']}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Users who picked MIN to win: {', '.join(min_pickers)}")
    print(f"Users who picked CHI to win: {', '.join(chi_pickers)}")
    print(f"Actual winner was: {actual_winner}")
    
    conn.close()

if __name__ == "__main__":
    check_mnf_team_picks()
