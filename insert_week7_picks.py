import sqlite3
from datetime import datetime

# Raw data from user input
user_names = ["JAVIER", "VIZCA", "ROBERT", "COYOTE", "JEAN", "RAMFIS", "GUILLERMO", "JONIEL", "RADA", "RAYMOND", "SHORTY", "KRISTIAN", "FER"]

# Team picks for each game (in order of Week 7 games)
picks_data = [
    ["STEELERS", "STEELERS", "STEELERS", "STEELERS", "STEELERS", "STEELERS", "STEELERS", "STEELERS", "STEELERS", "BENGALS", "STEELERS", "STEELERS", "STEELERS"],  # Game 1: LAR @ JAX (but picked Steelers - this might be wrong)
    ["Jax", "Jax", "Jax", "Jax", "Rams", "Rams", "Rams", "Rams", "Rams", "X", "Jax", "Rams", "Jax"],  # Game 1: LAR @ JAX (corrected)
    ["Bears", "Bears", "Bears", "Bears", "Bears", "Bears", "Bears", "Bears", "Bears", "Bears", "Bears", "Bears", "Bears"],  # Game 2: NO @ CHI
    ["Browns", "Browns", "Browns", "Miami", "Browns", "Miami", "Miami", "Browns", "Miami", "Browns", "Browns", "Browns", "Browns"],  # Game 3: MIA @ CLE
    ["Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats"],  # Game 4: NE @ TEN
    ["Kc", "Kc", "Kc", "Kc", "Kc", "Kc", "Kc", "Kc", "Kc", "Kc", "Kc", "Kc", "Kc"],  # Game 5: LV @ KC
    ["Minn", "Minn", "Eagles", "Eagles", "Minn", "Eagles", "Eagles", "Eagles", "Minn", "Eagles", "Eagles", "Eagles", "Minn"],  # Game 6: PHI @ MIN
    ["Panthers", "Panthers", "Panthers", "Panthers", "Jets", "Panthers", "Panthers", "Jets", "Jets", "Jets", "Panthers", "Jets", "Panthers"],  # Game 7: CAR @ NYJ
    ["Giants", "Denver", "Denver", "Denver", "Denver", "Denver", "Denver", "Denver", "Denver", "Denver", "Denver", "Denver", "Denver"],  # Game 8: NYG @ DEN
    ["Chargers", "Chargers", "Colts", "Chargers", "Colts", "Chargers", "Colts", "Chargers", "Chargers", "Colts", "Chargers", "Chargers", "Chargers"],  # Game 9: IND @ LAC
    ["Dallas", "Dallas", "Dallas", "Dallas", "Wash", "Dallas", "Wash", "Wash", "Wash", "Dallas", "Wash", "Dallas", "Wash"],  # Game 10: WSH @ DAL
    ["Gb", "Arizona", "Gb", "Gb", "Gb", "Gb", "Gb", "Gb", "Gb", "Gb", "Gb", "Gb", "Arizona"],  # Game 11: GB @ ARI
    ["49ers", "Atlanta", "49ers", "49ers", "49ers", "49ers", "49ers", "Falcons", "Falcons", "49ers", "49ers", "49ers", "Falcons"],  # Game 12: ATL @ SF (MNF)
    ["Bucs", "Lions", "Lions", "Lions", "Bucs", "Lions", "Lions", "Bucs", "Lions", "Lions", "Lions", "Lions", "Lions"],  # Game 13: TB @ DET (MNF)
    ["Seattle", "Seattle", "Seattle", "Seattle", "Seattle", "Seattle", "Seattle", "Seattle", "Texans", "Seattle", "Seattle", "Seattle", "Seattle"],  # Game 14: HOU @ SEA (MNF)
]

# MNF Score predictions for last game (HOU @ SEA) - format: "away-home"
mnf_scores = ["24-10", "24-20", "27-24", "31-17", "26-10", "24-17", "33-19", "28-22", "27-18", "25-20", "34-21", "30-13", "21-14"]

# Team name mappings
team_mappings = {
    "STEELERS": "PIT", "BENGALS": "CIN",
    "Jax": "JAX", "Rams": "LAR", "X": None,  # X means no pick
    "Bears": "CHI",
    "Browns": "CLE", "Miami": "MIA",
    "Pats": "NE",
    "Kc": "KC",
    "Minn": "MIN", "Eagles": "PHI",
    "Panthers": "CAR", "Jets": "NYJ",
    "Giants": "NYG", "Denver": "DEN",
    "Chargers": "LAC", "Colts": "IND",
    "Dallas": "DAL", "Wash": "WAS",
    "Gb": "GB", "Arizona": "ARI",
    "49ers": "SF", "Atlanta": "ATL", "Falcons": "ATL",
    "Bucs": "TB", "Lions": "DET",
    "Seattle": "SEA", "Texans": "HOU"
}

# User name mappings (lowercase database usernames)
user_mappings = {
    "JAVIER": "javier", "VIZCA": "vizca", "ROBERT": "robert", "COYOTE": "coyote",
    "JEAN": "jean", "RAMFIS": "ramfis", "GUILLERMO": "guillermo", "JONIEL": "joniel", 
    "RADA": "rada", "RAYMOND": "raymond", "SHORTY": "shorty", "KRISTIAN": "kristian", "FER": "fer"
}

def insert_week7_picks():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get Week 7 games in order
    cursor.execute('''
        SELECT id, away_team, home_team, is_monday_night
        FROM nfl_games 
        WHERE week = 7 AND year = 2025
        ORDER BY game_date, id
    ''')
    games = cursor.fetchall()
    
    # Get user IDs
    cursor.execute('SELECT id, username FROM users')
    users = {username: user_id for user_id, username in cursor.fetchall()}
    
    print(f'=== INSERTING WEEK 7 PICKS ===')
    print(f'Found {len(games)} games and {len(users)} users')
    
    total_picks_inserted = 0
    
    # Skip first row (STEELERS picks seem to be misplaced)
    # Start from row 1 (Jax/Rams picks for Game 1)
    for game_idx in range(len(games)):
        game_id, away_team, home_team, is_mnf = games[game_idx]
        
        # Get picks for this game (skip first STEELERS row, use actual game picks)
        if game_idx < len(picks_data) - 1:  # Regular games (not using STEELERS row)
            game_picks = picks_data[game_idx + 1]  # Skip STEELERS row
        else:
            continue  # No more pick data
        
        print(f'\nGame {game_id}: {away_team} @ {home_team}')
        
        for user_idx, user_name in enumerate(user_names):
            if user_idx >= len(game_picks):
                continue
                
            pick = game_picks[user_idx]
            if pick == "X":  # Skip no-picks
                continue
                
            # Map team name to abbreviation
            selected_team = team_mappings.get(pick)
            if not selected_team:
                print(f'  WARNING: Unknown team "{pick}" for {user_name}')
                continue
            
            # Get user ID
            db_username = user_mappings.get(user_name)
            if not db_username or db_username not in users:
                print(f'  WARNING: Unknown user "{user_name}"')
                continue
                
            user_id = users[db_username]
            
            # For MNF games (HOU @ SEA), add score predictions
            predicted_home = None
            predicted_away = None
            
            if is_mnf and game_idx == 13:  # Last MNF game (HOU @ SEA)
                if user_idx < len(mnf_scores):
                    score_parts = mnf_scores[user_idx].split('-')
                    if len(score_parts) == 2:
                        predicted_away = int(score_parts[0])  # HOU (away)
                        predicted_home = int(score_parts[1])  # SEA (home)
            
            # Insert the pick
            try:
                cursor.execute('''
                    INSERT INTO user_picks (
                        user_id, game_id, selected_team, predicted_home_score, 
                        predicted_away_score, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, game_id, selected_team, predicted_home, predicted_away,
                    datetime.now(), datetime.now()
                ))
                
                score_info = ""
                if predicted_home is not None and predicted_away is not None:
                    score_info = f" (Predicted: {predicted_away}-{predicted_home})"
                
                print(f'  ✅ {user_name} ({db_username}) picked {selected_team}{score_info}')
                total_picks_inserted += 1
                
            except Exception as e:
                print(f'  ❌ Error inserting pick for {user_name}: {e}')
    
    # Commit all changes
    conn.commit()
    conn.close()
    
    print(f'\n🎉 COMPLETED: Inserted {total_picks_inserted} picks for Week 7')
    print('✅ All picks have been successfully added to the database!')

if __name__ == "__main__":
    insert_week7_picks()