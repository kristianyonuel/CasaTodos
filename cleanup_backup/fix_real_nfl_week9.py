#!/usr/bin/env python3
"""
Fix Week 9 picks using REAL NFL games and scores
The user provided the actual game results with real scores
"""

import sqlite3

def fix_real_week9():
    """Fix Week 9 with real NFL games and your provided picks"""
    
    print("🏈 FIXING WEEK 9 WITH REAL NFL GAMES & SCORES")
    print("=" * 55)
    
    # Real NFL Week 9 games with your provided scores
    real_games = [
        # Game, Away Team, Home Team, Away Score, Home Score, Winner
        ("Ravens @ Dolphins", "Baltimore Ravens", "Miami Dolphins", 31, 20, "Baltimore Ravens"),
        ("Bears @ Bengals", "Chicago Bears", "Cincinnati Bengals", 34, 31, "Chicago Bears"),  
        ("Vikings @ Lions", "Minnesota Vikings", "Detroit Lions", 31, 14, "Minnesota Vikings"),
        ("Panthers @ Packers", "Carolina Panthers", "Green Bay Packers", 31, 21, "Carolina Panthers"),
        ("Chargers @ Titans", "Los Angeles Chargers", "Tennessee Titans", 21, 16, "Los Angeles Chargers"),
        ("Falcons @ Patriots", "Atlanta Falcons", "New England Patriots", 41, 21, "Atlanta Falcons"),
        ("49ers @ Giants", "San Francisco 49ers", "New York Giants", 28, 24, "San Francisco 49ers"),
        ("Colts @ Steelers", "Indianapolis Colts", "Pittsburgh Steelers", 32, 27, "Indianapolis Colts"),
        ("Broncos @ Texans", "Denver Broncos", "Houston Texans", 27, 16, "Denver Broncos"),
        ("Jaguars @ Raiders", "Jacksonville Jaguars", "Las Vegas Raiders", 28, 24, "Jacksonville Jaguars"),
        ("Saints @ Rams", "New Orleans Saints", "Los Angeles Rams", 32, 24, "New Orleans Saints"),
        ("Chiefs @ Bills", "Kansas City Chiefs", "Buffalo Bills", 24, 7, "Kansas City Chiefs"),
        ("Seahawks @ Commanders", "Seattle Seahawks", "Washington Commanders", 35, 21, "Seattle Seahawks"),
        ("Cardinals @ Cowboys", "Arizona Cardinals", "Dallas Cowboys", 30, 26, "Arizona Cardinals")
    ]
    
    # User picks from your data
    users = ['JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 'KRISTIAN', 'FER', 'MIKITIN']
    
    user_picks = [
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
        'ravens': 'Baltimore Ravens', 'miami': 'Miami Dolphins', 'Miami': 'Miami Dolphins',
        'Bengals': 'Cincinnati Bengals', 'Bears': 'Chicago Bears',
        'Lions': 'Detroit Lions', 'Minn': 'Minnesota Vikings',
        'Gb': 'Green Bay Packers',
        'Chargers': 'Los Angeles Chargers',
        'Pats': 'New England Patriots',
        '49ers': 'San Francisco 49ers', 'Giants': 'New York Giants',
        'Colts': 'Indianapolis Colts', 'Pit': 'Pittsburgh Steelers', 'Pitt': 'Pittsburgh Steelers',
        'Denver': 'Denver Broncos', 'Den': 'Denver Broncos', 'Texans': 'Houston Texans',
        'Jax': 'Jacksonville Jaguars', 'Raiders': 'Las Vegas Raiders',
        'Rams': 'Los Angeles Rams',
        'Bills': 'Buffalo Bills', 'Kc': 'Kansas City Chiefs',
        'Wash': 'Washington Commanders', 'Seattle': 'Seattle Seahawks',
        'Dallas': 'Dallas Cowboys', 'Arizona': 'Arizona Cardinals'
    }
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🗑️ CLEARING EXISTING WEEK 9 DATA...")
    cursor.execute("DELETE FROM nfl_games WHERE week = 9")
    cursor.execute("DELETE FROM user_picks WHERE game_id LIKE '%w9%'")
    
    print("🏈 CREATING REAL NFL WEEK 9 GAMES...")
    game_ids = []
    for i, (game_desc, away, home, away_score, home_score, winner) in enumerate(real_games):
        game_id = f"nfl_2025_w9_real_{i+1}"
        game_ids.append(game_id)
        
        cursor.execute("""
            INSERT INTO nfl_games (game_id, week, year, game_date, away_team, home_team, 
                                   away_score, home_score, is_final)
            VALUES (?, 9, 2025, '2025-11-03', ?, ?, ?, ?, 1)
        """, (game_id, away, home, away_score, home_score))
        
        print(f"   ✅ {game_desc}: {away} {away_score} - {home_score} {home}")
    
    print(f"\n👥 INSERTING USER PICKS...")
    picks_inserted = 0
    
    for user_idx, username in enumerate(users):
        cursor.execute("SELECT id FROM users WHERE UPPER(username) = ?", (username.upper(),))
        user_result = cursor.fetchone()
        
        if not user_result:
            print(f"❌ User not found: {username}")
            continue
            
        user_id = user_result[0]
        user_correct = 0
        
        print(f"\n📋 {username}:")
        
        for game_idx in range(14):
            game_id = game_ids[game_idx]
            pick_text = user_picks[game_idx][user_idx]
            selected_team = team_map.get(pick_text, pick_text)
            winner = real_games[game_idx][5]  # Winner from real_games
            
            is_correct = 1 if selected_team == winner else 0
            if is_correct:
                user_correct += 1
            
            cursor.execute("""
                INSERT INTO user_picks (user_id, game_id, selected_team, is_correct, points_earned)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, game_id, selected_team, is_correct, is_correct))
            
            status = "✅" if is_correct else "❌"
            print(f"   {status} {real_games[game_idx][0]}: {pick_text} → {selected_team} (Winner: {winner})")
            picks_inserted += 1
        
        print(f"   📊 {username}: {user_correct}/14 correct")
    
    conn.commit()
    
    print(f"\n✅ INSERTED {picks_inserted} PICKS")
    
    # Final leaderboard
    cursor.execute("""
        SELECT u.username, 
               SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
               SUM(up.points_earned) as points
        FROM users u
        JOIN user_picks up ON u.id = up.user_id
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9
        GROUP BY u.username
        ORDER BY points DESC, correct DESC
    """)
    
    print(f"\n🏆 REAL NFL WEEK 9 LEADERBOARD:")
    for rank, (username, correct, points) in enumerate(cursor.fetchall(), 1):
        print(f"   {rank}. {username.upper()}: {correct}/14 correct ({points} points)")
    
    conn.close()

if __name__ == "__main__":
    fix_real_week9()