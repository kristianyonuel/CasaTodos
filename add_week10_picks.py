#!/usr/bin/env python3
"""
Add Week 10 picks for all users
"""

import sqlite3
from datetime import datetime

def add_week10_picks():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # User mapping by order in the data
    users_order = [
        ('javier', 8), ('vizca', 9), ('robert', 10), ('coyote', 11), 
        ('jean', 12), ('ramfis', 13), ('guillermo', 14), ('joniel', 15), 
        ('rada', 16), ('raymond', 17), ('shorty', 18), ('kristian', 4), 
        ('fer', 19), ('mikitin', 24)
    ]
    
    # Game mapping (database ID: [game_description, home_team, away_team])
    games = {
        381: ('Raiders @ Broncos', 'Denver Broncos', 'Las Vegas Raiders'),
        382: ('Falcons @ Colts', 'Indianapolis Colts', 'Atlanta Falcons'), 
        385: ('Giants @ Bears', 'Chicago Bears', 'New York Giants'),
        383: ('Bills @ Dolphins', 'Miami Dolphins', 'Buffalo Bills'),
        389: ('Ravens @ Vikings', 'Minnesota Vikings', 'Baltimore Ravens'),
        388: ('Browns @ Jets', 'New York Jets', 'Cleveland Browns'),
        387: ('Patriots @ Bucs', 'Tampa Bay Buccaneers', 'New England Patriots'),
        386: ('Saints @ Panthers', 'Carolina Panthers', 'New Orleans Saints'),
        384: ('Jaguars @ Texans', 'Houston Texans', 'Jacksonville Jaguars'),
        390: ('Cardinals @ Seahawks', 'Seattle Seahawks', 'Arizona Cardinals'),
        391: ('Rams @ 49ers', 'San Francisco 49ers', 'Los Angeles Rams'),
        392: ('Lions @ Commanders', 'Washington Commanders', 'Detroit Lions'),
        393: ('Steelers @ Chargers', 'Los Angeles Chargers', 'Pittsburgh Steelers'),
        394: ('Eagles @ Packers', 'Green Bay Packers', 'Philadelphia Eagles')
    }
    
    # Picks data (each row is one user's picks for all games)
    picks_data = [
        # javier, vizca, robert, coyote, jean, ramfis, guillermo, joniel, rada, raymond, shorty, kristian, fer, mikitin
        ['denver', 'denver', 'denver', 'denver', 'denver', 'denver', 'denver', 'denver', 'denver', 'denver', 'denver', 'denver', 'denver', 'denver'],
        ['colts', 'colts', 'colts', 'colts', 'colts', 'colts', 'colts', 'colts', 'colts', 'colts', 'colts', 'colts', 'colts', ''],
        ['bears', 'bears', 'bears', 'bears', 'bears', 'giants', 'giants', 'bears', 'giants', 'bears', 'bears', 'bears', 'bears', 'bears'],
        ['bills', 'bills', 'bills', 'bills', 'bills', 'bills', 'bills', 'bills', 'bills', 'bills', 'bills', 'bills', 'bills', 'bills'],
        ['ravens', 'ravens', 'ravens', 'minn', 'minn', 'ravens', 'minn', 'ravens', 'ravens', 'minn', 'minn', 'ravens', 'ravens', 'ravens'],
        ['browns', 'jets', 'jets', 'browns', 'jets', 'jets', 'browns', 'browns', 'jets', 'jets', 'jets', 'browns', 'jets', 'jets'],
        ['bucs', 'bucs', 'bucs', 'bucs', 'bucs', 'bucs', 'pats', 'pats', 'bucs', 'bucs', 'pats', 'pats', 'pats', 'pats'],
        ['panthers', 'panthers', 'panthers', 'panthers', 'panthers', 'panthers', 'saints', 'panthers', 'panthers', 'panthers', 'panthers', 'panthers', 'panthers', 'panthers'],
        ['texans', 'texans', 'texans', 'jax', 'jax', 'jax', 'texans', 'jax', 'jax', 'jax', 'jax', 'jax', 'jax', 'jax'],
        ['seattle', 'seattle', 'seattle', 'seattle', 'seattle', 'seattle', 'arizona', 'seattle', 'seattle', 'seattle', 'seattle', 'seattle', 'seattle', 'seattle'],
        ['rams', 'rams', 'rams', 'rams', 'rams', 'rams', 'rams', 'rams', 'rams', 'rams', 'rams', '49ers', 'rams', 'rams'],
        ['lions', 'lions', 'lions', 'lions', 'lions', 'lions', 'lions', 'lions', 'lions', 'lions', 'lions', 'lions', 'lions', 'lions'],
        ['chargers', 'steelers', 'chargers', 'steelers', 'steelers', 'chargers', 'steelers', 'chargers', 'steelers', 'steelers', 'chargers', 'chagers', 'chargers', 'steelers'],
        ['gb', 'eagles', 'eagles', 'eagles', 'eagles', 'eagles', 'eagles', 'gb', 'eagles', 'eagles', 'eagles', 'gb', 'gb', 'eagles']
    ]
    
    # Tiebreaker scores
    tiebreaker_scores = [
        '24-20', '24-23', '28-17', '32-15', '32-24', '30-24', '20-14', 
        '26-22', '26-20', '30-27', '34-21', '22-7', '24-21', '30-15'
    ]
    
    # Team name mapping
    team_map = {
        'denver': 'Denver Broncos',
        'colts': 'Indianapolis Colts',
        'bears': 'Chicago Bears',
        'giants': 'New York Giants', 
        'bills': 'Buffalo Bills',
        'ravens': 'Baltimore Ravens',
        'minn': 'Minnesota Vikings',
        'browns': 'Cleveland Browns',
        'jets': 'New York Jets',
        'bucs': 'Tampa Bay Buccaneers',
        'pats': 'New England Patriots',
        'panthers': 'Carolina Panthers',
        'saints': 'New Orleans Saints',
        'texans': 'Houston Texans',
        'jax': 'Jacksonville Jaguars',
        'seattle': 'Seattle Seahawks',
        'arizona': 'Arizona Cardinals',
        'rams': 'Los Angeles Rams',
        '49ers': 'San Francisco 49ers',
        'lions': 'Detroit Lions',
        'chargers': 'Los Angeles Chargers',
        'chagers': 'Los Angeles Chargers',  # Handle typo
        'steelers': 'Pittsburgh Steelers',
        'gb': 'Green Bay Packers',
        'eagles': 'Philadelphia Eagles'
    }
    
    game_ids = [381, 382, 385, 383, 389, 388, 387, 386, 384, 390, 391, 392, 393, 394]
    
    print("Adding Week 10 picks for all users...")
    
    # Process each user
    for user_idx, (username, user_id) in enumerate(users_order):
        print(f"\nProcessing {username} (ID: {user_id})...")
        
        # Process each game for this user
        for game_idx, game_id in enumerate(game_ids):
            pick_text = picks_data[game_idx][user_idx]
            
            if pick_text == '':  # Empty pick
                print(f"  Game {game_id}: No pick (marked as loss)")
                continue
                
            selected_team = team_map.get(pick_text.lower())
            if not selected_team:
                print(f"  Game {game_id}: Unknown team '{pick_text}' - skipping")
                continue
                
            # Check if pick exists
            cursor.execute('SELECT id FROM user_picks WHERE user_id = ? AND game_id = ?', 
                          (user_id, game_id))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing pick
                cursor.execute('''UPDATE user_picks 
                                 SET selected_team = ?, updated_at = ? 
                                 WHERE user_id = ? AND game_id = ?''',
                              (selected_team, datetime.now(), user_id, game_id))
                print(f"  Game {game_id}: Updated to {selected_team}")
            else:
                # Insert new pick
                cursor.execute('''INSERT INTO user_picks 
                                 (user_id, game_id, selected_team, created_at, updated_at)
                                 VALUES (?, ?, ?, ?, ?)''',
                              (user_id, game_id, selected_team, datetime.now(), datetime.now()))
                print(f"  Game {game_id}: Added {selected_team}")
        
        # Add tiebreaker score for MNF game (game 394)
        if user_idx < len(tiebreaker_scores) and tiebreaker_scores[user_idx]:
            score = tiebreaker_scores[user_idx]
            home_score, away_score = score.split('-')
            
            cursor.execute('''UPDATE user_picks 
                             SET predicted_home_score = ?, predicted_away_score = ?
                             WHERE user_id = ? AND game_id = 394''',
                          (int(home_score), int(away_score), user_id))
            print(f"  Tiebreaker: {score}")
    
    conn.commit()
    print(f"\n✅ Successfully added/updated all Week 10 picks!")
    
    # Summary
    cursor.execute('SELECT COUNT(*) FROM user_picks WHERE game_id IN (381,382,383,384,385,386,387,388,389,390,391,392,393,394)')
    total_picks = cursor.fetchone()[0]
    print(f"📊 Total picks in database for Week 10: {total_picks}")
    
    conn.close()

if __name__ == "__main__":
    add_week10_picks()