#!/usr/bin/env python3

import sqlite3

def update_week9_picks_final():
    """Update Week 9 picks with the actual user data provided"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # User order and their picks for each game
    users = ['JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 'KRISTIAN', 'FER', 'MIKITIN']
    
    # Actual picks data (14 games)
    picks_data = [
        ['ravens', 'ravens', 'ravens', 'miami', 'ravens', 'ravens', 'ravens', 'ravens', 'ravens', 'Miami', 'ravens', 'ravens', 'ravens', 'ravens'],
        ['Bengals', 'Bears', 'Bears', 'Bengals', 'Bears', 'Bears', 'Bengals', 'Bears', 'Bears', 'Bears', 'Bears', 'Bears', 'Bengals', 'Bengals'],
        ['Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Minn', 'Lions', 'Lions', 'Lions', 'Lions'],
        ['Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb'],
        ['Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers'],
        ['Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats'],
        ['49ers', '49ers', '49ers', '49ers', '49ers', 'Giants', '49ers', '49ers', 'Giants', 'Giants', 'Giants', '49ers', 'Giants', '49ers'],
        ['Colts', 'Colts', 'Colts', 'Pit', 'Colts', 'Colts', 'Colts', 'Colts', 'Pitt', 'Pitt', 'Colts', 'Colts', 'Pitt', 'Colts'],
        ['Denver', 'Texans', 'Denver', 'Den', 'Denver', 'Denver', 'Denver', 'Denver', 'Texans', 'Denver', 'Denver', 'Texans', 'Denver', 'Denver'],
        ['Jax', 'Jax', 'Raiders', 'Jax', 'Jax', 'Jax', 'Jax', 'Jax', 'Jax', 'Raiders', 'Jax', 'Jax', 'Jax', 'Jax'],
        ['Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams'],
        ['Bills', 'Bills', 'Kc', 'Kc', 'Kc', 'Kc', 'Bills', 'Bills', 'Bills', 'Kc', 'Kc', 'Kc', 'Bills', 'Kc'],
        ['Wash', 'Seattle', 'Seattle', 'Wash', 'Seattle', 'Wash', 'Wash', 'Wash', 'Seattle', 'Seattle', 'Seattle', 'Seattle', 'Wash', 'Seattle'],
        ['Dallas', 'Arizona', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Arizona', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Dallas']
    ]
    
    # Get user IDs
    user_ids = {}
    for username in users:
        cursor.execute('SELECT id FROM users WHERE UPPER(username) = UPPER(?)', (username,))
        result = cursor.fetchone()
        if result:
            user_ids[username] = result[0]
    
    # Get Week 9 games in order
    cursor.execute('SELECT game_id, home_team, away_team FROM nfl_games WHERE week = 9 ORDER BY game_id')
    games = cursor.fetchall()
    
    # Team name mappings to full names
    team_mappings = {
        'ravens': 'Baltimore Ravens',
        'miami': 'Miami Dolphins',
        'bears': 'Chicago Bears',
        'bengals': 'Cincinnati Bengals',
        'lions': 'Detroit Lions',
        'minn': 'Minnesota Vikings',
        'gb': 'Green Bay Packers',
        'chargers': 'Los Angeles Chargers',
        'pats': 'New England Patriots',
        '49ers': 'San Francisco 49ers',
        'giants': 'New York Giants',
        'colts': 'Indianapolis Colts',
        'pit': 'Pittsburgh Steelers',
        'pitt': 'Pittsburgh Steelers',
        'denver': 'Denver Broncos',
        'den': 'Denver Broncos',
        'texans': 'Houston Texans',
        'jax': 'Jacksonville Jaguars',
        'raiders': 'Las Vegas Raiders',
        'rams': 'Los Angeles Rams',
        'bills': 'Buffalo Bills',
        'kc': 'Kansas City Chiefs',
        'wash': 'Washington Commanders',
        'seattle': 'Seattle Seahawks',
        'dallas': 'Dallas Cowboys',
        'arizona': 'Arizona Cardinals'
    }
    
    print('Updating Week 9 picks with actual user data...')
    print('=' * 50)
    
    # Update picks for each game
    for game_idx, (game_id, home_team, away_team) in enumerate(games):
        print(f'Game {game_idx + 1}: {away_team} @ {home_team}')
        
        # Get game picks for this game
        game_picks = picks_data[game_idx]
        
        for user_idx, username in enumerate(users):
            if username in user_ids:
                user_id = user_ids[username]
                pick_text = game_picks[user_idx].lower()
                
                # Map pick to full team name
                selected_team = team_mappings.get(pick_text, pick_text)
                
                # Update the pick
                cursor.execute('''
                    UPDATE user_picks 
                    SET selected_team = ?
                    WHERE user_id = ? AND game_id = ?
                ''', (selected_team, user_id, game_id))
                
                print(f'  {username}: {selected_team}')
    
    conn.commit()
    print('\n✅ All picks updated!')
    
    # Now recalculate scoring with actual game results
    final_scores = [31, 20, 34, 31, 31, 14, 31, 21, 21, 16, 41, 21, 28, 24, 32, 27, 27, 16, 28, 24, 32, 24, 24, 7, 35, 21, 30, 26]
    
    # Update game scores (away_score, home_score for each game)
    score_idx = 0
    for game_id, home_team, away_team in games:
        away_score = final_scores[score_idx]
        home_score = final_scores[score_idx + 1]
        
        cursor.execute('''
            UPDATE nfl_games 
            SET away_score = ?, home_score = ?, status = 'Final'
            WHERE game_id = ?
        ''', (away_score, home_score, game_id))
        
        print(f'Updated: {away_team} {away_score} - {home_team} {home_score}')
        score_idx += 2
    
    # Recalculate all pick correctness
    cursor.execute('''
        UPDATE user_picks 
        SET is_correct = 
            CASE 
                WHEN (ng.home_score > ng.away_score AND up.selected_team = ng.home_team) OR
                     (ng.away_score > ng.home_score AND up.selected_team = ng.away_team)
                THEN 1
                ELSE 0
            END
        FROM nfl_games ng
        WHERE user_picks.game_id = ng.game_id AND ng.week = 9
    ''')
    
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
    
    # Special check for VIZCA vs JEAN
    print('\nVIZCA vs JEAN Analysis:')
    print('=' * 25)
    for username in ['vizca', 'jean']:
        for user, correct in leaderboard:
            if user.lower() == username:
                print(f'{user.upper()}: {correct}/14')
    
    conn.close()

if __name__ == '__main__':
    update_week9_picks_final()