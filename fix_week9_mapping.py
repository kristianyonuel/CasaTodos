#!/usr/bin/env python3

import sqlite3

def fix_week9_picks_correct_mapping():
    """Fix Week 9 picks with correct game-to-pick mapping"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # User order as provided
    users = ['JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 'KRISTIAN', 'FER', 'MIKITIN']
    
    # Get user IDs
    user_ids = {}
    for username in users:
        cursor.execute('SELECT id FROM users WHERE UPPER(username) = UPPER(?)', (username,))
        result = cursor.fetchone()
        if result:
            user_ids[username] = result[0]
    
    # Picks data in the order provided by user
    # Based on the pick order: ravens, bengals, lions, gb, chargers, pats, 49ers, colts, denver, jax, rams, bills, wash, dallas
    picks_by_game_type = {
        'Ravens @ Dolphins': ['ravens', 'ravens', 'ravens', 'miami', 'ravens', 'ravens', 'ravens', 'ravens', 'ravens', 'Miami', 'ravens', 'ravens', 'ravens', 'ravens'],
        'Bears @ Bengals': ['Bengals', 'Bears', 'Bears', 'Bengals', 'Bears', 'Bears', 'Bengals', 'Bears', 'Bears', 'Bears', 'Bears', 'Bears', 'Bengals', 'Bengals'],
        'Vikings @ Lions': ['Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Minn', 'Lions', 'Lions', 'Lions', 'Lions'],
        'Panthers @ Packers': ['Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb'],
        'Chargers @ Titans': ['Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers'],
        'Falcons @ Patriots': ['Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats'],
        '49ers @ Giants': ['49ers', '49ers', '49ers', '49ers', '49ers', 'Giants', '49ers', '49ers', 'Giants', 'Giants', 'Giants', '49ers', 'Giants', '49ers'],
        'Colts @ Steelers': ['Colts', 'Colts', 'Colts', 'Pit', 'Colts', 'Colts', 'Colts', 'Colts', 'Pitt', 'Pitt', 'Colts', 'Colts', 'Pitt', 'Colts'],
        'Broncos @ Texans': ['Denver', 'Texans', 'Denver', 'Den', 'Denver', 'Denver', 'Denver', 'Denver', 'Texans', 'Denver', 'Denver', 'Texans', 'Denver', 'Denver'],
        'Jaguars @ Raiders': ['Jax', 'Jax', 'Raiders', 'Jax', 'Jax', 'Jax', 'Jax', 'Jax', 'Jax', 'Raiders', 'Jax', 'Jax', 'Jax', 'Jax'],
        'Saints @ Rams': ['Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams'],
        'Chiefs @ Bills': ['Bills', 'Bills', 'Kc', 'Kc', 'Kc', 'Kc', 'Bills', 'Bills', 'Bills', 'Kc', 'Kc', 'Kc', 'Bills', 'Kc'],
        'Seahawks @ Commanders': ['Wash', 'Seattle', 'Seattle', 'Wash', 'Seattle', 'Wash', 'Wash', 'Wash', 'Seattle', 'Seattle', 'Seattle', 'Seattle', 'Wash', 'Seattle'],
        'Cardinals @ Cowboys': ['Dallas', 'Arizona', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Arizona', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Dallas']
    }
    
    # Team name mappings
    team_mappings = {
        'ravens': 'Baltimore Ravens', 'miami': 'Miami Dolphins',
        'bears': 'Chicago Bears', 'bengals': 'Cincinnati Bengals',
        'lions': 'Detroit Lions', 'minn': 'Minnesota Vikings',
        'gb': 'Green Bay Packers', 'chargers': 'Los Angeles Chargers',
        'pats': 'New England Patriots', '49ers': 'San Francisco 49ers',
        'giants': 'New York Giants', 'colts': 'Indianapolis Colts',
        'pit': 'Pittsburgh Steelers', 'pitt': 'Pittsburgh Steelers',
        'denver': 'Denver Broncos', 'den': 'Denver Broncos',
        'texans': 'Houston Texans', 'jax': 'Jacksonville Jaguars',
        'raiders': 'Las Vegas Raiders', 'rams': 'Los Angeles Rams',
        'bills': 'Buffalo Bills', 'kc': 'Kansas City Chiefs',
        'wash': 'Washington Commanders', 'seattle': 'Seattle Seahawks',
        'dallas': 'Dallas Cowboys', 'arizona': 'Arizona Cardinals'
    }
    
    print('Fixing Week 9 picks with correct mapping...')
    print('=' * 45)
    
    # Update picks for each game type
    for game_key, pick_list in picks_by_game_type.items():
        # Find the corresponding game in database
        if 'Ravens @ Dolphins' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'Miami Dolphins' AND away_team = 'Baltimore Ravens' AND week = 9")
        elif 'Bears @ Bengals' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'Cincinnati Bengals' AND away_team = 'Chicago Bears' AND week = 9")
        elif 'Vikings @ Lions' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'Detroit Lions' AND away_team = 'Minnesota Vikings' AND week = 9")
        elif 'Panthers @ Packers' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'Green Bay Packers' AND away_team = 'Carolina Panthers' AND week = 9")
        elif 'Chargers @ Titans' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'Tennessee Titans' AND away_team = 'Los Angeles Chargers' AND week = 9")
        elif 'Falcons @ Patriots' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'New England Patriots' AND away_team = 'Atlanta Falcons' AND week = 9")
        elif '49ers @ Giants' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'New York Giants' AND away_team = 'San Francisco 49ers' AND week = 9")
        elif 'Colts @ Steelers' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'Pittsburgh Steelers' AND away_team = 'Indianapolis Colts' AND week = 9")
        elif 'Broncos @ Texans' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'Houston Texans' AND away_team = 'Denver Broncos' AND week = 9")
        elif 'Jaguars @ Raiders' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'Las Vegas Raiders' AND away_team = 'Jacksonville Jaguars' AND week = 9")
        elif 'Saints @ Rams' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'Los Angeles Rams' AND away_team = 'New Orleans Saints' AND week = 9")
        elif 'Chiefs @ Bills' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'Buffalo Bills' AND away_team = 'Kansas City Chiefs' AND week = 9")
        elif 'Seahawks @ Commanders' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'Washington Commanders' AND away_team = 'Seattle Seahawks' AND week = 9")
        elif 'Cardinals @ Cowboys' in game_key:
            cursor.execute("SELECT game_id FROM nfl_games WHERE home_team = 'Dallas Cowboys' AND away_team = 'Arizona Cardinals' AND week = 9")
        
        game_result = cursor.fetchone()
        if game_result:
            game_id = game_result[0]
            print(f'{game_key}:')
            
            for user_idx, username in enumerate(users):
                if username in user_ids:
                    user_id = user_ids[username]
                    pick_text = pick_list[user_idx].lower()
                    selected_team = team_mappings.get(pick_text, pick_text)
                    
                    cursor.execute('''
                        UPDATE user_picks 
                        SET selected_team = ?
                        WHERE user_id = ? AND game_id = ?
                    ''', (selected_team, user_id, game_id))
                    
                    print(f'  {username}: {selected_team}')
    
    conn.commit()
    print('\n✅ All picks updated with correct mapping!')
    
    conn.close()

if __name__ == '__main__':
    fix_week9_picks_correct_mapping()