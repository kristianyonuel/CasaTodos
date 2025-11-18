#!/usr/bin/env python3
"""
Correct Week 9 picks to exactly match the provided data
The database has incorrect picks - need to fix them
"""

import sqlite3

def fix_week9_picks_correctly():
    """Fix Week 9 picks to match the provided data exactly"""
    
    print("🔧 FIXING WEEK 9 PICKS TO MATCH PROVIDED DATA")
    print("=" * 55)
    
    # User order from your data
    users = ['JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 'KRISTIAN', 'FER', 'MIKITIN']
    
    # Your provided picks data (in your order)
    provided_picks = [
        # Ravens @ Dolphins
        ['ravens', 'ravens', 'ravens', 'miami', 'ravens', 'ravens', 'ravens', 'ravens', 'ravens', 'Miami', 'ravens', 'ravens', 'ravens', 'ravens'],
        
        # Bears @ Bengals  
        ['Bengals', 'Bears', 'Bears', 'Bengals', 'Bears', 'Bears', 'Bengals', 'Bears', 'Bears', 'Bears', 'Bears', 'Bears', 'Bengals', 'Bengals'],
        
        # Vikings @ Lions
        ['Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Minn', 'Lions', 'Lions', 'Lions', 'Lions'],
        
        # Panthers @ Packers
        ['Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb'],
        
        # Chargers @ Titans
        ['Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers'],
        
        # Falcons @ Patriots
        ['Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats'],
        
        # 49ers @ Giants
        ['49ers', '49ers', '49ers', '49ers', '49ers', 'Giants', '49ers', '49ers', 'Giants', 'Giants', 'Giants', '49ers', 'Giants', '49ers'],
        
        # Colts @ Steelers
        ['Colts', 'Colts', 'Colts', 'Pit', 'Colts', 'Colts', 'Colts', 'Colts', 'Pitt', 'Pitt', 'Colts', 'Colts', 'Pitt', 'Colts'],
        
        # Broncos @ Texans
        ['Denver', 'Texans', 'Denver', 'Den', 'Denver', 'Denver', 'Denver', 'Denver', 'Texans', 'Denver', 'Denver', 'Texans', 'Denver', 'Denver'],
        
        # Jaguars @ Raiders
        ['Jax', 'Jax', 'Raiders', 'Jax', 'Jax', 'Jax', 'Jax', 'Jax', 'Jax', 'Raiders', 'Jax', 'Jax', 'Jax', 'Jax'],
        
        # Saints @ Rams
        ['Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams'],
        
        # Chiefs @ Bills
        ['Bills', 'Bills', 'Kc', 'Kc', 'Kc', 'Kc', 'Bills', 'Bills', 'Bills', 'Kc', 'Kc', 'Kc', 'Bills', 'Kc'],
        
        # Seahawks @ Commanders
        ['Wash', 'Seattle', 'Seattle', 'Wash', 'Seattle', 'Wash', 'Wash', 'Wash', 'Seattle', 'Seattle', 'Seattle', 'Seattle', 'Wash', 'Seattle'],
        
        # Cardinals @ Cowboys
        ['Dallas', 'Arizona', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Arizona', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Dallas']
    ]
    
    # Team name mappings
    team_mappings = {
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
    
    # Expected game order based on your data structure
    expected_games = [
        ('Baltimore Ravens', 'Miami Dolphins'),
        ('Chicago Bears', 'Cincinnati Bengals'),
        ('Minnesota Vikings', 'Detroit Lions'),
        ('Carolina Panthers', 'Green Bay Packers'),
        ('Los Angeles Chargers', 'Tennessee Titans'),
        ('Atlanta Falcons', 'New England Patriots'),
        ('San Francisco 49ers', 'New York Giants'),
        ('Indianapolis Colts', 'Pittsburgh Steelers'),
        ('Denver Broncos', 'Houston Texans'),
        ('Jacksonville Jaguars', 'Las Vegas Raiders'),
        ('New Orleans Saints', 'Los Angeles Rams'),
        ('Kansas City Chiefs', 'Buffalo Bills'),
        ('Seattle Seahawks', 'Washington Commanders'),
        ('Arizona Cardinals', 'Dallas Cowboys')
    ]
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🔍 IDENTIFYING GAME ORDER:")
    # Get actual games from database in date order
    cursor.execute("""
        SELECT game_id, away_team, home_team
        FROM nfl_games 
        WHERE week = 9 
        ORDER BY game_date, game_id
    """)
    
    db_games = cursor.fetchall()
    
    # Create mapping between expected order and database games
    game_mapping = {}
    for i, (away, home) in enumerate(expected_games):
        for game_id, db_away, db_home in db_games:
            if (away in db_away or db_away in away) and (home in db_home or db_home in home):
                game_mapping[i] = game_id
                print(f"   Game {i+1}: {away} @ {home} → DB Game {game_id}")
                break
    
    if len(game_mapping) != 14:
        print(f"❌ Could only map {len(game_mapping)}/14 games")
        return
    
    print(f"\n🔄 UPDATING PICKS:")
    picks_updated = 0
    
    for user_idx, username in enumerate(users):
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE UPPER(username) = ?", (username.upper(),))
        user_result = cursor.fetchone()
        
        if not user_result:
            print(f"❌ User not found: {username}")
            continue
            
        user_id = user_result[0]
        user_picks_updated = 0
        
        print(f"\n👤 {username}:")
        
        for game_idx in range(14):
            if game_idx in game_mapping and game_idx < len(provided_picks):
                game_id = game_mapping[game_idx]
                pick_text = provided_picks[game_idx][user_idx]
                selected_team = team_mappings.get(pick_text, pick_text)
                
                # Update the pick
                cursor.execute("""
                    UPDATE user_picks 
                    SET selected_team = ?
                    WHERE user_id = ? AND game_id = ?
                """, (selected_team, user_id, game_id))
                
                if cursor.rowcount > 0:
                    user_picks_updated += 1
                    print(f"   ✅ Game {game_idx+1}: {pick_text} → {selected_team}")
        
        picks_updated += user_picks_updated
        print(f"   📊 Updated {user_picks_updated} picks for {username}")
    
    conn.commit()
    print(f"\n✅ Total picks updated: {picks_updated}")
    
    # Re-score all picks with corrected data
    print(f"\n🎯 RE-SCORING ALL PICKS:")
    cursor.execute("UPDATE user_picks SET is_correct = NULL, points_earned = 0 WHERE game_id IN (SELECT game_id FROM nfl_games WHERE week = 9)")
    
    # Score picks again
    cursor.execute("""
        SELECT game_id, away_team, home_team, away_score, home_score
        FROM nfl_games
        WHERE week = 9 AND is_final = 1
    """)
    
    for game_id, away, home, away_score, home_score in cursor.fetchall():
        winner = home if home_score > away_score else away
        
        cursor.execute("""
            UPDATE user_picks
            SET is_correct = CASE WHEN selected_team = ? THEN 1 ELSE 0 END,
                points_earned = CASE WHEN selected_team = ? THEN 1 ELSE 0 END
            WHERE game_id = ?
        """, (winner, winner, game_id))
    
    conn.commit()
    
    # Show corrected leaderboard
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
    
    leaderboard = cursor.fetchall()
    print(f"\n🏆 CORRECTED WEEK 9 LEADERBOARD:")
    for rank, (username, correct, points) in enumerate(leaderboard, 1):
        print(f"   {rank}. {username}: {correct} correct, {points} points")
    
    conn.close()

if __name__ == "__main__":
    fix_week9_picks_correctly()