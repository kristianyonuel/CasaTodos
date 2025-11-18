#!/usr/bin/env python3
"""
Update Week 9 picks for all 14 users with provided data
"""

import sqlite3
import sys

def update_week9_picks():
    """Update Week 9 picks with the provided data"""
    
    # User names in order
    users = ['JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 'KRISTIAN', 'FER', 'MIKITIN']
    
    # Picks data for each game (14 games total)
    picks_data = [
        # Game 1: Ravens @ Dolphins
        ['ravens', 'ravens', 'ravens', 'miami', 'ravens', 'ravens', 'ravens', 'ravens', 'ravens', 'Miami', 'ravens', 'ravens', 'ravens', 'ravens'],
        
        # Game 2: Bears @ Bengals  
        ['Bengals', 'Bears', 'Bears', 'Bengals', 'Bears', 'Bears', 'Bengals', 'Bears', 'Bears', 'Bears', 'Bears', 'Bears', 'Bengals', 'Bengals'],
        
        # Game 3: Vikings @ Lions
        ['Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Lions', 'Minn', 'Lions', 'Lions', 'Lions', 'Lions'],
        
        # Game 4: Panthers @ Packers
        ['Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb', 'Gb'],
        
        # Game 5: Chargers @ Titans
        ['Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers', 'Chargers'],
        
        # Game 6: Falcons @ Patriots
        ['Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats', 'Pats'],
        
        # Game 7: 49ers @ Giants
        ['49ers', '49ers', '49ers', '49ers', '49ers', 'Giants', '49ers', '49ers', 'Giants', 'Giants', 'Giants', '49ers', 'Giants', '49ers'],
        
        # Game 8: Colts @ Steelers
        ['Colts', 'Colts', 'Colts', 'Pit', 'Colts', 'Colts', 'Colts', 'Colts', 'Pitt', 'Pitt', 'Colts', 'Colts', 'Pitt', 'Colts'],
        
        # Game 9: Broncos @ Texans
        ['Denver', 'Texans', 'Denver', 'Den', 'Denver', 'Denver', 'Denver', 'Denver', 'Texans', 'Denver', 'Denver', 'Texans', 'Denver', 'Denver'],
        
        # Game 10: Jaguars @ Raiders
        ['Jax', 'Jax', 'Raiders', 'Jax', 'Jax', 'Jax', 'Jax', 'Jax', 'Jax', 'Raiders', 'Jax', 'Jax', 'Jax', 'Jax'],
        
        # Game 11: Saints @ Rams
        ['Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams', 'Rams'],
        
        # Game 12: Chiefs @ Bills
        ['Bills', 'Bills', 'Kc', 'Kc', 'Kc', 'Kc', 'Bills', 'Bills', 'Bills', 'Kc', 'Kc', 'Kc', 'Bills', 'Kc'],
        
        # Game 13: Seahawks @ Commanders
        ['Wash', 'Seattle', 'Seattle', 'Wash', 'Seattle', 'Wash', 'Wash', 'Wash', 'Seattle', 'Seattle', 'Seattle', 'Seattle', 'Wash', 'Seattle'],
        
        # Game 14: Cardinals @ Cowboys
        ['Dallas', 'Arizona', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Arizona', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Dallas', 'Dallas']
    ]
    
    # Tiebreaker scores
    tiebreaker_scores = ['31-20', '34-31', '31-14', '31-21', '21-16', '41-21', '28-24', '32-27', '27-16', '28-24', '32-24', '24-7', '35-21', '30-26']
    
    # Team name mappings to match database format
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
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        print("🏈 UPDATING WEEK 9 PICKS WITH PROVIDED DATA")
        print("=" * 50)
        
        # Get Week 9 games in order
        cursor.execute("""
            SELECT game_id, away_team, home_team, game_date 
            FROM nfl_games 
            WHERE week = 9 
            ORDER BY game_date, game_id
        """)
        week9_games = cursor.fetchall()
        
        if len(week9_games) != 14:
            print(f"❌ Expected 14 Week 9 games, found {len(week9_games)}")
            return
        
        print(f"📅 Found {len(week9_games)} Week 9 games")
        for i, (game_id, away, home, date) in enumerate(week9_games):
            print(f"   Game {i+1}: {away} @ {home} ({date})")
        
        # Clear existing Week 9 picks
        cursor.execute("DELETE FROM user_picks WHERE game_id IN (SELECT game_id FROM nfl_games WHERE week = 9)")
        cleared_picks = cursor.rowcount
        print(f"\n🗑️  Cleared {cleared_picks} existing Week 9 picks")
        
        # Add new picks
        total_picks_added = 0
        
        for user_idx, username in enumerate(users):
            # Get user ID
            cursor.execute("SELECT id FROM users WHERE UPPER(username) = ?", (username.upper(),))
            user_result = cursor.fetchone()
            
            if not user_result:
                print(f"❌ User not found: {username}")
                continue
                
            user_id = user_result[0]
            user_picks_count = 0
            
            # Add picks for each game
            for game_idx in range(len(week9_games)):
                if game_idx < len(picks_data):
                    game_id = week9_games[game_idx][0]
                    pick_text = picks_data[game_idx][user_idx]
                    
                    # Map team name
                    selected_team = team_mappings.get(pick_text, pick_text)
                    
                    # Add the pick
                    cursor.execute("""
                        INSERT INTO user_picks (user_id, game_id, selected_team) 
                        VALUES (?, ?, ?)
                    """, (user_id, game_id, selected_team))
                    
                    user_picks_count += 1
            
            total_picks_added += user_picks_count
            print(f"   ✅ {username}: {user_picks_count} picks added")
        
        # Update tiebreaker predictions for Monday Night game (Game 14)
        monday_game_id = week9_games[13][0]  # Cardinals @ Cowboys
        
        for user_idx, username in enumerate(users):
            cursor.execute("SELECT id FROM users WHERE UPPER(username) = ?", (username.upper(),))
            user_result = cursor.fetchone()
            
            if user_result:
                user_id = user_result[0]
                tiebreaker = tiebreaker_scores[user_idx]
                
                # Parse tiebreaker (e.g., "31-20")
                if '-' in tiebreaker:
                    parts = tiebreaker.split('-')
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        away_score = int(parts[0])
                        home_score = int(parts[1])
                        total_points = away_score + home_score
                        
                        # Update tiebreaker in user_picks
                        cursor.execute("""
                            UPDATE user_picks 
                            SET predicted_away_score = ?, predicted_home_score = ?
                            WHERE user_id = ? AND game_id = ?
                        """, (away_score, home_score, user_id, monday_game_id))
        
        conn.commit()
        print(f"\n✅ Successfully added {total_picks_added} picks for Week 9!")
        print("✅ Tiebreaker predictions updated for Monday Night game!")
        
        # Verify the update
        cursor.execute("""
            SELECT u.username, COUNT(up.id) as pick_count
            FROM users u
            LEFT JOIN user_picks up ON u.id = up.user_id
            LEFT JOIN nfl_games g ON up.game_id = g.game_id AND g.week = 9
            WHERE u.username IN ('JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 'KRISTIAN', 'FER', 'MIKITIN')
            GROUP BY u.id, u.username
            ORDER BY u.username
        """)
        
        verification = cursor.fetchall()
        print(f"\n📊 VERIFICATION:")
        for username, count in verification:
            print(f"   {username}: {count} picks")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_week9_picks()