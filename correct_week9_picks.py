#!/usr/bin/env python3
"""
Correct Week 9 picks based on actual user data provided
"""

import sqlite3

def parse_and_correct_week9_picks():
    """Parse the actual user picks and correct the database"""
    print("=" * 70)
    print("CORRECTING WEEK 9 PICKS WITH ACTUAL USER DATA")
    print("=" * 70)
    
    # Parse the user data provided
    users = ['JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 'GUILLERMO', 
             'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 'KRISTIAN', 'FER', 'MIKITIN']
    
    # Raw picks data from user (14 games per user)
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
    
    # Team name mapping to full names
    team_mapping = {
        'ravens': 'Baltimore Ravens',
        'miami': 'Miami Dolphins',
        'Miami': 'Miami Dolphins',
        'Bengals': 'Cincinnati Bengals',
        'Bears': 'Chicago Bears',
        'Lions': 'Detroit Lions',
        'Minn': 'Minnesota Vikings',
        'Gb': 'Green Bay Packers',
        'Chargers': 'Los Angeles Chargers',
        'Pats': 'New England Patriots',
        '49ers': 'San Francisco 49ers',
        'Giants': 'New York Giants',
        'Colts': 'Indianapolis Colts',
        'Pit': 'Pittsburgh Steelers',
        'Pitt': 'Pittsburgh Steelers',
        'Denver': 'Denver Broncos',
        'Den': 'Denver Broncos',
        'Texans': 'Houston Texans',
        'Jax': 'Jacksonville Jaguars',
        'Raiders': 'Las Vegas Raiders',
        'Rams': 'Los Angeles Rams',
        'Bills': 'Buffalo Bills',
        'Kc': 'Kansas City Chiefs',
        'Wash': 'Washington Commanders',
        'Seattle': 'Seattle Seahawks',
        'Dallas': 'Dallas Cowboys',
        'Arizona': 'Arizona Cardinals'
    }
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get Week 9 games in order
    cursor.execute("""
        SELECT id, away_team, home_team 
        FROM nfl_games 
        WHERE week = 9 AND year = 2025
        ORDER BY game_date
    """)
    games = cursor.fetchall()
    
    print(f"Found {len(games)} Week 9 games:")
    for i, game in enumerate(games):
        print(f"  Game {i+1} (ID {game[0]}): {game[1]} @ {game[2]}")
    
    # Get user mappings
    user_mappings = {}
    for user in users:
        cursor.execute("SELECT id FROM users WHERE username = ?", (user.lower(),))
        result = cursor.fetchone()
        if result:
            user_mappings[user] = result[0]
            print(f"User {user.lower()}: ID {result[0]}")
        else:
            print(f"❌ User {user.lower()} not found!")
    
    print(f"\n📝 Updating picks for {len(user_mappings)} users...")
    
    total_updates = 0
    
    # Update picks for each user
    for user_idx, username in enumerate(users):
        if username not in user_mappings:
            continue
            
        user_id = user_mappings[username]
        print(f"\n{username.lower()}:")
        
        # Update each game pick for this user
        for game_idx in range(14):  # 14 games
            if game_idx >= len(games):
                break
                
            game_id = games[game_idx][0]
            raw_pick = picks_data[game_idx][user_idx]
            
            # Convert to full team name
            if raw_pick in team_mapping:
                selected_team = team_mapping[raw_pick]
            else:
                print(f"  ❌ Unknown team: {raw_pick}")
                continue
            
            # Update the pick in database
            cursor.execute("""
                UPDATE user_picks 
                SET selected_team = ?, is_correct = 0, points_earned = 0
                WHERE user_id = ? AND game_id = ?
            """, (selected_team, user_id, game_id))
            
            if cursor.rowcount > 0:
                print(f"  ✅ Game {game_idx+1}: {raw_pick} -> {selected_team}")
                total_updates += 1
            else:
                print(f"  ❌ Failed to update Game {game_idx+1}: {raw_pick}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"\n" + "=" * 50)
    print("PICK CORRECTION COMPLETE")
    print("=" * 50)
    print(f"✅ Updated {total_updates} picks total")
    print("🔄 Need to recalculate scoring...")

def recalculate_corrected_scoring():
    """Recalculate scoring with corrected picks"""
    print("\n" + "=" * 70)
    print("RECALCULATING WEEK 9 SCORING WITH CORRECTED PICKS")
    print("=" * 70)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get all final games with results
    cursor.execute("""
        SELECT 
            id,
            away_team,
            home_team,
            away_score,
            home_score
        FROM nfl_games 
        WHERE week = 9 AND year = 2025 AND is_final = 1 
        AND away_score IS NOT NULL AND home_score IS NOT NULL
        ORDER BY game_date
    """)
    
    final_games = cursor.fetchall()
    print(f"\nRecalculating scoring for {len(final_games)} games...")
    
    for game in final_games:
        game_id = game[0]
        away_team = game[1] 
        home_team = game[2]
        away_score = game[3]
        home_score = game[4]
        
        # Determine winner
        if away_score > home_score:
            winning_team = away_team
        elif home_score > away_score:
            winning_team = home_team
        else:
            winning_team = None  # Tie
        
        if winning_team:
            # Update all picks for this game
            cursor.execute("""
                UPDATE user_picks 
                SET is_correct = (CASE WHEN selected_team = ? THEN 1 ELSE 0 END),
                    points_earned = (CASE WHEN selected_team = ? THEN 1 ELSE 0 END)
                WHERE game_id = ?
            """, (winning_team, winning_team, game_id))
            
            print(f"✅ Game {game_id}: {away_team} {away_score}-{home_score} {home_team} (Winner: {winning_team})")
    
    # Commit changes
    conn.commit()
    
    # Show corrected leaderboard
    print(f"\n" + "=" * 50)
    print("CORRECTED WEEK 9 LEADERBOARD")
    print("=" * 50)
    
    cursor.execute("""
        SELECT 
            u.username,
            SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
            SUM(CASE WHEN up.is_correct = 0 THEN 1 ELSE 0 END) as wrong_picks,
            COUNT(up.id) as total_picks
        FROM users u
        JOIN user_picks up ON u.id = up.user_id
        JOIN nfl_games g ON up.game_id = g.id
        WHERE g.week = 9 AND g.year = 2025 AND NOT u.is_admin
        GROUP BY u.id, u.username
        ORDER BY correct_picks DESC, wrong_picks ASC, u.username
    """)
    
    leaderboard = cursor.fetchall()
    
    rank = 1
    for user in leaderboard:
        win_pct = (user[1] / user[3] * 100) if user[3] > 0 else 0
        print(f"{rank:2}. {user[0]:12}: {user[1]:2}/{user[3]:2} correct ({win_pct:5.1f}%)")
        rank += 1
    
    conn.close()
    print("🎯 Corrected scoring calculation complete!")

if __name__ == "__main__":
    parse_and_correct_week9_picks()
    recalculate_corrected_scoring()