#!/usr/bin/env python3
"""Check and fix Jean's scoring"""

from app import get_db
from database_sync import update_pick_correctness


def main():
    # Update the pick correctness for Week 1
    result = update_pick_correctness(1, 2025)
    print(f'Updated correctness for {result} picks in Week 1, 2025')

    # Now check Jean's corrected results
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get Jean's ID
        cursor.execute('SELECT id FROM users WHERE username = ?', ('jean',))
        jean_id = cursor.fetchone()[0]
        
        # Check corrected picks
        cursor.execute('''
            SELECT p.selected_team, p.is_correct,
                   g.home_team, g.away_team, g.home_score, g.away_score, g.game_id
            FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            WHERE p.user_id = ? AND g.week = 1 AND g.year = 2025 AND g.is_final = 1
            ORDER BY g.game_date
        ''', (jean_id,))
        
        picks = cursor.fetchall()
        correct_count = 0
        
        print('\nJean\'s corrected picks:')
        for pick in picks:
            selected_team, is_correct, home_team, away_team, home_score, away_score, game_id = pick
            
            actual_winner = home_team if home_score > away_score else away_team
            should_be_correct = (selected_team == actual_winner)
            
            status = 'CORRECT' if is_correct else 'INCORRECT'
            if is_correct != should_be_correct:
                status += ' (MISMATCH!)'
            
            print(f'  {game_id}: {away_team} @ {home_team} ({away_score}-{home_score})')
            print(f'    Selected: {selected_team}, Winner: {actual_winner}, Status: {status}')
            
            if is_correct:
                correct_count += 1
        
        print(f'\nJean should have {correct_count} correct picks')
        
        # Also run the leaderboard query to see what it returns
        cursor.execute('''
            SELECT COUNT(p.id) as total_picks,
                   SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks
            FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            WHERE p.user_id = ? AND g.week = 1 AND g.year = 2025 AND g.is_final = 1
        ''', (jean_id,))
        
        leaderboard_data = cursor.fetchone()
        print(f'Leaderboard query: {leaderboard_data[1]} correct out of {leaderboard_data[0]} total')


if __name__ == '__main__':
    main()
