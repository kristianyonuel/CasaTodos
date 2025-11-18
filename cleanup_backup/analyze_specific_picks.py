#!/usr/bin/env python3

def analyze_specific_picks():
    """Analyze VIZCA, JEAN, and RADA picks specifically"""
    
    print('🔍 DETAILED PICK ANALYSIS')
    print('=' * 40)
    
    # User order as provided
    users = ['JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 
             'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 
             'KRISTIAN', 'FER', 'MIKITIN']
    
    # Find positions
    vizca_pos = users.index('VIZCA')  # Position 1 (0-indexed)
    jean_pos = users.index('JEAN')    # Position 4 (0-indexed)
    rada_pos = users.index('RADA')    # Position 8 (0-indexed)
    
    print(f'VIZCA position: {vizca_pos} (column {vizca_pos + 1})')
    print(f'JEAN position: {jean_pos} (column {jean_pos + 1})')  
    print(f'RADA position: {rada_pos} (column {rada_pos + 1})')
    
    # Picks data exactly as provided
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
    
    # Game results
    game_results = ['W', 'W', 'L', 'L', 'W', 'L', 'W', 'W', 'W', 'W', 'L', 'W', 'W', 'W']
    actual_winners = ['ravens', 'Bears', 'Minn', 'Panthers', 'Chargers', 'Falcons', '49ers', 'Colts', 'Denver', 'Jax', 'Saints', 'Kc', 'Seattle', 'Arizona']
    
    # Game names for clarity
    game_names = [
        'Ravens @ Dolphins (31-20)',
        'Bears @ Bengals (34-31)', 
        'Vikings @ Lions (31-14)',
        'Panthers @ Packers (31-21)',
        'Chargers @ Titans (21-16)',
        'Falcons @ Patriots (41-21)',
        '49ers @ Giants (28-24)',
        'Colts @ Steelers (32-27)',
        'Broncos @ Texans (27-16)',
        'Jaguars @ Raiders (28-24)',
        'Saints @ Rams (32-24)',
        'Chiefs @ Bills (24-7)',
        'Seahawks @ Commanders (35-21)',
        'Cardinals @ Cowboys (30-26)'
    ]
    
    print('\n📊 PICK-BY-PICK ANALYSIS:')
    print('=' * 50)
    
    # Analyze each user
    for name, pos in [('VIZCA', vizca_pos), ('JEAN', jean_pos), ('RADA', rada_pos)]:
        print(f'\n{name} (Column {pos + 1}):')
        print('-' * 25)
        
        correct_count = 0
        wrong_picks = []
        
        for game_idx, game_name in enumerate(game_names):
            user_pick = picks_raw[game_idx][pos].lower()
            winner = actual_winners[game_idx].lower()
            
            # Normalize team names for comparison
            if user_pick in ['minn', 'minnesota']:
                user_pick = 'minn'
            if user_pick in ['gb', 'packers']:
                user_pick = 'gb'
            if user_pick in ['kc', 'chiefs']:
                user_pick = 'kc'
            if user_pick in ['pitt', 'pit']:
                user_pick = 'pit'
            if user_pick in ['den', 'denver']:
                user_pick = 'denver'
                
            if winner in ['minn', 'minnesota']:
                winner = 'minn'
            if winner == 'panthers':
                winner = 'gb'  # Panthers beat Packers, so if picked GB = wrong
            if winner == 'kc':
                winner = 'kc'
            
            # Special case analysis
            is_correct = False
            if game_idx == 0:  # Ravens vs Dolphins
                is_correct = user_pick in ['ravens', 'baltimore']
            elif game_idx == 1:  # Bears vs Bengals  
                is_correct = user_pick in ['bears', 'chicago']
            elif game_idx == 2:  # Vikings vs Lions
                is_correct = user_pick in ['minn', 'minnesota', 'vikings']
            elif game_idx == 3:  # Panthers vs Packers
                is_correct = user_pick in ['panthers', 'carolina'] # Panthers won
            elif game_idx == 4:  # Chargers vs Titans
                is_correct = user_pick in ['chargers', 'los angeles chargers']
            elif game_idx == 5:  # Falcons vs Patriots
                is_correct = user_pick in ['falcons', 'atlanta']
            elif game_idx == 6:  # 49ers vs Giants
                is_correct = user_pick in ['49ers', 'san francisco']
            elif game_idx == 7:  # Colts vs Steelers
                is_correct = user_pick in ['colts', 'indianapolis']
            elif game_idx == 8:  # Broncos vs Texans
                is_correct = user_pick in ['denver', 'broncos']
            elif game_idx == 9:  # Jaguars vs Raiders
                is_correct = user_pick in ['jax', 'jaguars', 'jacksonville']
            elif game_idx == 10:  # Saints vs Rams
                is_correct = user_pick in ['saints', 'new orleans']
            elif game_idx == 11:  # Chiefs vs Bills
                is_correct = user_pick in ['kc', 'chiefs', 'kansas city']
            elif game_idx == 12:  # Seahawks vs Commanders
                is_correct = user_pick in ['seattle', 'seahawks']
            elif game_idx == 13:  # Cardinals vs Cowboys
                is_correct = user_pick in ['arizona', 'cardinals']
            
            if is_correct:
                correct_count += 1
                status = '✅'
            else:
                status = '❌'
                wrong_picks.append(f"Game {game_idx + 1}")
            
            print(f'  {game_idx + 1:2d}. {game_name:<30} | Picked: {user_pick:<8} | {status}')
        
        print(f'\n  TOTAL: {correct_count}/14')
        if wrong_picks:
            print(f'  WRONG: {", ".join(wrong_picks)}')
    
    print(f'\n🎯 SUMMARY:')
    print('Based on your statement:')
    print('- VIZCA lost: Colts, Lions, GB, Texans (games 8, 3, 4, 9)')  
    print('- JEAN lost: Lions, GB, Colts, KC (games 3, 4, 8, 12)')
    print('- RADA lost: Lions, GB, Giants, Texans (games 3, 4, 7, 9)')

if __name__ == '__main__':
    analyze_specific_picks()