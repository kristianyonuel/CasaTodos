#!/usr/bin/env python3

import sqlite3

def apply_week9_final_results():
    """Apply final Week 9 game results and recalculate picks"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Final scores for Week 9 games in order
    # Format: (away_score, home_score) for each game
    final_scores = [
        (31, 20),  # Ravens @ Dolphins
        (34, 31),  # Bears @ Bengals  
        (31, 14),  # Vikings @ Lions
        (31, 21),  # Panthers @ Packers
        (21, 16),  # Chargers @ Titans
        (41, 21),  # Falcons @ Patriots
        (28, 24),  # 49ers @ Giants
        (32, 27),  # Colts @ Steelers
        (27, 16),  # Broncos @ Texans
        (28, 24),  # Jaguars @ Raiders
        (32, 24),  # Saints @ Rams
        (24, 7),   # Chiefs @ Bills
        (35, 21),  # Seahawks @ Commanders
        (30, 26)   # Cardinals @ Cowboys (MNF)
    ]
    
    # Get Week 9 games in order
    cursor.execute('SELECT game_id, home_team, away_team FROM nfl_games WHERE week = 9 ORDER BY game_id')
    games = cursor.fetchall()
    
    print('Applying final Week 9 results...')
    print('=' * 40)
    
    # Update game scores
    for i, (game_id, home_team, away_team) in enumerate(games):
        if i < len(final_scores):
            away_score, home_score = final_scores[i]
            
            cursor.execute('''
                UPDATE nfl_games 
                SET away_score = ?, home_score = ?, game_status = 'Final', is_final = 1
                WHERE game_id = ?
            ''', (away_score, home_score, game_id))
            
            print(f'{away_team} {away_score} - {home_team} {home_score}')
    
    conn.commit()
    
    # Now recalculate all pick correctness for Week 9
    print('\nRecalculating pick correctness...')
    cursor.execute('''
        SELECT up.id, up.selected_team, ng.home_team, ng.away_team, ng.home_score, ng.away_score
        FROM user_picks up
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE ng.week = 9
    ''')
    
    picks = cursor.fetchall()
    
    for pick_id, selected_team, home_team, away_team, home_score, away_score in picks:
        # Determine winner
        if home_score > away_score:
            winner = home_team
        else:
            winner = away_team
        
        # Check if pick is correct
        is_correct = 1 if selected_team == winner else 0
        
        # Update pick correctness
        cursor.execute('''
            UPDATE user_picks 
            SET is_correct = ?
            WHERE id = ?
        ''', (is_correct, pick_id))
    
    conn.commit()
    
    # Show final leaderboard
    cursor.execute('''
        SELECT 
            u.username,
            COUNT(CASE WHEN up.is_correct = 1 THEN 1 END) as correct_picks
        FROM users u
        LEFT JOIN user_picks up ON u.id = up.user_id
        LEFT JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE ng.week = 9
        GROUP BY u.id, u.username
        ORDER BY correct_picks DESC, u.username
    ''')
    
    leaderboard = cursor.fetchall()
    print('\nFinal Week 9 Leaderboard:')
    print('=' * 30)
    
    for i, (username, correct) in enumerate(leaderboard, 1):
        print(f'{i}. {username.upper()}: {correct}/14')
    
    # Check specific users
    print('\nKey Comparisons:')
    print('=' * 20)
    
    # Check VIZCA vs JEAN for Monday Night Football
    cursor.execute('''
        SELECT 
            u.username,
            up.selected_team,
            ng.away_team,
            ng.home_team,
            ng.away_score,
            ng.home_score,
            up.is_correct
        FROM users u
        JOIN user_picks up ON u.id = up.user_id
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE ng.home_team = 'Dallas Cowboys' AND ng.week = 9 
        AND u.username IN ('vizca', 'jean')
        ORDER BY u.username
    ''')
    
    mnf_picks = cursor.fetchall()
    print('Monday Night Football:')
    for username, selected, away, home, away_score, home_score, is_correct in mnf_picks:
        winner = away if away_score > home_score else home
        print(f'{username.upper()}: picked {selected} - {"CORRECT" if is_correct else "WRONG"} (Cardinals won 30-26)')
    
    conn.close()

if __name__ == '__main__':
    apply_week9_final_results()