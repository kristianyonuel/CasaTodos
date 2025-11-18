#!/usr/bin/env python3
"""
Debug script to check actual Monday Night picks and selected_team values
"""

import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('🔍 Debugging Monday Night Picks for Contenders')
print('=' * 50)

# Get Monday Night game
cursor.execute('''
    SELECT id, home_team, away_team 
    FROM nfl_games 
    WHERE week = 1 AND is_monday_night = 1
''')
mnf_game = cursor.fetchone()
game_id, home_team, away_team = mnf_game
print(f'Monday Night Game: {away_team} @ {home_team}')

# Get picks for the 4 contenders only
contenders = ['coyote', 'ramfis', 'raymond', 'vizca']

for username in contenders:
    cursor.execute('''
        SELECT p.selected_team, p.predicted_home_score, p.predicted_away_score
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        WHERE u.username = ? AND p.game_id = ?
    ''', (username, game_id))
    
    pick = cursor.fetchone()
    if pick:
        selected_team, pred_home, pred_away = pick
        total = pred_home + pred_away
        
        print(f'\n{username}:')
        print(f'  {away_team} {pred_away} - {pred_home} {home_team} (Total: {total})')
        
        # Determine who they actually picked to win based on scores
        if pred_home > pred_away:
            predicted_winner = home_team
        else:
            predicted_winner = away_team
        
        print(f'  Predicted winner by score: {predicted_winner}')
        print(f'  Selected team field: {selected_team}')
        
        # Check if there's a mismatch
        if selected_team != predicted_winner:
            print(f'  ⚠️  MISMATCH: selected_team={selected_team} but scores predict {predicted_winner}')

conn.close()

print('\n🎯 The issue is likely that we should use selected_team field instead of comparing scores!')
print('   OR the selected_team field might not be populated correctly.')
