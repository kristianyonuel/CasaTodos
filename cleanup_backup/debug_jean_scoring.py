#!/usr/bin/env python3
"""Debug Jean's scoring issue"""

from app import get_db

def check_jean_picks():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # First, find Jean's user ID
        cursor.execute("SELECT id, username FROM users WHERE username LIKE '%jean%' OR username LIKE '%Jean%'")
        jean_users = cursor.fetchall()
        print('Users matching Jean:')
        for user in jean_users:
            print(f'  ID: {user[0]}, Username: {user[1]}')
        
        if not jean_users:
            print('No users found matching Jean')
            return
        
        jean_id = jean_users[0][0]  # Use first match
        jean_username = jean_users[0][1]
        
        print(f'\nAnalyzing picks for {jean_username} (ID: {jean_id}):')
        
        # Check Week 1 picks and results
        cursor.execute('''
            SELECT p.id, p.selected_team, p.is_correct,
                   g.home_team, g.away_team, g.home_score, g.away_score, g.is_final,
                   g.week, g.year, g.game_id
            FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            WHERE p.user_id = ? AND g.week = 1 AND g.year = 2025
            ORDER BY g.game_date
        ''', (jean_id,))
        
        picks = cursor.fetchall()
        correct_count = 0
        incorrect_count = 0
        
        print(f'\nWeek 1 picks for {jean_username}:')
        for pick in picks:
            pick_id, selected_team, is_correct, home_team, away_team, home_score, away_score, is_final, week, year, game_id = pick
            
            if is_final:
                # Determine actual winner
                if home_score is not None and away_score is not None:
                    actual_winner = home_team if home_score > away_score else away_team
                    should_be_correct = (selected_team == actual_winner)
                    
                    status = 'CORRECT' if is_correct else 'INCORRECT'
                    if is_correct != should_be_correct:
                        status += f' (SHOULD BE {"CORRECT" if should_be_correct else "INCORRECT"})'
                    
                    print(f'  Game {game_id}: {away_team} @ {home_team} ({home_score}-{away_score})')
                    print(f'    Selected: {selected_team}, Winner: {actual_winner}, Status: {status}')
                    
                    if is_correct:
                        correct_count += 1
                    else:
                        incorrect_count += 1
                else:
                    print(f'  Game {game_id}: {away_team} @ {home_team}: Game final but no scores')
            else:
                print(f'  Game {game_id}: {away_team} @ {home_team}: Game not final yet')
        
        print(f'\nManual count: {correct_count} correct, {incorrect_count} incorrect')
        
        # Check what the leaderboard query returns
        cursor.execute('''
            SELECT COUNT(p.id) as total_picks,
                   SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks
            FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            WHERE p.user_id = ? AND g.week = 1 AND g.year = 2025 AND g.is_final = 1
        ''', (jean_id,))
        
        leaderboard_data = cursor.fetchone()
        print(f'Leaderboard query result: {leaderboard_data[1]} correct out of {leaderboard_data[0]} total')
        
        # Check if there are any discrepancies in is_correct field
        cursor.execute('''
            SELECT p.id, p.selected_team, p.is_correct,
                   g.home_team, g.away_team, g.home_score, g.away_score, g.game_id
            FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            WHERE p.user_id = ? AND g.week = 1 AND g.year = 2025 AND g.is_final = 1
              AND g.home_score IS NOT NULL AND g.away_score IS NOT NULL
        ''', (jean_id,))
        
        final_picks = cursor.fetchall()
        print(f'\nDetailed analysis of finalized games:')
        
        correct_manual = 0
        for pick in final_picks:
            pick_id, selected_team, is_correct, home_team, away_team, home_score, away_score, game_id = pick
            
            actual_winner = home_team if home_score > away_score else away_team
            should_be_correct = (selected_team == actual_winner)
            
            if should_be_correct:
                correct_manual += 1
            
            if is_correct != should_be_correct:
                print(f'  MISMATCH Game {game_id}: {away_team} @ {home_team} ({home_score}-{away_score})')
                print(f'    Selected: {selected_team}, Winner: {actual_winner}')
                print(f'    Database says: {"CORRECT" if is_correct else "INCORRECT"}')
                print(f'    Should be: {"CORRECT" if should_be_correct else "INCORRECT"}')
        
        print(f'\nShould have {correct_manual} correct picks based on game results')

if __name__ == '__main__':
    check_jean_picks()
