#!/usr/bin/env python3
"""
Verify the final scoring results
"""

import sqlite3


def verify_results():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check the weekly results table with usernames
    cursor.execute('''
        SELECT u.username, wr.correct_picks, wr.weekly_rank
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.week = 1 AND wr.year = 2025 
        ORDER BY wr.weekly_rank
    ''')
    results = cursor.fetchall()
    print('=== WEEKLY RESULTS TABLE ===')
    for username, correct, rank in results:
        print(f'{rank}. {username}: {correct} correct picks')
    
    # Check coyote's Monday Night pick details
    cursor.execute('''
        SELECT p.predicted_away_score, p.predicted_home_score, 
               p.selected_team, p.is_correct,
               g.away_team, g.home_team, g.away_score, g.home_score
        FROM user_picks p
        JOIN nfl_games g ON p.game_id = g.id
        JOIN users u ON p.user_id = u.id
        WHERE u.username = "coyote" AND g.week = 1 AND g.year = 2025 
        AND g.home_team = "CHI" AND g.away_team = "MIN"
    ''')
    mnf_pick = cursor.fetchone()
    print(f'\n=== COYOTE MONDAY NIGHT DETAILS ===')
    print(f'Predicted: {mnf_pick[4]} {mnf_pick[0]} - {mnf_pick[5]} {mnf_pick[1]}')
    print(f'Actual: {mnf_pick[4]} {mnf_pick[6]} - {mnf_pick[5]} {mnf_pick[7]}')
    print(f'Selected Team: {mnf_pick[2]}')
    print(f'Is Correct: {mnf_pick[3]}')
    
    # Calculate differences for tiebreaker
    away_diff = abs(mnf_pick[0] - mnf_pick[6])  # predicted vs actual away
    home_diff = abs(mnf_pick[1] - mnf_pick[7])  # predicted vs actual home
    print(f'Away Score Difference: {away_diff}')
    print(f'Home Score Difference: {home_diff}')
    
    conn.close()


if __name__ == "__main__":
    verify_results()
