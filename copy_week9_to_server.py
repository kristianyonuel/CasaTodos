#!/usr/bin/env python3
"""
Script to copy Week 9 data to server database
Run this on Azure VM after uploading the local database
"""

import sqlite3
import os
import shutil

def copy_week9_data_to_server():
    """Copy Week 9 data to the server database"""
    
    print("📋 COPYING WEEK 9 DATA TO SERVER DATABASE")
    print("=" * 50)
    
    # Server database path
    server_db = '/home/casa/CasaTodos/nfl_fantasy.db'
    
    if not os.path.exists(server_db):
        print(f"❌ Server database not found at {server_db}")
        return
    
    print(f"✅ Found server database: {server_db}")
    
    # Backup existing database
    backup_path = f"{server_db}.backup_{int(time.time())}"
    shutil.copy2(server_db, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Connect to server database
    conn = sqlite3.connect(server_db)
    cursor = conn.cursor()
    
    # Clear existing Week 9 data
    print("🗑️ Clearing existing Week 9 data...")
    cursor.execute("DELETE FROM user_picks WHERE game_id IN (SELECT game_id FROM nfl_games WHERE week = 9)")
    cursor.execute("DELETE FROM nfl_games WHERE week = 9")
    cursor.execute("DELETE FROM weekly_results WHERE week = 9")
    
    # Week 9 games with real scores
    print("🏈 Inserting Week 9 games...")
    week9_games = [
        ("nfl_2025_w9_real_1", "Baltimore Ravens", "Miami Dolphins", 31, 20),
        ("nfl_2025_w9_real_2", "Chicago Bears", "Cincinnati Bengals", 34, 31),
        ("nfl_2025_w9_real_3", "Minnesota Vikings", "Detroit Lions", 31, 14),
        ("nfl_2025_w9_real_4", "Carolina Panthers", "Green Bay Packers", 31, 21),
        ("nfl_2025_w9_real_5", "Los Angeles Chargers", "Tennessee Titans", 21, 16),
        ("nfl_2025_w9_real_6", "Atlanta Falcons", "New England Patriots", 41, 21),
        ("nfl_2025_w9_real_7", "San Francisco 49ers", "New York Giants", 28, 24),
        ("nfl_2025_w9_real_8", "Indianapolis Colts", "Pittsburgh Steelers", 32, 27),
        ("nfl_2025_w9_real_9", "Denver Broncos", "Houston Texans", 27, 16),
        ("nfl_2025_w9_real_10", "Jacksonville Jaguars", "Las Vegas Raiders", 28, 24),
        ("nfl_2025_w9_real_11", "New Orleans Saints", "Los Angeles Rams", 32, 24),
        ("nfl_2025_w9_real_12", "Kansas City Chiefs", "Buffalo Bills", 24, 7),
        ("nfl_2025_w9_real_13", "Seattle Seahawks", "Washington Commanders", 35, 21),
        ("nfl_2025_w9_real_14", "Arizona Cardinals", "Dallas Cowboys", 30, 26)
    ]
    
    for game_id, away, home, away_score, home_score in week9_games:
        cursor.execute("""
            INSERT INTO nfl_games (game_id, week, year, game_date, away_team, home_team, 
                                   away_score, home_score, is_final, game_status)
            VALUES (?, 9, 2025, '2025-11-03 13:00:00', ?, ?, ?, ?, 1, 'FINAL')
        """, (game_id, away, home, away_score, home_score))
    
    print(f"✅ Inserted {len(week9_games)} games")
    
    # User picks data
    print("📝 Inserting user picks...")
    
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
    
    # Team mappings
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
    
    # Game winners for scoring
    winners = [
        'Baltimore Ravens', 'Chicago Bears', 'Minnesota Vikings', 'Carolina Panthers',
        'Los Angeles Chargers', 'Atlanta Falcons', 'San Francisco 49ers', 'Indianapolis Colts',
        'Denver Broncos', 'Jacksonville Jaguars', 'New Orleans Saints', 'Kansas City Chiefs',
        'Seattle Seahawks', 'Arizona Cardinals'
    ]
    
    game_ids = [game[0] for game in week9_games]
    picks_inserted = 0
    
    for user_idx, username in enumerate(users):
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE UPPER(username) = ?", (username.upper(),))
        user_result = cursor.fetchone()
        
        if not user_result:
            print(f"❌ User not found: {username}")
            continue
            
        user_id = user_result[0]
        
        for game_idx in range(14):
            game_id = game_ids[game_idx]
            pick_text = user_picks[game_idx][user_idx]
            selected_team = team_map.get(pick_text, pick_text)
            winner = winners[game_idx]
            
            is_correct = 1 if selected_team == winner else 0
            
            cursor.execute("""
                INSERT INTO user_picks (user_id, game_id, selected_team, is_correct, points_earned)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, game_id, selected_team, is_correct, is_correct))
            
            picks_inserted += 1
    
    print(f"✅ Inserted {picks_inserted} picks")
    
    # Insert weekly results
    print("📊 Inserting weekly results...")
    cursor.execute("""
        SELECT u.id, u.username, 
               SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
               SUM(up.points_earned) as points
        FROM users u
        JOIN user_picks up ON u.id = up.user_id
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
        GROUP BY u.id, u.username
        ORDER BY points DESC, correct DESC
    """)
    
    results = cursor.fetchall()
    
    for rank, (user_id, username, correct, points) in enumerate(results, 1):
        cursor.execute("""
            INSERT INTO weekly_results 
            (user_id, week, year, correct_picks, total_points, total_picks, weekly_rank)
            VALUES (?, 9, 2025, ?, ?, 14, ?)
        """, (user_id, correct, points, rank))
    
    print(f"✅ Inserted {len(results)} weekly results")
    
    conn.commit()
    conn.close()
    
    print("🎯 WEEK 9 DATA COPY COMPLETE!")
    print("✅ All data successfully copied to server database")
    print("🔧 Now restart Flask service to load new data")

if __name__ == "__main__":
    import time
    copy_week9_data_to_server()