import sqlite3
from datetime import datetime

def update_picks_for_week6():
    """
    Update the database with Week 6 picks for all users.
    This script will clear existing Week 6 picks and insert new ones.
    """
    
    # User mapping (name -> database user_id)
    user_mapping = {
        'JAVIER': 8,
        'VIZCA': 9, 
        'ROBERT': 10,
        'COYOTE': 11,
        'JEAN': 12,
        'RAMFIS': 13,
        'GUILLERMO': 14,
        'JONIEL': 15,
        'RADA': 16,
        'RAYMOND': 17,
        'SHORTY': 18,
        'KRISTIAN': 4,
        'FER': 19
    }
    
    # Raw picks data from user
    users_order = ["JAVIER", "VIZCA", "ROBERT", "COYOTE", "JEAN", "RAMFIS", 
                   "GUILLERMO", "JONIEL", "RADA", "RAYMOND", "SHORTY", "KRISTIAN", "FER"]
    
    # Corrected picks data - aligned with actual Week 6 games
    picks_data = [
        # Game 1: PHI @ NYG
        ["eagles", "eagles", "eagles", "eagles", "eagles", "eagles", "eagles", "eagles", "eagles", "giants", "eagles", "eagles", "eagles"],
        # Game 2: DEN @ NYJ  
        ["Denver", "Denver", "Denver", "Denver", "X", "Denver", "Denver", "Denver", "Denver", "Denver", "Denver", "Denver", "X"],
        # Game 3: LAR @ BAL
        ["Rams", "Rams", "Rams", "Rams", "Rams", "Rams", "Ravens", "Rams", "Rams", "Rams", "Rams", "Rams", "Rams"],
        # Game 4: DAL @ CAR
        ["Dallas", "Dallas", "Dallas", "Dallas", "Dallas", "Dallas", "Panthers", "Dallas", "Dallas", "Dallas", "Dallas", "Dallas", "Dallas"],
        # Game 5: SEA @ JAX (this was row 6 in original - picks show Jax/Seattle)
        ["Jax", "Seattle", "Jax", "Jax", "Jax", "Seattle", "Jax", "Jax", "Jax", "Jax", "Jax", "Seattle", "Jax"],
        # Game 6: ARI @ IND (this was row 5 in original - picks show Colts)
        ["Colts", "Colts", "Colts", "Colts", "Colts", "Colts", "Colts", "Colts", "Colts", "Colts", "Colts", "Colts", "Colts"],
        # Game 7: LAC @ MIA
        ["Chargers", "Miami", "Chargers", "Chargers", "Chargers", "Chargers", "Miami", "Chargers", "Chargers", "Chargers", "Chargers", "Chargers", "Chargers"],
        # Game 8: CLE @ PIT
        ["Pitt", "Pitt", "Pitt", "Pitt", "Pitt", "Pitt", "Pitt", "Pitt", "Pitt", "Pitt", "Pitt", "Pitt", "Pitt"],
        # Game 9: SF @ TB (this was row 12 in original - picks show 49ers/Bucs)
        ["49ers", "Bucs", "Bucs", "Bucs", "X", "Bucs", "49ers", "Bucs", "Bucs", "Bucs", "49ers", "Bucs", "49ers"],
        # Game 10: TEN @ LV
        ["Titans", "Raiders", "Raiders", "Raiders", "Raiders", "Raiders", "Raiders", "Raiders", "Raiders", "Raiders", "Raiders", "Raiders", "Titans"],
        # Game 11: NE @ NO (this was row 9 in original - picks show Pats)
        ["Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats", "Pats"],
        # Game 12: CIN @ GB (this was row 11 in original - picks show Gb)  
        ["Gb", "Gb", "Gb", "Gb", "Gb", "Gb", "Gb", "Gb", "Gb", "Gb", "Gb", "Gb", "Gb"],
        # Game 13: DET @ KC
        ["Lions", "Lions", "Lions", "Kc", "Lions", "Kc", "Lions", "Lions", "Kc", "Lions", "Lions", "Kc", "Kc"],
        # Game 14: BUF @ ATL (Monday Night)
        ["Bills", "Bills", "Bills", "Bills", "Bills", "Bills", "Bills", "Bills", "Bills", "Bills", "Bills", "Bills", "Bills"],
        # Game 15: CHI @ WSH (Monday Night) 
        ["Wash", "Wash", "Bears", "Wash", "Wash", "Wash", "Wash", "Wash", "Wash", "Wash", "Wash", "Wash", "Wash"]
    ]
    
    # Tiebreaker predictions (for Monday Night games)
    tiebreakers = ["20-17", "27-23", "27-21", "27-14", "30-14", "27-17", "24-18", "31-24", "27-15", "27-23", "34-24", "21-13", "21-17"]
    
    # Team name mappings
    team_mappings = {
        'eagles': 'PHI', 'giants': 'NYG', 'denver': 'DEN', 'rams': 'LAR', 'ravens': 'BAL',
        'dallas': 'DAL', 'panthers': 'CAR', 'jax': 'JAX', 'seattle': 'SEA', 'colts': 'IND',
        'chargers': 'LAC', 'miami': 'MIA', 'pitt': 'PIT', 'pats': 'NE', 'titans': 'TEN', 
        'raiders': 'LV', 'gb': 'GB', '49ers': 'SF', 'bucs': 'TB', 'lions': 'DET', 'kc': 'KC',
        'bills': 'BUF', 'wash': 'WSH', 'bears': 'CHI'
    }
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    try:
        # Get Week 6 games
        cursor.execute("""
            SELECT id, home_team, away_team, is_monday_night
            FROM nfl_games 
            WHERE week = 6 AND year = 2025 
            ORDER BY game_date
        """)
        games = cursor.fetchall()
        
        print(f"Found {len(games)} games for Week 6")
        print(f"Have picks for {len(picks_data)} games")
        
        # Clear existing Week 6 picks
        cursor.execute("""
            DELETE FROM user_picks 
            WHERE game_id IN (
                SELECT id FROM nfl_games 
                WHERE week = 6 AND year = 2025
            )
        """)
        
        deleted_picks = cursor.rowcount
        print(f"Deleted {deleted_picks} existing Week 6 picks")
        
        # Insert new picks
        picks_inserted = 0
        
        for game_idx, game in enumerate(games):
            game_id, home_team, away_team, is_monday_night = game
            
            if game_idx >= len(picks_data):
                print(f"Warning: No pick data for game {game_idx + 1}")
                continue
                
            game_picks = picks_data[game_idx]
            
            print(f"\nGame {game_idx + 1}: {away_team} @ {home_team} (ID: {game_id})")
            
            for user_idx, pick in enumerate(game_picks):
                if user_idx >= len(users_order):
                    break
                    
                username = users_order[user_idx]
                user_id = user_mapping.get(username)
                
                if not user_id:
                    print(f"Warning: User {username} not found in database")
                    continue
                
                if pick == 'X':
                    print(f"  {username}: NO PICK")
                    continue
                
                # Convert pick to team code
                team_code = team_mappings.get(pick.lower())
                if not team_code:
                    print(f"Warning: Unknown team '{pick}' for {username}")
                    continue
                
                # Add tiebreaker scores for Monday Night games
                home_score = away_score = None
                if is_monday_night and user_idx < len(tiebreakers):
                    scores = tiebreakers[user_idx].split('-')
                    if len(scores) == 2:
                        try:
                            # Assume format is home-away (need to verify which team is which)
                            home_score = int(scores[0])
                            away_score = int(scores[1])
                        except ValueError:
                            pass
                
                # Insert pick
                cursor.execute("""
                    INSERT INTO user_picks (
                        user_id, game_id, selected_team, predicted_home_score, predicted_away_score,
                        confidence_level, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                """, (user_id, game_id, team_code, home_score, away_score, 
                      datetime.now(), datetime.now()))
                
                picks_inserted += 1
                tiebreaker_info = f" (Tiebreaker: {home_score}-{away_score})" if home_score else ""
                print(f"  {username}: {pick} -> {team_code}{tiebreaker_info}")
        
        conn.commit()
        print(f"\n✅ Successfully inserted {picks_inserted} picks for Week 6")
        
        # Verify the results
        cursor.execute("""
            SELECT COUNT(*) FROM user_picks up
            JOIN nfl_games ng ON up.game_id = ng.id
            WHERE ng.week = 6 AND ng.year = 2025
        """)
        
        total_picks = cursor.fetchone()[0]
        print(f"✅ Total picks in database for Week 6: {total_picks}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== PREVIEW: Week 6 Picks Update ===")
    print("This script will:")
    print("1. Delete all existing Week 6 picks")
    print("2. Insert new picks for all 13 users across 15 games") 
    print("3. Include tiebreaker predictions for Monday Night games")
    print("\nRunning update...")
    
    update_picks_for_week6()