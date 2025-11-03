#!/usr/bin/env python3
"""
FINAL CORRECTED script for Game 9 schedule and week picks update
Uses the actual database schema with 'selected_team' column
"""

import sqlite3

def main():
    print("🏈 FINAL FIX: GAME 9 AND WEEK 9 PICKS")
    print("=" * 45)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # 1. Fix Game 9 schedule (already done but confirm)
    print("\n1. CONFIRMING GAME 9 SCHEDULE")
    cursor.execute("SELECT id, home_team, away_team FROM nfl_games WHERE id = 9")
    current = cursor.fetchone()
    if current:
        print(f"   Game 9: {current[2]} @ {current[1]}")
    
    # 2. Define user picks data
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
    
    # 3. Get Week 9 games
    current_week = 9
    cursor.execute("""
        SELECT id, home_team, away_team 
        FROM nfl_games 
        WHERE week = ? 
        ORDER BY id
    """, (current_week,))
    games = cursor.fetchall()
    print(f"\n2. FOUND {len(games)} GAMES FOR WEEK {current_week}")
    
    # Show first few games for verification
    for i, game in enumerate(games[:5]):
        print(f"   Game {game[0]}: {game[2]} @ {game[1]}")
    
    # 4. Update picks for each user
    print(f"\n3. UPDATING USER PICKS")
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
                    # Use correct column name: selected_team
                    cursor.execute("""
                        INSERT INTO user_picks (user_id, game_id, selected_team)
                        VALUES (?, ?, ?)
                    """, (user_id, game_id, pick_team))
                    picks_count += 1
            
            # Add tiebreaker prediction
            clean_tiebreaker = tiebreaker.replace('--', '-')
            cursor.execute("""
                INSERT OR REPLACE INTO tiebreaker_predictions (user_id, week, prediction)
                VALUES (?, ?, ?)
            """, (user_id, current_week, clean_tiebreaker))
            
            print(f"   ✅ {username}: {picks_count} picks + tiebreaker ({clean_tiebreaker})")
            total_updated += 1
            
        except Exception as e:
            print(f"   ❌ Error updating {username}: {e}")
    
    # 5. Commit and verify
    conn.commit()
    
    # Verification
    cursor.execute("""
        SELECT COUNT(*) FROM user_picks 
        WHERE game_id IN (SELECT id FROM nfl_games WHERE week = ?)
    """, (current_week,))
    total_picks = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM tiebreaker_predictions WHERE week = ?
    """, (current_week,))
    total_tiebreakers = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"✅ Game 9: Carolina Panthers @ Green Bay Packers")
    print(f"✅ Users updated: {total_updated}")
    print(f"✅ Total picks saved: {total_picks}")
    print(f"✅ Tiebreaker predictions: {total_tiebreakers}")
    print(f"✅ Week {current_week} picks complete!")

if __name__ == "__main__":
    main()