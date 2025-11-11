#!/usr/bin/env python3

import sqlite3

def apply_correct_week9_scores():
    """Apply the correct Week 9 final scores from user data"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Game results from user data: 31-20 34-31 31-14 31-21 21-16 41-21 28-24 32-27 27-16 28-24 32-24 24-7 35-21 30-26
    # Order should match the actual games as they appear in picks data order
    
    # Mapping games to their actual final scores
    game_scores = {
        'Baltimore Ravens @ Miami Dolphins': (31, 20),    # Ravens won
        'Chicago Bears @ Cincinnati Bengals': (34, 31),   # Bears won
        'Minnesota Vikings @ Detroit Lions': (31, 14),     # Vikings won  
        'Carolina Panthers @ Green Bay Packers': (31, 21), # Panthers won
        'Los Angeles Chargers @ Tennessee Titans': (21, 16), # Chargers won
        'Atlanta Falcons @ New England Patriots': (41, 21),  # Falcons won
        'San Francisco 49ers @ New York Giants': (28, 24),   # 49ers won
        'Indianapolis Colts @ Pittsburgh Steelers': (32, 27), # Colts won
        'Denver Broncos @ Houston Texans': (27, 16),         # Broncos won
        'Jacksonville Jaguars @ Las Vegas Raiders': (28, 24), # Jaguars won
        'New Orleans Saints @ Los Angeles Rams': (32, 24),   # Saints won
        'Kansas City Chiefs @ Buffalo Bills': (24, 7),       # Chiefs won
        'Seattle Seahawks @ Washington Commanders': (35, 21), # Seahawks won
        'Arizona Cardinals @ Dallas Cowboys': (30, 26)       # Cardinals won (MNF)
    }
    
    print('Applying correct Week 9 final scores...')
    print('=' * 42)
    
    # Update each game with correct scores
    for game_key, (away_score, home_score) in game_scores.items():
        away_team, home_team = game_key.split(' @ ')
        
        cursor.execute('''
            UPDATE nfl_games 
            SET away_score = ?, home_score = ?, game_status = 'Final', is_final = 1
            WHERE home_team = ? AND away_team = ? AND week = 9
        ''', (away_score, home_score, home_team, away_team))
        
        print(f'{away_team} {away_score} - {home_team} {home_score}')
    
    conn.commit()
    
    # Recalculate pick correctness
    print('\nRecalculating all pick correctness...')
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
    
    # Show final corrected leaderboard
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
    print('\nFinal Corrected Week 9 Leaderboard:')
    print('=' * 38)
    
    for i, (username, correct) in enumerate(leaderboard, 1):
        print(f'{i}. {username.upper()}: {correct}/14')
    
    # Specific Monday Night Football check
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
    print('\nMonday Night Football Final:')
    print('=' * 30)
    for username, selected, away, home, away_score, home_score, is_correct in mnf_picks:
        result_text = "CORRECT" if is_correct else "WRONG"
        print(f'{username.upper()}: picked {selected} - {result_text}')
    
    print(f'\nCardinals won 30-26 over Cowboys')
    
    # Check for ties
    jean_score = vizca_score = 0
    for username, correct in leaderboard:
        if username.lower() == 'jean':
            jean_score = correct
        elif username.lower() == 'vizca':
            vizca_score = correct
    
    if jean_score == vizca_score:
        print(f'\n🎯 JEAN and VIZCA are TIED at {jean_score}/14!')
    else:
        print(f'\nJEAN: {jean_score}/14, VIZCA: {vizca_score}/14')
    
    conn.close()

if __name__ == '__main__':
    apply_correct_week9_scores()