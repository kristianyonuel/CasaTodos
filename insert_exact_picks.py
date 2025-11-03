#!/usr/bin/env python3
"""
Insert Week 9 picks exactly as specified by the user
Clear existing picks and insert fresh data
"""

import sqlite3

def insert_week9_picks_exactly():
    """Insert Week 9 picks exactly as user specified"""
    
    print("📝 INSERTING WEEK 9 PICKS EXACTLY AS SPECIFIED")
    print("=" * 55)
    
    # User order and picks from the user's latest message
    users = ['JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 'KRISTIAN', 'FER', 'MIKITIN']
    
    # Picks in the exact order provided
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
    
    # Team mappings to full names
    team_mappings = {
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
    
    # Real game results for scoring
    game_winners = [
        'Baltimore Ravens',    # Ravens beat Dolphins 31-20
        'Chicago Bears',       # Bears beat Bengals 34-31  
        'Minnesota Vikings',   # Vikings beat Lions 31-14
        'Carolina Panthers',   # Panthers beat Packers 31-21
        'Los Angeles Chargers', # Chargers beat Titans 21-16
        'Atlanta Falcons',     # Falcons beat Patriots 41-21
        'San Francisco 49ers', # 49ers beat Giants 28-24
        'Indianapolis Colts',  # Colts beat Steelers 32-27
        'Denver Broncos',      # Broncos beat Texans 27-16
        'Jacksonville Jaguars', # Jaguars beat Raiders 28-24
        'New Orleans Saints',  # Saints beat Rams 32-24
        'Kansas City Chiefs',  # Chiefs beat Bills 24-7
        'Seattle Seahawks',    # Seahawks beat Commanders 35-21
        'Arizona Cardinals'    # Cardinals beat Cowboys 30-26
    ]
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get Week 9 games in order
    cursor.execute("""
        SELECT game_id
        FROM nfl_games 
        WHERE week = 9 AND year = 2025
        ORDER BY game_id
    """)
    
    game_ids = [row[0] for row in cursor.fetchall()]
    
    if len(game_ids) != 14:
        print(f"❌ Expected 14 games, found {len(game_ids)}")
        return
    
    print(f"🎯 Found {len(game_ids)} Week 9 games")
    
    # Clear existing Week 9 picks
    cursor.execute("""
        DELETE FROM user_picks 
        WHERE game_id IN (SELECT game_id FROM nfl_games WHERE week = 9 AND year = 2025)
    """)
    
    print("🗑️ Cleared existing Week 9 picks")
    
    # Insert new picks
    picks_inserted = 0
    
    for user_idx, username in enumerate(users):
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE UPPER(username) = ?", (username.upper(),))
        user_result = cursor.fetchone()
        
        if not user_result:
            print(f"❌ User not found: {username}")
            continue
            
        user_id = user_result[0]
        user_correct = 0
        
        print(f"\\n👤 {username}:")
        
        for game_idx in range(14):
            game_id = game_ids[game_idx]
            pick_text = user_picks[game_idx][user_idx]
            selected_team = team_mappings.get(pick_text, pick_text)
            winner = game_winners[game_idx]
            
            is_correct = 1 if selected_team == winner else 0
            if is_correct:
                user_correct += 1
            
            cursor.execute("""
                INSERT INTO user_picks (user_id, game_id, selected_team, is_correct, points_earned)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, game_id, selected_team, is_correct, is_correct))
            
            status = "✅" if is_correct else "❌"
            print(f"   Game {game_idx+1}: {pick_text} → {selected_team} {status}")
            picks_inserted += 1
        
        print(f"   📊 {username}: {user_correct}/14 correct")
    
    conn.commit()
    
    print(f"\\n✅ INSERTED {picks_inserted} PICKS")
    
    # Update weekly_results
    cursor.execute("DELETE FROM weekly_results WHERE week = 9 AND year = 2025")
    
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
    
    conn.commit()
    
    print(f"\\n🏆 FINAL WEEK 9 LEADERBOARD:")
    for rank, (user_id, username, correct, points) in enumerate(results, 1):
        print(f"   {rank}. {username.upper()}: {correct}/14 correct ({points} points)")
    
    conn.close()

if __name__ == "__main__":
    insert_week9_picks_exactly()