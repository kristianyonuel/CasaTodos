#!/usr/bin/env python3
"""
Check who picked the correct Monday Night winner
"""

import sqlite3

def check_mnf_winners():
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get Monday Night game
    cursor.execute('SELECT * FROM nfl_games WHERE week = 1 AND year = 2025 AND is_monday_night = 1')
    mnf_game = cursor.fetchone()
    
    print(f"MNF Game: {mnf_game['away_team']} @ {mnf_game['home_team']}")
    print(f"Result: {mnf_game['away_team']} {mnf_game['away_score']} - {mnf_game['home_team']} {mnf_game['home_score']}")
    
    # Determine actual winner
    actual_winner = mnf_game['away_team'] if mnf_game['away_score'] > mnf_game['home_score'] else mnf_game['home_team']
    print(f"Actual Winner: {actual_winner}")
    
    # Get all MNF picks
    cursor.execute('''
        SELECT u.username, p.predicted_home_score, p.predicted_away_score
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        WHERE p.game_id = ?
        ORDER BY u.username
    ''', (mnf_game['id'],))
    
    picks = cursor.fetchall()
    print(f"\nAll Monday Night Picks:")
    print("-" * 50)
    
    correct_winners = []
    wrong_winners = []
    
    for pick in picks:
        pred_home = pick['predicted_home_score'] or 0
        pred_away = pick['predicted_away_score'] or 0
        predicted_winner = mnf_game['home_team'] if pred_home > pred_away else mnf_game['away_team']
        correct = predicted_winner == actual_winner
        
        status = "✓ CORRECT" if correct else "✗ WRONG"
        print(f"{pick['username']}: {mnf_game['away_team']} {pred_away} - {mnf_game['home_team']} {pred_home} (Predicted: {predicted_winner}) {status}")
        
        if correct:
            correct_winners.append(pick['username'])
        else:
            wrong_winners.append(pick['username'])
    
    print(f"\n🏆 USERS WHO PICKED CORRECT WINNER ({actual_winner}): {len(correct_winners)}")
    for user in correct_winners:
        print(f"  ✓ {user}")
    
    print(f"\n❌ USERS WHO PICKED WRONG WINNER: {len(wrong_winners)}")
    for user in wrong_winners:
        print(f"  ✗ {user}")
    
    conn.close()

if __name__ == "__main__":
    check_mnf_winners()
