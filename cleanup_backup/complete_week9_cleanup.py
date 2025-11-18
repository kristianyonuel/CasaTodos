#!/usr/bin/env python3

import sqlite3

def complete_week9_cleanup():
    """Complete cleanup and rebuild of Week 9 with exact user data"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print('🧹 COMPLETE WEEK 9 CLEANUP & REBUILD')
    print('=' * 45)
    
    # User order exactly as provided
    users = ['JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 
             'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 
             'KRISTIAN', 'FER', 'MIKITIN']
    
    # Get user IDs
    user_ids = {}
    for username in users:
        cursor.execute('SELECT id FROM users WHERE UPPER(username) = UPPER(?)', (username,))
        result = cursor.fetchone()
        if result:
            user_ids[username] = result[0]
            print(f'✓ Found user {username} (ID: {result[0]})')
    
    # Game results in order as provided: 31-20 34-31 31-14 31-21 21-16 41-21 28-24 32-27 27-16 28-24 32-24 24-7 35-21 30-26
    game_results = [
        (31, 20),  # ravens vs miami
        (34, 31),  # bears vs bengals 
        (31, 14),  # vikings vs lions
        (31, 21),  # panthers vs packers
        (21, 16),  # chargers vs titans
        (41, 21),  # falcons vs patriots
        (28, 24),  # 49ers vs giants
        (32, 27),  # colts vs steelers
        (27, 16),  # broncos vs texans
        (28, 24),  # jaguars vs raiders
        (32, 24),  # saints vs rams
        (24, 7),   # chiefs vs bills
        (35, 21),  # seahawks vs commanders
        (30, 26)   # cardinals vs cowboys (MNF)
    ]
    
    # Picks data exactly as provided - 14 rows (games) x 14 columns (users)
    picks_raw = [
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
    
    # Team name mappings
    team_map = {
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
    
    # Game matchups in the order of picks
    game_matchups = [
        ('Baltimore Ravens', 'Miami Dolphins'),      # ravens vs miami
        ('Chicago Bears', 'Cincinnati Bengals'),     # bears vs bengals
        ('Minnesota Vikings', 'Detroit Lions'),      # vikings vs lions
        ('Carolina Panthers', 'Green Bay Packers'),  # panthers vs packers
        ('Los Angeles Chargers', 'Tennessee Titans'), # chargers vs titans
        ('Atlanta Falcons', 'New England Patriots'), # falcons vs patriots
        ('San Francisco 49ers', 'New York Giants'),  # 49ers vs giants
        ('Indianapolis Colts', 'Pittsburgh Steelers'), # colts vs steelers
        ('Denver Broncos', 'Houston Texans'),        # broncos vs texans
        ('Jacksonville Jaguars', 'Las Vegas Raiders'), # jaguars vs raiders
        ('New Orleans Saints', 'Los Angeles Rams'),  # saints vs rams
        ('Kansas City Chiefs', 'Buffalo Bills'),     # chiefs vs bills
        ('Seattle Seahawks', 'Washington Commanders'), # seahawks vs commanders
        ('Arizona Cardinals', 'Dallas Cowboys')      # cardinals vs cowboys (MNF)
    ]
    
    print(f'\n📊 Processing {len(game_matchups)} games for {len(users)} users...')
    
    # Update each game
    for game_idx, (away_team, home_team) in enumerate(game_matchups):
        away_score, home_score = game_results[game_idx]
        winner = away_team if away_score > home_score else home_team
        
        print(f'\nGame {game_idx + 1}: {away_team} @ {home_team} ({away_score}-{home_score})')
        print(f'Winner: {winner}')
        
        # Find the game in database
        cursor.execute('''
            SELECT game_id FROM nfl_games 
            WHERE away_team = ? AND home_team = ? AND week = 9
        ''', (away_team, home_team))
        
        game_result = cursor.fetchone()
        if game_result:
            game_id = game_result[0]
            
            # Update game score
            cursor.execute('''
                UPDATE nfl_games 
                SET away_score = ?, home_score = ?, game_status = 'Final', is_final = 1
                WHERE game_id = ?
            ''', (away_score, home_score, game_id))
            
            # Update picks for this game
            game_picks = picks_raw[game_idx]
            for user_idx, username in enumerate(users):
                if username in user_ids:
                    user_id = user_ids[username]
                    pick_text = game_picks[user_idx].lower()
                    selected_team = team_map.get(pick_text, pick_text)
                    is_correct = 1 if selected_team == winner else 0
                    
                    # Update the pick
                    cursor.execute('''
                        UPDATE user_picks 
                        SET selected_team = ?, is_correct = ?
                        WHERE user_id = ? AND game_id = ?
                    ''', (selected_team, is_correct, user_id, game_id))
                    
                    result_symbol = "✅" if is_correct else "❌"
                    print(f'  {username}: {selected_team} {result_symbol}')
            
            if home_team == 'Dallas Cowboys':
                print('  🏈 MONDAY NIGHT FOOTBALL')
    
    conn.commit()
    
    # Generate final leaderboard
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
    
    print(f'\n🏆 FINAL WEEK 9 LEADERBOARD')
    print('=' * 35)
    
    for i, (username, correct) in enumerate(leaderboard, 1):
        print(f'{i:2d}. {username.upper():10s}: {correct:2d}/14')
    
    # Check for ties and specifically highlight the key players
    print(f'\n🎯 KEY PLAYERS ANALYSIS:')
    print('=' * 30)
    
    key_scores = {}
    for username, correct in leaderboard:
        if username.lower() in ['vizca', 'jean', 'rada']:
            key_scores[username.lower()] = correct
            print(f'{username.upper()}: {correct}/14')
    
    # Check Monday Night Football impact
    print(f'\n🏈 MONDAY NIGHT FOOTBALL IMPACT:')
    print('=' * 40)
    
    for username in ['VIZCA', 'JEAN', 'RADA']:
        if username in user_ids:
            user_id = user_ids[username]
            cursor.execute('''
                SELECT up.selected_team, up.is_correct
                FROM user_picks up
                JOIN nfl_games ng ON up.game_id = ng.game_id
                WHERE up.user_id = ? AND ng.home_team = 'Dallas Cowboys' AND ng.week = 9
            ''', (user_id,))
            
            mnf_result = cursor.fetchone()
            if mnf_result:
                mnf_pick, mnf_correct = mnf_result
                status = "WON" if mnf_correct else "LOST"
                print(f'{username}: picked {mnf_pick} - {status}')
    
    print(f'\n✅ Week 9 cleanup complete!')
    conn.close()

if __name__ == '__main__':
    complete_week9_cleanup()