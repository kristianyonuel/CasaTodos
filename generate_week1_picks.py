#!/usr/bin/env python3
"""
Week 1 Picks Recovery Script
Generates SQL INSERT statements to restore all user picks
"""

# User picks data exactly as provided
users_picks = {
    'JAVIER': {
        'picks': ['DAL', 'KC', 'TB', 'CIN', 'IND', 'JAX', 'LV', 'ARI', 'PIT', 'WAS', 'DEN', 'SF', 'DET', 'LAR', 'BAL', 'MIN'],
        'monday': '24–10'
    },
    'VIZCA': {
        'picks': ['PHI', 'LAC', 'ATL', 'CIN', 'MIA', 'JAX', 'NE', 'ARI', 'PIT', 'WAS', 'DEN', 'SF', 'GB', 'LAR', 'BUF', 'MIN'],
        'monday': '24–17'
    },
    'ROBERT': {
        'picks': ['PHI', 'KC', 'TB', 'CIN', 'IND', 'JAX', 'NE', 'ARI', 'PIT', 'WAS', 'DEN', 'SEA', 'GB', 'HOU', 'BAL', 'MIN'],
        'monday': '28–21'
    },
    'COYOTE': {
        'picks': ['PHI', 'KC', 'ATL', 'CIN', 'MIA', 'JAX', 'LV', 'ARI', 'PIT', 'WAS', 'DEN', 'SF', 'GB', 'LAR', 'BUF', 'MIN'],
        'monday': '27–21'
    },
    'JEAN': {
        'picks': ['PHI', 'KC', 'TB', 'CIN', 'MIA', 'CAR', 'NE', 'ARI', 'PIT', 'WAS', 'DEN', 'SF', 'DET', 'LAR', 'BAL', 'CHI'],
        'monday': '24–20'
    },
    'RAMFIS': {
        'picks': ['PHI', 'KC', 'TB', 'CIN', 'MIA', 'JAX', 'NE', 'ARI', 'PIT', 'WAS', 'DEN', 'SF', 'GB', 'LAR', 'BUF', 'CHI'],
        'monday': '22–19'
    },
    'GUILLERMO': {
        'picks': ['PHI', 'KC', 'TB', 'CIN', 'MIA', 'CAR', 'NE', 'ARI', 'PIT', 'WAS', 'DEN', 'SF', 'DET', 'HOU', 'BUF', 'MIN'],
        'monday': '28–10'
    },
    'JONIEL': {
        'picks': ['PHI', 'KC', 'TB', 'CIN', 'MIA', 'JAX', 'NE', 'ARI', 'PIT', 'WAS', 'DEN', 'SF', 'DET', 'LAR', 'BAL', 'CHI'],
        'monday': '26–22'
    },
    'RADA': {
        'picks': ['PHI', 'KC', 'TB', 'CIN', 'MIA', 'JAX', 'NE', 'ARI', 'PIT', 'WAS', 'DEN', 'SF', 'GB', 'LAR', 'BAL', 'CHI'],
        'monday': '20–14'
    },
    'RAYMOND': {
        'picks': ['PHI', 'LAC', 'TB', 'CIN', 'MIA', 'JAX', 'LV', 'ARI', 'PIT', 'WAS', 'DEN', 'SEA', 'GB', 'HOU', 'BUF', 'MIN'],
        'monday': '25–21'
    },
    'SHORTY': {
        'picks': ['PHI', 'LAC', 'ATL', 'CIN', 'MIA', 'JAX', 'NE', 'ARI', 'PIT', 'WAS', 'DEN', 'SEA', 'GB', 'LAR', 'BAL', 'CHI'],
        'monday': '35–24'
    },
    'KRISTIAN': {
        'picks': ['DAL', 'KC', 'TB', 'CIN', 'MIA', 'JAX', 'NE', 'ARI', 'PIT', 'WAS', 'DEN', 'SF', 'GB', 'LAR', 'BAL', 'CHI'],
        'monday': '20–13'
    },
    'FER': {
        'picks': ['DAL', 'KC', 'TB', 'CIN', 'MIA', 'JAX', 'NE', 'NO', 'PIT', 'NYG', 'TEN', 'SEA', 'DET', 'LAR', 'BUF', 'CHI'],
        'monday': '28–24'
    }
}

# Games in order (based on typical NFL Week 1 schedule)
games_order = [
    ('DAL', 'PHI'),  # 1. DAL @ PHI
    ('KC', 'LAC'),   # 2. KC @ LAC
    ('TB', 'ATL'),   # 3. TB @ ATL
    ('CIN', 'CLE'),  # 4. CIN @ CLE
    ('MIA', 'IND'),  # 5. MIA @ IND
    ('CAR', 'JAX'),  # 6. CAR @ JAX
    ('LV', 'NE'),    # 7. LV @ NE
    ('ARI', 'NO'),   # 8. ARI @ NO
    ('PIT', 'NYJ'),  # 9. PIT @ NYJ
    ('NYG', 'WSH'),  # 10. NYG @ WSH (Note: WAS → WSH)
    ('TEN', 'DEN'),  # 11. TEN @ DEN
    ('SF', 'SEA'),   # 12. SF @ SEA
    ('DET', 'GB'),   # 13. DET @ GB
    ('HOU', 'LAR'),  # 14. HOU @ LAR
    ('BAL', 'BUF'),  # 15. BAL @ BUF
    ('MIN', 'CHI')   # 16. MIN @ CHI (Monday Night)
]

def parse_monday_score(score_str):
    """Parse Monday score like '24–10' into home and away scores"""
    if '–' in score_str:
        parts = score_str.split('–')
        return int(parts[0]), int(parts[1])
    return None, None

def generate_sql():
    """Generate SQL INSERT statements"""
    
    print("-- NFL Fantasy Week 1 Picks Recovery Script")
    print("-- Generated automatically from user data")
    print()
    
    # Clear existing picks first
    print("-- Clear any existing Week 1 picks")
    print("DELETE FROM user_picks WHERE game_id IN (")
    print("    SELECT id FROM nfl_games WHERE week = 1 AND year = 2025")
    print(");")
    print()
    
    # Generate INSERT statements for each user
    for username, data in users_picks.items():
        print(f"-- Picks for {username}")
        picks = data['picks']
        monday_score = data['monday']
        
        # Parse Monday Night score
        home_score, away_score = parse_monday_score(monday_score)
        
        for i, (away_team, home_team) in enumerate(games_order):
            pick = picks[i]
            
            # Fix WAS → WSH mapping
            if pick == 'WAS':
                pick = 'WSH'
            if away_team == 'WAS':
                away_team = 'WSH'
            if home_team == 'WAS':
                home_team = 'WSH'
            
            # Check if this is Monday Night game (game 16)
            is_monday = (i == 15)  # Last game is Monday Night
            
            if is_monday and home_score and away_score:
                # Monday Night game with score prediction
                print(f"INSERT INTO user_picks (user_id, game_id, selected_team, predicted_home_score, predicted_away_score, created_at)")
                print(f"SELECT u.id, g.id, '{pick}', {home_score}, {away_score}, datetime('now')")
                print(f"FROM users u, nfl_games g")
                print(f"WHERE LOWER(u.username) = '{username.lower()}' AND g.away_team = '{away_team}' AND g.home_team = '{home_team}' AND g.week = 1 AND g.year = 2025;")
            else:
                # Regular game
                print(f"INSERT INTO user_picks (user_id, game_id, selected_team, created_at)")
                print(f"SELECT u.id, g.id, '{pick}', datetime('now')")
                print(f"FROM users u, nfl_games g")
                print(f"WHERE LOWER(u.username) = '{username.lower()}' AND g.away_team = '{away_team}' AND g.home_team = '{home_team}' AND g.week = 1 AND g.year = 2025;")
        
        print()

if __name__ == "__main__":
    generate_sql()
