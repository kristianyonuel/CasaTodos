import sqlite3

# Analyze Week 7 picks based on the provided data
def analyze_week7_picks():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get actual game results first
    cursor.execute("""
        SELECT 
            g.id, g.home_team, g.away_team, g.home_score, g.away_score,
            CASE 
                WHEN g.home_score > g.away_score THEN g.home_team
                ELSE g.away_team 
            END as winner
        FROM nfl_games g
        WHERE g.week = 7 AND g.year = 2025
        ORDER BY g.id
    """)
    
    games = cursor.fetchall()
    
    print("=== WEEK 7 GAME RESULTS ===")
    game_results = {}
    for game_id, home, away, h_score, a_score, winner in games:
        print(f"Game {game_id}: {away} @ {home} = {a_score}-{h_score} (Winner: {winner})")
        game_results[game_id] = {
            'home': home, 'away': away, 
            'home_score': h_score, 'away_score': a_score,
            'winner': winner
        }
    
    print("\n" + "="*80)
    
    # Manual picks data from user input
    players = ['JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 'KRISTIAN', 'FER']
    
    # Picks by game (in order of game IDs)
    picks_data = [
        # Game 259: PIT @ CIN (Winner: CIN)
        ['STEELERS', 'STEELERS', 'STEELERS', 'STEELERS', 'STEELERS', 'STEELERS', 'STEELERS', 'STEELERS', 'STEELERS', 'BENGALS', 'STEELERS', 'STEELERS', 'STEELERS'],
        # Game 245: LAR @ JAX (Winner: LAR)  
        ['Jax', 'Jax', 'Jax', 'Jax', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'X', 'Jax', 'Rams', 'Jax'],
        # Game 246: NO @ CHI (Winner: NO)
        ['Bears', 'Bears', 'Bears', 'Bears', 'Bears', 'Bears', 'Bears', 'Bears', 'Bears', 'Bears', 'Bears', 'Bears', 'Bears'],
        # Game 247: MIA @ CLE (Winner: MIA)
        ['Browns', 'Browns', 'Browns', 'Miami', 'Browns', 'Miami', 'Miami', 'Browns', 'Miami', 'Browns', 'Browns', 'Browns', 'Browns'],
        # Game 248: NE @ TEN (Winner: NE)
        ['Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats'],
        # Game 249: LV @ KC (Winner: KC)
        ['Kc', 'Kc', 'Kc', 'Kc', 'Kc', 'Kc', 'Kc', 'Kc', 'Kc', 'Kc', 'Kc', 'Kc', 'Kc'],
        # Game 250: PHI @ MIN (Winner: MIN)
        ['Minn', 'Minn', 'Eagles', 'Eagles', 'Minn', 'Eagles', 'Eagles', 'Eagles', 'Minn', 'Eagles', 'Eagles', 'Eagles', 'Minn'],
        # Game 251: CAR @ NYJ (Winner: CAR)
        ['Panthers', 'Panthers', 'Panthers', 'Panthers', 'Jets', 'Panthers', 'Panthers', 'Jets', 'Jets', 'Jets', 'Panthers', 'Jets', 'Panthers'],
        # Game 252: NYG @ DEN (Winner: DEN)
        ['Giants', 'Denver', 'Denver', 'Denver', 'Denver', 'Denver', 'Denver', 'Denver', 'Denver', 'Denver', 'Denver', 'Denver', 'Denver'],
        # Game 253: IND @ LAC (Winner: IND)
        ['Chargers', 'Chargers', 'Colts', 'Chargers', 'Colts', 'Chargers', 'Colts', 'Chargers', 'Chargers', 'Colts', 'Chargers', 'Chargers', 'Chargers'],
        # Game 254: WSH @ DAL (Winner: DAL)
        ['Dallas', 'Dallas', 'Dallas', 'Dallas', 'Wash', 'Dallas', 'Wash', 'Wash', 'Wash', 'Dallas', 'Wash', 'Dallas', 'Wash'],
        # Game 255: GB @ ARI (Winner: GB)
        ['Gb', 'Arizona', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Arizona'],
        # Game 256: ATL @ SF (Winner: SF)
        ['49ers', 'Atlanta', '49ers', '49ers', '49ers', '49ers', '49ers', 'Falcons', 'Falcons', '49ers', '49ers', '49ers', 'Falcons'],
        # Game 257: TB @ DET (Winner: DET)
        ['Bucs', 'Lions', 'Lions', 'Lions', 'Bucs', 'Lions', 'Lions', 'Bucs', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions'],
        # Game 258: HOU @ SEA (Winner: HOU)
        ['Seattle', 'Seattle', 'Seattle', 'Seattle', 'Seattle', 'Seattle', 'Seattle', 'Seattle', 'Texans', 'Seattle', 'Seattle', 'Seattle', 'Seattle']
    ]
    
    # Tiebreaker scores provided
    tiebreaker_scores = ['24-10', '24-20', '27-24', '31-17', '26-10', '24-17', '33-19', '28-22', '27-18', '25-20', '34-21', '30-13', '21-14']
    
    # Team name mappings
    team_mapping = {
        'STEELERS': 'PIT', 'BENGALS': 'CIN',
        'Jax': 'JAX', 'Rams': 'LAR', 'X': None,  # X means no pick
        'Bears': 'CHI',
        'Browns': 'CLE', 'Miami': 'MIA',
        'Pats': 'NE',
        'Kc': 'KC',
        'Minn': 'MIN', 'Eagles': 'PHI',
        'Panthers': 'CAR', 'Jets': 'NYJ',
        'Giants': 'NYG', 'Denver': 'DEN',
        'Chargers': 'LAC', 'Colts': 'IND',
        'Dallas': 'DAL', 'Wash': 'WSH',
        'Gb': 'GB', 'Arizona': 'ARI',
        '49ers': 'SF', 'Atlanta': 'ATL', 'Falcons': 'ATL',
        'Bucs': 'TB', 'Lions': 'DET',
        'Seattle': 'SEA', 'Texans': 'HOU'
    }
    
    # Game order (by game ID)
    game_ids = [259, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258]
    
    print("=== PICK ANALYSIS ===")
    player_scores = {}
    
    for p_idx, player in enumerate(players):
        correct = 0
        wrong = 0
        no_pick = 0
        wrong_picks = []
        
        print(f"\n{player}:")
        
        for g_idx, game_id in enumerate(game_ids):
            pick_raw = picks_data[g_idx][p_idx]
            pick_team = team_mapping.get(pick_raw)
            
            if pick_team is None:  # No pick made
                no_pick += 1
                result = "NO PICK"
                wrong_picks.append(f"Game {game_id} (no pick)")
            else:
                actual_winner = game_results[game_id]['winner']
                if pick_team == actual_winner:
                    correct += 1
                    result = "✓"
                else:
                    wrong += 1
                    result = "✗"
                    game_info = game_results[game_id]
                    wrong_picks.append(f"Game {game_id}: {game_info['away']}@{game_info['home']} (picked {pick_team}, winner {actual_winner})")
            
            print(f"  Game {game_id}: {pick_raw} ({pick_team}) - {result}")
        
        total_losses = wrong + no_pick
        print(f"  SUMMARY: {correct} correct, {wrong} wrong, {no_pick} no pick = {total_losses} total losses")
        
        if wrong_picks:
            print(f"  MISSED/WRONG:")
            for miss in wrong_picks:
                print(f"    - {miss}")
        
        player_scores[player] = {
            'correct': correct,
            'wrong': wrong,
            'no_pick': no_pick,
            'total_losses': total_losses,
            'tiebreaker': tiebreaker_scores[p_idx] if p_idx < len(tiebreaker_scores) else '0-0'
        }
    
    print("\n" + "="*80)
    print("=== FINAL STANDINGS (by fewest losses) ===")
    
    # Sort by total losses (ascending), then by correct picks (descending)
    sorted_players = sorted(player_scores.items(), key=lambda x: (x[1]['total_losses'], -x[1]['correct']))
    
    for rank, (player, stats) in enumerate(sorted_players, 1):
        print(f"{rank:2d}. {player:10s} - {stats['correct']:2d} correct, {stats['total_losses']:2d} losses (tiebreaker: {stats['tiebreaker']})")
    
    print("\n" + "="*80)
    print("=== CHECKING RAYMOND AND ROBERT SPECIFICALLY ===")
    
    raymond_stats = player_scores['RAYMOND']
    robert_stats = player_scores['ROBERT']
    
    print(f"RAYMOND: {raymond_stats['correct']} correct, {raymond_stats['total_losses']} total losses")
    print(f"ROBERT:  {robert_stats['correct']} correct, {robert_stats['total_losses']} total losses")
    
    if raymond_stats['total_losses'] == robert_stats['total_losses']:
        print(f"Both have {raymond_stats['total_losses']} losses - TIED!")
        print("Need tiebreaker analysis...")
    
    conn.close()

if __name__ == "__main__":
    analyze_week7_picks()