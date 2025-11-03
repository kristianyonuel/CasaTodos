#!/usr/bin/env python3
"""
Fix Game 9 schedule error and update current week picks
- Fix Game 9: Should be Green Bay Packers vs Carolina Panthers
- Update picks for all users based on provided data
"""

import sqlite3
import sys
from datetime import datetime

def connect_database():
    """Connect to the NFL Fantasy database"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def get_current_week():
    """Get the current NFL week"""
    conn = connect_database()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    # Get current week from database
    cursor.execute("""
        SELECT week FROM nfl_games 
        WHERE game_date >= date('now') 
        ORDER BY game_date LIMIT 1
    """)
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        # Default to week 9 if no future games found
        return 9

def fix_game9_schedule():
    """Fix Game 9 schedule to Green Bay Packers vs Carolina Panthers"""
    print("=== FIXING GAME 9 SCHEDULE ===")
    
    conn = connect_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # First, check what Game 9 currently shows
    cursor.execute("""
        SELECT id, home_team, away_team, week, game_date 
        FROM nfl_games 
        WHERE id = 9
    """)
    current_game = cursor.fetchone()
    
    if current_game:
        print(f"Current Game 9: {current_game[2]} @ {current_game[1]} (Week {current_game[3]})")
        
        # Update to correct teams
        cursor.execute("""
            UPDATE nfl_games 
            SET home_team = 'Green Bay Packers', 
                away_team = 'Carolina Panthers'
            WHERE id = 9
        """)
        
        conn.commit()
        print("✅ Fixed Game 9: Carolina Panthers @ Green Bay Packers")
        
        # Verify the fix
        cursor.execute("SELECT home_team, away_team FROM nfl_games WHERE id = 9")
        updated_game = cursor.fetchone()
        print(f"✅ Verified: {updated_game[1]} @ {updated_game[0]}")
        
    else:
        print("❌ Game 9 not found in database")
        conn.close()
        return False
    
    conn.close()
    return True

def get_team_mappings():
    """Map team abbreviations to full names"""
    return {
        'chargers': 'Los Angeles Chargers',
        'minn': 'Minnesota Vikings',
        'falcons': 'Atlanta Falcons',
        'bengals': 'Cincinnati Bengals',
        'pats': 'New England Patriots',
        'browns': 'Cleveland Browns',
        'eagles': 'Philadelphia Eagles',
        'bills': 'Buffalo Bills',
        'bears': 'Chicago Bears',
        'ravens': 'Baltimore Ravens',
        '49ers': 'San Francisco 49ers',
        'texans': 'Houston Texans',
        'bucs': 'Tampa Bay Buccaneers',
        'dallas': 'Dallas Cowboys',
        'denver': 'Denver Broncos',
        'colts': 'Indianapolis Colts',
        'gb': 'Green Bay Packers',
        'steelers': 'Pittsburgh Steelers',
        'kc': 'Kansas City Chiefs'
    }

def update_user_picks():
    """Update picks for all users based on provided data"""
    print("\n=== UPDATING USER PICKS ===")
    
    # User data from the request
    users = ['JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 'GUILLERMO', 
             'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 'KRISTIAN', 'FER', 'MIKITIN']
    
    # Picks data (14 users x 13 games + tiebreaker)
    picks_data = [
        ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'dallas', 'colts', 'gb', 'kc', '30-10'],
        ['minn', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', 'texans', 'bucs', 'denver', 'colts', 'gb', 'kc', '24-13'],
        ['minn', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc', '28-14'],
        ['minn', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'dallas', 'colts', 'steelers', 'kc', '31-17'],
        ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc', '31-14'],
        ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', 'texans', 'bucs', 'denver', 'colts', 'gb', 'kc', '32-20'],
        ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'dallas', 'colts', 'gb', 'kc', '42-14'],
        ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc', '35-21'],
        ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'bears', 'texans', 'bucs', 'denver', 'colts', 'steelers', 'kc', '27-15'],
        ['minn', 'falcons', 'bengals', 'browns', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'dallas', 'colts', 'steelers', 'kc', '31-17'],
        ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc', '38-24'],
        ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', 'texans', 'bucs', 'denver', 'colts', 'gb', 'kc', '30-13'],
        ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'dallas', 'colts', 'gb', 'kc', '34-21'],
        ['chargers', 'falcons', 'bengals', 'pats', 'eagles', 'bills', 'ravens', '49ers', 'bucs', 'denver', 'colts', 'gb', 'kc', '38-10']
    ]
    
    current_week = get_current_week()
    if not current_week:
        print("❌ Could not determine current week")
        return False
    
    print(f"Updating picks for Week {current_week}")
    
    conn = connect_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    team_mappings = get_team_mappings()
    
    # Get games for current week
    cursor.execute("""
        SELECT id, home_team, away_team 
        FROM nfl_games 
        WHERE week = ? 
        ORDER BY id
    """, (current_week,))
    
    games = cursor.fetchall()
    
    if len(games) < 13:
        print(f"❌ Only found {len(games)} games for week {current_week}, expected 13")
        conn.close()
        return False
    
    print(f"Found {len(games)} games for Week {current_week}")
    
    # Process each user's picks
    for i, username in enumerate(users):
        if i >= len(picks_data):
            print(f"❌ No picks data for user {username}")
            continue
            
        user_picks = picks_data[i]
        tiebreaker = user_picks[-1]  # Last item is tiebreaker
        game_picks = user_picks[:-1]  # All except last are game picks
        
        print(f"\nUpdating picks for {username}:")
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE UPPER(username) = UPPER(?)", (username,))
        user_result = cursor.fetchone()
        
        if not user_result:
            print(f"  ❌ User {username} not found in database")
            continue
            
        user_id = user_result[0]
        
        # Clear existing picks for this week
        cursor.execute("""
            DELETE FROM user_picks 
            WHERE user_id = ? AND week = ?
        """, (user_id, current_week))
        
        # Insert new picks
        picks_inserted = 0
        for j, pick_abbr in enumerate(game_picks):
            if j >= len(games):
                break
                
            game = games[j]
            game_id = game[0]
            home_team = game[1]
            away_team = game[2]
            
            # Convert abbreviation to full team name
            pick_abbr_lower = pick_abbr.lower()
            if pick_abbr_lower in team_mappings:
                picked_team = team_mappings[pick_abbr_lower]
            else:
                print(f"  ⚠️  Unknown team abbreviation: {pick_abbr}")
                continue
            
            # Verify the picked team is actually in this game
            if picked_team not in [home_team, away_team]:
                print(f"  ⚠️  {picked_team} not in game {game_id}: {away_team} @ {home_team}")
                continue
            
            # Insert the pick
            cursor.execute("""
                INSERT INTO user_picks (user_id, game_id, picked_team, week)
                VALUES (?, ?, ?, ?)
            """, (user_id, game_id, picked_team, current_week))
            
            picks_inserted += 1
            print(f"  ✅ Game {game_id}: {picked_team}")
        
        # Insert tiebreaker prediction
        if tiebreaker and '-' in tiebreaker:
            # Clean up tiebreaker format (handle cases like "38--24")
            clean_tiebreaker = tiebreaker.replace('--', '-')
            
            cursor.execute("""
                INSERT OR REPLACE INTO tiebreaker_predictions 
                (user_id, week, prediction)
                VALUES (?, ?, ?)
            """, (user_id, current_week, clean_tiebreaker))
            print(f"  ✅ Tiebreaker: {clean_tiebreaker}")
        
        print(f"  📊 Total picks inserted: {picks_inserted}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully updated picks for Week {current_week}")
    return True

def verify_updates():
    """Verify that updates were applied correctly"""
    print("\n=== VERIFICATION ===")
    
    conn = connect_database()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Verify Game 9 fix
    cursor.execute("SELECT home_team, away_team FROM nfl_games WHERE id = 9")
    game9 = cursor.fetchone()
    if game9:
        print(f"Game 9: {game9[1]} @ {game9[0]}")
    
    # Verify picks count
    current_week = get_current_week()
    cursor.execute("""
        SELECT COUNT(DISTINCT user_id) as users, COUNT(*) as total_picks
        FROM user_picks 
        WHERE week = ?
    """, (current_week,))
    
    picks_count = cursor.fetchone()
    if picks_count:
        print(f"Week {current_week} picks: {picks_count[1]} total picks from {picks_count[0]} users")
    
    # Verify tiebreaker predictions
    cursor.execute("""
        SELECT COUNT(*) 
        FROM tiebreaker_predictions 
        WHERE week = ?
    """, (current_week,))
    
    tiebreaker_count = cursor.fetchone()
    if tiebreaker_count:
        print(f"Tiebreaker predictions: {tiebreaker_count[0]}")
    
    conn.close()

def main():
    print("🏈 NFL FANTASY DATABASE UPDATE")
    print("=" * 50)
    
    # Fix Game 9 schedule
    if fix_game9_schedule():
        print("✅ Game 9 schedule fixed")
    else:
        print("❌ Failed to fix Game 9 schedule")
        return
    
    # Update user picks
    if update_user_picks():
        print("✅ User picks updated")
    else:
        print("❌ Failed to update user picks")
        return
    
    # Verify everything
    verify_updates()
    
    print("\n" + "=" * 50)
    print("🎯 UPDATE COMPLETE!")
    print("✅ Game 9 fixed: Carolina Panthers @ Green Bay Packers")
    print("✅ All user picks updated for current week")
    print("✅ Tiebreaker predictions saved")

if __name__ == "__main__":
    main()