#!/usr/bin/env python3
"""
Quick fix for Game 9 schedule and week picks update
Run this on the server: python3 quick_fix_week9.py
"""

import sqlite3

def main():
    print("🏈 FIXING GAME 9 AND UPDATING PICKS")
    print("=" * 40)
    
    # Connect to database
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # Fix Game 9 schedule
    print("\n1. FIXING GAME 9 SCHEDULE")
    try:
        # Check current Game 9
        cursor.execute("SELECT id, home_team, away_team FROM nfl_games WHERE id = 9")
        current = cursor.fetchone()
        if current:
            print(f"   Current: {current[2]} @ {current[1]}")
        
        # Fix to correct teams
        cursor.execute("""
            UPDATE nfl_games 
            SET home_team = 'Green Bay Packers', away_team = 'Carolina Panthers'
            WHERE id = 9
        """)
        print("   ✅ Fixed: Carolina Panthers @ Green Bay Packers")
        
    except Exception as e:
        print(f"   ❌ Error fixing Game 9: {e}")
    
    # Get current week
    print("\n2. DETERMINING CURRENT WEEK")
    try:
        cursor.execute("""
            SELECT week FROM nfl_games 
            WHERE game_date >= date('now') 
            ORDER BY game_date LIMIT 1
        """)
        week_result = cursor.fetchone()
        current_week = week_result[0] if week_result else 9
        print(f"   Current week: {current_week}")
    except:
        current_week = 9
        print(f"   Using default week: {current_week}")
    
    # Define user picks (from your data)
    users_picks = {
        'JAVIER': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'dallas', 'colts', 'gb', 'kc', '30-10'],
        'VIZCA': ['minn', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', 'texans', 'bucs', 'denver', 'colts', 'gb', 'kc', '24-13'],
        'ROBERT': ['minn', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc', '28-14'],
        'COYOTE': ['minn', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'dallas', 'colts', 'steelers', 'kc', '31-17'],
        'JEAN': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc', '31-14'],
        'RAMFIS': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', 'texans', 'bucs', 'denver', 'colts', 'gb', 'kc', '32-20'],
        'GUILLERMO': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'dallas', 'colts', 'gb', 'kc', '42-14'],
        'JONIEL': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc', '35-21'],
        'RADA': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', 'texans', 'bucs', 'denver', 'colts', 'steelers', 'kc', '27-15'],
        'RAYMOND': ['minn', 'falcons', 'bengals', 'browns', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'dallas', 'colts', 'steelers', 'kc', '31-17'],
        'SHORTY': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc', '38-24'],
        'KRISTIAN': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', 'texans', 'bucs', 'denver', 'colts', 'gb', 'kc', '30-13'],
        'FER': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'dallas', 'colts', 'gb', 'kc', '34-21'],
        'MIKITIN': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc', '38-10']
    }
    
    # Team name mappings
    team_map = {
        'chargers': 'Los Angeles Chargers', 'minn': 'Minnesota Vikings',
        'falcons': 'Atlanta Falcons', 'bengals': 'Cincinnati Bengals',
        'pats': 'New England Patriots', 'browns': 'Cleveland Browns',
        'eagles': 'Philadelphia Eagles', 'bills': 'Buffalo Bills',
        'bears': 'Chicago Bears', 'ravens': 'Baltimore Ravens',
        '49ers': 'San Francisco 49ers', 'texans': 'Houston Texans',
        'bucs': 'Tampa Bay Buccaneers', 'dallas': 'Dallas Cowboys',
        'denver': 'Denver Broncos', 'colts': 'Indianapolis Colts',
        'gb': 'Green Bay Packers', 'steelers': 'Pittsburgh Steelers',
        'kc': 'Kansas City Chiefs'
    }
    
    print(f"\n3. UPDATING PICKS FOR WEEK {current_week}")
    
    # Get games for the week
    cursor.execute("""
        SELECT id, home_team, away_team 
        FROM nfl_games 
        WHERE week = ? 
        ORDER BY id
    """, (current_week,))
    games = cursor.fetchall()
    print(f"   Found {len(games)} games")
    
    # Update picks for each user
    total_updated = 0
    for username, picks in users_picks.items():
        try:
            # Get user ID
            cursor.execute("SELECT id FROM users WHERE UPPER(username) = UPPER(?)", (username,))
            user_result = cursor.fetchone()
            if not user_result:
                print(f"   ⚠️  User {username} not found")
                continue
            
            user_id = user_result[0]
            
            # Clear existing picks
            cursor.execute("DELETE FROM user_picks WHERE user_id = ? AND week = ?", (user_id, current_week))
            
            # Insert new picks (first 13 are game picks, last is tiebreaker)
            game_picks = picks[:-1]
            tiebreaker = picks[-1]
            
            picks_count = 0
            for i, pick_abbr in enumerate(game_picks):
                if i >= len(games):
                    break
                
                game_id = games[i][0]
                pick_team = team_map.get(pick_abbr.lower())
                
                if pick_team:
                    cursor.execute("""
                        INSERT INTO user_picks (user_id, game_id, picked_team, week)
                        VALUES (?, ?, ?, ?)
                    """, (user_id, game_id, pick_team, current_week))
                    picks_count += 1
            
            # Add tiebreaker
            clean_tiebreaker = tiebreaker.replace('--', '-')
            cursor.execute("""
                INSERT OR REPLACE INTO tiebreaker_predictions (user_id, week, prediction)
                VALUES (?, ?, ?)
            """, (user_id, current_week, clean_tiebreaker))
            
            print(f"   ✅ {username}: {picks_count} picks + tiebreaker {clean_tiebreaker}")
            total_updated += 1
            
        except Exception as e:
            print(f"   ❌ Error updating {username}: {e}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"\n🎯 COMPLETE!")
    print(f"✅ Game 9 fixed: Carolina Panthers @ Green Bay Packers")
    print(f"✅ Updated picks for {total_updated} users in Week {current_week}")
    print(f"✅ All changes saved to database")

if __name__ == "__main__":
    main()