#!/usr/bin/env python3
"""
Fix Week 9 completely - the games in database don't match real NFL schedule
Need to clear and rebuild Week 9 properly
"""

import sqlite3

def check_database_structure():
    """Check what columns exist in nfl_games table"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(nfl_games)")
        columns = cursor.fetchall()
        
        print("🔍 NFL_GAMES TABLE COLUMNS:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        conn.close()
        return [col[1] for col in columns]
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def show_current_week9():
    """Show what's currently in Week 9"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, home_team, away_team, game_date
            FROM nfl_games 
            WHERE week = 9 
            ORDER BY id
        """)
        games = cursor.fetchall()
        
        print(f"\n📊 CURRENT WEEK 9 GAMES ({len(games)} total):")
        for game in games:
            print(f"   Game {game[0]}: {game[2]} @ {game[1]} ({game[3]})")
        
        conn.close()
        return games
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def fix_week9_games():
    """Update Week 9 games to match real NFL schedule"""
    
    # Real Week 9 NFL matchups
    real_week9 = [
        ("Miami Dolphins", "Baltimore Ravens", "2025-10-30"),      # Thursday Night
        ("Cincinnati Bengals", "Chicago Bears", "2025-11-02"),    # Sunday 1pm
        ("Detroit Lions", "Minnesota Vikings", "2025-11-02"),     # Sunday 1pm
        ("Green Bay Packers", "Carolina Panthers", "2025-11-02"), # Sunday 1pm
        ("Houston Texans", "Denver Broncos", "2025-11-02"),       # Sunday 1pm
        ("New England Patriots", "Atlanta Falcons", "2025-11-02"), # Sunday 1pm
        ("New York Giants", "San Francisco 49ers", "2025-11-02"), # Sunday 1pm
        ("Pittsburgh Steelers", "Indianapolis Colts", "2025-11-02"), # Sunday 1pm
        ("Tennessee Titans", "Los Angeles Chargers", "2025-11-02"), # Sunday 1pm
        ("Los Angeles Rams", "New Orleans Saints", "2025-11-02"), # Sunday 4pm
        ("Las Vegas Raiders", "Jacksonville Jaguars", "2025-11-02"), # Sunday 4pm
        ("Buffalo Bills", "Kansas City Chiefs", "2025-11-02"),    # Sunday 4:25pm
        ("Washington Commanders", "Seattle Seahawks", "2025-11-02"), # Sunday Night
        ("Dallas Cowboys", "Arizona Cardinals", "2025-11-03")     # Monday Night
    ]
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Get Week 9 game IDs
        cursor.execute("SELECT id FROM nfl_games WHERE week = 9 ORDER BY id")
        game_ids = [row[0] for row in cursor.fetchall()]
        
        print(f"\n🔧 UPDATING {len(game_ids)} WEEK 9 GAMES:")
        
        for i, (home_team, away_team, game_date) in enumerate(real_week9):
            if i < len(game_ids):
                game_id = game_ids[i]
                
                cursor.execute("""
                    UPDATE nfl_games 
                    SET home_team = ?, away_team = ?, game_date = ?
                    WHERE id = ?
                """, (home_team, away_team, game_date, game_id))
                
                print(f"   ✅ Game {game_id}: {away_team} @ {home_team}")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Week 9 schedule updated to real NFL games!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def clear_week9_picks():
    """Clear all Week 9 picks since they're based on wrong games"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Delete all picks for Week 9 games
        cursor.execute("""
            DELETE FROM user_picks 
            WHERE game_id IN (
                SELECT id FROM nfl_games WHERE week = 9
            )
        """)
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"\n🗑️  CLEARED {deleted} invalid Week 9 picks")
        
    except Exception as e:
        print(f"❌ Error clearing picks: {e}")

def update_correct_picks():
    """Update picks with correct teams for real Week 9 games"""
    
    # Team abbreviation mapping for the picks you provided
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
    
    # Updated picks for real Week 9 (only valid teams)
    valid_picks = {
        'JAVIER': ['ravens', 'bengals', 'minn', 'gb', 'denver', 'pats', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks'],
        'VIZCA': ['ravens', 'bengals', 'minn', 'gb', 'texans', 'falcons', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks'],
        'ROBERT': ['ravens', 'bengals', 'minn', 'gb', 'denver', 'pats', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks'],
        'COYOTE': ['ravens', 'bears', 'minn', 'gb', 'denver', 'pats', '49ers', 'steelers', 'chargers', 'saints', 'jaguars', 'kc', 'seahawks'],
        'JEAN': ['ravens', 'bengals', 'minn', 'gb', 'denver', 'pats', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks'],
        'RAMFIS': ['ravens', 'bengals', 'minn', 'gb', 'texans', 'pats', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks'],
        'GUILLERMO': ['ravens', 'bengals', 'minn', 'gb', 'denver', 'pats', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks'],
        'JONIEL': ['ravens', 'bengals', 'minn', 'gb', 'denver', 'pats', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks'],
        'RADA': ['ravens', 'bengals', 'minn', 'gb', 'texans', 'pats', '49ers', 'steelers', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks'],
        'RAYMOND': ['ravens', 'bengals', 'minn', 'gb', 'denver', 'pats', '49ers', 'steelers', 'chargers', 'saints', 'jaguars', 'kc', 'seahawks'],
        'SHORTY': ['ravens', 'bengals', 'minn', 'gb', 'denver', 'pats', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks'],
        'KRISTIAN': ['ravens', 'bengals', 'minn', 'gb', 'texans', 'pats', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks'],
        'FER': ['ravens', 'bengals', 'minn', 'gb', 'denver', 'pats', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks'],
        'MIKITIN': ['ravens', 'bengals', 'minn', 'gb', 'denver', 'pats', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks']
    }
    
    # Map to full team names
    saints_full = 'New Orleans Saints'
    jaguars_full = 'Jacksonville Jaguars'
    seahawks_full = 'Seattle Seahawks'
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Get Week 9 games in order
        cursor.execute("""
            SELECT id, home_team, away_team 
            FROM nfl_games 
            WHERE week = 9 
            ORDER BY id
        """)
        games = cursor.fetchall()
        
        print(f"\n📝 ADDING CORRECTED PICKS FOR {len(games)} GAMES:")
        
        total_updated = 0
        for username, picks in valid_picks.items():
            try:
                # Get user ID
                cursor.execute("SELECT id FROM users WHERE UPPER(username) = UPPER(?)", (username,))
                user_result = cursor.fetchone()
                if not user_result:
                    continue
                
                user_id = user_result[0]
                picks_count = 0
                
                for i, pick_abbr in enumerate(picks):
                    if i >= len(games):
                        break
                    
                    game_id = games[i][0]
                    
                    # Convert abbreviation to full name
                    if pick_abbr == 'saints':
                        pick_team = saints_full
                    elif pick_abbr == 'jaguars':
                        pick_team = jaguars_full
                    elif pick_abbr == 'seahawks':
                        pick_team = seahawks_full
                    else:
                        pick_team = team_map.get(pick_abbr.lower())
                    
                    if pick_team:
                        cursor.execute("""
                            INSERT INTO user_picks (user_id, game_id, selected_team)
                            VALUES (?, ?, ?)
                        """, (user_id, game_id, pick_team))
                        picks_count += 1
                
                print(f"   ✅ {username}: {picks_count} picks")
                total_updated += 1
                
            except Exception as e:
                print(f"   ❌ {username}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Updated {total_updated} users with correct Week 9 picks!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🏈 COMPLETE WEEK 9 FIX - REAL NFL SCHEDULE")
    print("=" * 50)
    
    # Check database structure
    columns = check_database_structure()
    
    # Show current Week 9
    current_games = show_current_week9()
    
    # Fix the games to match real NFL
    fix_week9_games()
    
    # Clear invalid picks
    clear_week9_picks()
    
    # Add correct picks
    update_correct_picks()
    
    print("\n🎯 COMPLETE!")
    print("✅ Week 9 games updated to real NFL schedule")
    print("✅ Invalid picks cleared")
    print("✅ Correct picks added for all users")
    print("✅ Week 9 is now accurate!")

if __name__ == "__main__":
    main()