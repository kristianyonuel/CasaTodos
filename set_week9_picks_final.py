#!/usr/bin/env python3
"""
Final Week 9 picks update with exact user data and scores
"""

import sqlite3
import os

def set_week9_picks_final():
    """Set Week 9 picks with exact user data and scores"""
    
    print("🏈 SETTING WEEK 9 PICKS - FINAL UPDATE")
    print("=" * 50)
    
    # Connect to database
    db_path = 'nfl_fantasy.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear existing Week 9 data
    print("🗑️ Clearing existing Week 9 data...")
    cursor.execute("DELETE FROM user_picks WHERE game_id LIKE 'nfl_2025_w9_%'")
    cursor.execute("DELETE FROM nfl_games WHERE week = 9 AND year = 2025")
    cursor.execute("DELETE FROM weekly_results WHERE week = 9 AND year = 2025")
    
    # Week 9 games with real scores
    print("🏈 Creating Week 9 games...")
    games_data = [
        ("nfl_2025_w9_1", "Baltimore Ravens", "Miami Dolphins", 31, 20),
        ("nfl_2025_w9_2", "Chicago Bears", "Cincinnati Bengals", 34, 31),
        ("nfl_2025_w9_3", "Minnesota Vikings", "Detroit Lions", 31, 14),
        ("nfl_2025_w9_4", "Carolina Panthers", "Green Bay Packers", 31, 21),
        ("nfl_2025_w9_5", "Los Angeles Chargers", "Tennessee Titans", 21, 16),
        ("nfl_2025_w9_6", "Atlanta Falcons", "New England Patriots", 41, 21),
        ("nfl_2025_w9_7", "San Francisco 49ers", "New York Giants", 28, 24),
        ("nfl_2025_w9_8", "Indianapolis Colts", "Pittsburgh Steelers", 32, 27),
        ("nfl_2025_w9_9", "Denver Broncos", "Houston Texans", 27, 16),
        ("nfl_2025_w9_10", "Jacksonville Jaguars", "Las Vegas Raiders", 28, 24),
        ("nfl_2025_w9_11", "New Orleans Saints", "Los Angeles Rams", 32, 24),
        ("nfl_2025_w9_12", "Kansas City Chiefs", "Buffalo Bills", 24, 7),
        ("nfl_2025_w9_13", "Seattle Seahawks", "Washington Commanders", 35, 21),
        ("nfl_2025_w9_14", "Arizona Cardinals", "Dallas Cowboys", 30, 26)
    ]
    
    for game_id, away, home, away_score, home_score in games_data:
        cursor.execute("""
            INSERT INTO nfl_games (game_id, week, year, game_date, away_team, home_team, 
                                   away_score, home_score, is_final, game_status)
            VALUES (?, 9, 2025, '2025-11-03 13:00:00', ?, ?, ?, ?, 1, 'FINAL')
        """, (game_id, away, home, away_score, home_score))
    
    print(f"✅ Inserted {len(games_data)} games")
    
    # User picks data (exactly as provided)
    users = ['JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 'KRISTIAN', 'FER', 'MIKITIN']
    
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
    
    # Game winners (based on scores: 31-20 34-31 31-14 31-21 21-16 41-21 28-24 32-27 27-16 28-24 32-24 24-7 35-21 30-26)
    winners = [
        'Baltimore Ravens',  # Ravens 31-20 Dolphins
        'Chicago Bears',     # Bears 34-31 Bengals
        'Minnesota Vikings', # Vikings 31-14 Lions
        'Carolina Panthers', # Panthers 31-21 Packers
        'Los Angeles Chargers', # Chargers 21-16 Titans
        'Atlanta Falcons',   # Falcons 41-21 Patriots
        'San Francisco 49ers', # 49ers 28-24 Giants
        'Indianapolis Colts', # Colts 32-27 Steelers
        'Denver Broncos',    # Broncos 27-16 Texans
        'Jacksonville Jaguars', # Jaguars 28-24 Raiders
        'New Orleans Saints', # Saints 32-24 Rams
        'Kansas City Chiefs', # Chiefs 24-7 Bills
        'Seattle Seahawks',  # Seahawks 35-21 Commanders
        'Arizona Cardinals'  # Cardinals 30-26 Cowboys
    ]
    
    print("📝 Inserting user picks...")
    game_ids = [f"nfl_2025_w9_{i+1}" for i in range(14)]
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
    
    # Calculate and insert weekly results
    print("📊 Calculating weekly results...")
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
    
    # Show final leaderboard
    print("\n🏆 WEEK 9 FINAL LEADERBOARD:")
    print("-" * 40)
    for rank, (user_id, username, correct, points) in enumerate(results, 1):
        print(f"{rank:2d}. {username:10s} - {correct:2d}/14 correct ({points} points)")
    
    # Special check for COYOTE's Miami pick
    cursor.execute("""
        SELECT up.selected_team, up.is_correct, g.away_team, g.home_team, g.away_score, g.home_score
        FROM user_picks up
        JOIN users u ON up.user_id = u.id
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE u.username = 'COYOTE' AND g.week = 9 AND g.year = 2025
        AND (g.away_team = 'Miami Dolphins' OR g.home_team = 'Miami Dolphins')
    """)
    
    coyote_miami = cursor.fetchone()
    if coyote_miami:
        selected, correct, away, home, away_score, home_score = coyote_miami
        print(f"\n🔍 COYOTE's Miami pick: {selected} ({'✅ CORRECT' if correct else '❌ WRONG'})")
        print(f"   Game: {away} {away_score} - {home_score} {home}")
    
    conn.commit()
    conn.close()
    
    print("\n🎯 WEEK 9 PICKS UPDATE COMPLETE!")
    print("✅ All user picks set exactly as provided")
    print("✅ Scores applied correctly")
    print("✅ Weekly results calculated")

if __name__ == "__main__":
    set_week9_picks_final()