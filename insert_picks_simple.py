#!/usr/bin/env python3
"""
Simple Week 9 picks insertion - no deletions, just insert picks
"""

import sqlite3

def insert_week9_picks_simple():
    """Insert Week 9 picks directly without deleting existing data"""
    
    print("📝 INSERTING WEEK 9 PICKS (SIMPLE)")
    print("=" * 40)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Users in order
    users = ['JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 
             'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 
             'KRISTIAN', 'FER', 'MIKITIN']
    
    # Picks data - each row is one game, each column is one user's pick
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
    
    # Game winners (based on scores provided)
    winners = [
        'Baltimore Ravens',  # 31-20 vs Miami
        'Chicago Bears',     # 34-31 vs Bengals
        'Minnesota Vikings', # 31-14 vs Lions
        'Carolina Panthers', # 31-21 vs Packers
        'Los Angeles Chargers', # 21-16 vs Titans
        'Atlanta Falcons',   # 41-21 vs Patriots
        'San Francisco 49ers', # 28-24 vs Giants
        'Indianapolis Colts', # 32-27 vs Steelers
        'Denver Broncos',    # 27-16 vs Texans
        'Jacksonville Jaguars', # 28-24 vs Raiders
        'New Orleans Saints', # 32-24 vs Rams
        'Kansas City Chiefs', # 24-7 vs Bills
        'Seattle Seahawks',  # 35-21 vs Commanders
        'Arizona Cardinals'  # 30-26 vs Cowboys
    ]
    
    # Get Week 9 game IDs (assume they exist)
    cursor.execute("SELECT game_id FROM nfl_games WHERE week = 9 AND year = 2025 ORDER BY game_id")
    game_ids = [row[0] for row in cursor.fetchall()]
    
    if len(game_ids) != 14:
        print(f"⚠️  Warning: Found {len(game_ids)} games, expected 14")
    
    # Clear existing Week 9 picks only
    print("🗑️ Clearing existing Week 9 picks...")
    cursor.execute("""
        DELETE FROM user_picks 
        WHERE game_id IN (SELECT game_id FROM nfl_games WHERE week = 9 AND year = 2025)
    """)
    
    print("📝 Inserting new picks...")
    picks_inserted = 0
    
    # Insert picks for each user and game
    for user_idx, username in enumerate(users):
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE UPPER(username) = ?", (username.upper(),))
        user_result = cursor.fetchone()
        
        if not user_result:
            print(f"❌ User not found: {username}")
            continue
            
        user_id = user_result[0]
        
        for game_idx in range(min(14, len(game_ids))):
            game_id = game_ids[game_idx]
            pick_text = picks_data[game_idx][user_idx]
            selected_team = team_map.get(pick_text, pick_text)
            winner = winners[game_idx]
            
            is_correct = 1 if selected_team == winner else 0
            
            cursor.execute("""
                INSERT INTO user_picks (user_id, game_id, selected_team, is_correct, points_earned)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, game_id, selected_team, is_correct, is_correct))
            
            picks_inserted += 1
    
    print(f"✅ Inserted {picks_inserted} picks")
    
    # Update weekly_results
    print("📊 Updating weekly_results...")
    
    # Clear Week 9 results
    cursor.execute("DELETE FROM weekly_results WHERE week = 9 AND year = 2025")
    
    # Calculate and insert new results
    cursor.execute("""
        SELECT u.id, u.username,
               SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
               SUM(up.points_earned) as points,
               COUNT(*) as total
        FROM users u
        JOIN user_picks up ON u.id = up.user_id
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
        GROUP BY u.id, u.username
        ORDER BY points DESC, correct DESC
    """)
    
    results = cursor.fetchall()
    
    for rank, (user_id, username, correct, points, total) in enumerate(results, 1):
        cursor.execute("""
            INSERT INTO weekly_results 
            (user_id, week, year, correct_picks, total_points, total_picks, weekly_rank)
            VALUES (?, 9, 2025, ?, ?, ?, ?)
        """, (user_id, correct, points, total, rank))
    
    print(f"✅ Inserted {len(results)} weekly results")
    
    # Show final leaderboard
    print("\n🏆 FINAL WEEK 9 LEADERBOARD:")
    for rank, (user_id, username, correct, points, total) in enumerate(results, 1):
        print(f"  {rank:2d}. {username.upper():12s} - {correct:2d}/{total} correct ({points} pts)")
    
    conn.commit()
    conn.close()
    
    print("\n🎯 WEEK 9 PICKS INSERTED!")

if __name__ == "__main__":
    insert_week9_picks_simple()