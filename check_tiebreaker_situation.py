#!/usr/bin/env python3
"""Check current standings and tiebreaker situations"""

import sqlite3

def check_tiebreaker_situation():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print('Current Week 2 Standings:')
    print('=' * 50)
    
    # Get current standings
    cursor.execute('''
        SELECT 
            u.username,
            COUNT(CASE WHEN g.is_final = 1 AND p.is_correct = 1 THEN 1 END) as wins,
            COUNT(CASE WHEN g.is_final = 1 THEN 1 END) as total_games
        FROM users u
        JOIN user_picks p ON u.id = p.user_id  
        JOIN nfl_games g ON p.game_id = g.id
        WHERE g.week = 2 AND g.year = 2025 AND u.is_admin = 0
        GROUP BY u.id, u.username
        ORDER BY wins DESC, u.username
    ''')
    
    standings = cursor.fetchall()
    for user, wins, total in standings:
        print(f'{user:12} {wins:2}/14 wins')
    
    print('\n' + '=' * 50)
    print('LAC@LV Picks and Score Predictions:')
    print('=' * 50)
    
    # Find LAC@LV game  
    cursor.execute('''
        SELECT id, home_team, away_team FROM nfl_games 
        WHERE week = 2 AND year = 2025 
        AND ((home_team = 'LAC' AND away_team = 'LV') OR (home_team = 'LV' AND away_team = 'LAC'))
    ''')
    lac_game = cursor.fetchone()
    
    if lac_game:
        game_id, home_team, away_team = lac_game
        print(f'Game: {away_team} @ {home_team}')
        print()
        
        cursor.execute('''
            SELECT 
                u.username,
                p.selected_team,
                p.predicted_home_score,
                p.predicted_away_score
            FROM users u
            JOIN user_picks p ON u.id = p.user_id
            WHERE p.game_id = ? AND u.is_admin = 0
            ORDER BY u.username
        ''', (game_id,))
        
        lac_picks = cursor.fetchall()
        
        # Filter for users mentioned in question
        target_users = ['javier', 'joniel', 'ramfis', 'kristian', 'robert', 'shorty']
        
        print('Target users who picked LAC:')
        for user, selected, pred_home, pred_away in lac_picks:
            if user.lower() in target_users and selected == 'LAC':
                total_pred = (pred_home or 0) + (pred_away or 0)
                print(f'{user:10} picked {selected} | Predicted: {away_team} {pred_away or 0} - {pred_home or 0} {home_team} (Total: {total_pred})')
    
    conn.close()

if __name__ == "__main__":
    check_tiebreaker_situation()
