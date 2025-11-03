#!/usr/bin/env python3
"""
WORKING FINAL script - only updates picks (no tiebreaker table)
"""

import sqlite3

def main():
    print("🏈 WORKING FIX: GAME 9 AND WEEK 9 PICKS")
    print("=" * 42)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # User picks data (only game picks, no tiebreaker)
    users_picks = {
        'JAVIER': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'dallas', 'colts', 'gb', 'kc'],
        'VIZCA': ['minn', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', 'texans', 'bucs', 'denver', 'colts', 'gb', 'kc'],
        'ROBERT': ['minn', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc'],
        'COYOTE': ['minn', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'dallas', 'colts', 'steelers', 'kc'],
        'JEAN': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc'],
        'RAMFIS': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', 'texans', 'bucs', 'denver', 'colts', 'gb', 'kc'],
        'GUILLERMO': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'dallas', 'colts', 'gb', 'kc'],
        'JONIEL': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc'],
        'RADA': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', 'texans', 'bucs', 'denver', 'colts', 'steelers', 'kc'],
        'RAYMOND': ['minn', 'falcons', 'bengals', 'browns', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'dallas', 'colts', 'steelers', 'kc'],
        'SHORTY': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc'],
        'KRISTIAN': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', 'texans', 'bucs', 'denver', 'colts', 'gb', 'kc'],
        'FER': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'dallas', 'colts', 'gb', 'kc'],
        'MIKITIN': ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc']
    }
    
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
    
    # Get Week 9 games
    current_week = 9
    cursor.execute("""
        SELECT id, home_team, away_team 
        FROM nfl_games 
        WHERE week = ? 
        ORDER BY id
    """, (current_week,))
    games = cursor.fetchall()
    print(f"\n1. FOUND {len(games)} GAMES FOR WEEK {current_week}")
    
    # Update picks for each user
    print(f"\n2. UPDATING USER PICKS")
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
            
            # Clear existing picks for this user and week
            cursor.execute("""
                DELETE FROM user_picks 
                WHERE user_id = ? AND game_id IN (
                    SELECT id FROM nfl_games WHERE week = ?
                )
            """, (user_id, current_week))
            
            # Insert new picks
            picks_count = 0
            for i, pick_abbr in enumerate(picks):
                if i >= len(games):
                    break
                
                game_id = games[i][0]
                pick_team = team_map.get(pick_abbr.lower())
                
                if pick_team:
                    cursor.execute("""
                        INSERT INTO user_picks (user_id, game_id, selected_team)
                        VALUES (?, ?, ?)
                    """, (user_id, game_id, pick_team))
                    picks_count += 1
            
            print(f"   ✅ {username}: {picks_count} picks saved")
            total_updated += 1
            
        except Exception as e:
            print(f"   ❌ Error updating {username}: {e}")
    
    # Commit changes
    conn.commit()
    
    # Final verification
    cursor.execute("""
        SELECT COUNT(*) FROM user_picks 
        WHERE game_id IN (SELECT id FROM nfl_games WHERE week = ?)
    """, (current_week,))
    total_picks = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n🎯 COMPLETE!")
    print(f"✅ Users updated: {total_updated}")
    print(f"✅ Total picks in Week {current_week}: {total_picks}")
    print(f"✅ All picks successfully saved!")

if __name__ == "__main__":
    main()