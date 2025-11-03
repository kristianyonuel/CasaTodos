#!/usr/bin/env python3
"""
Check Week 9 vs Week 10 games - fix the scheduling error
"""

import sqlite3

def check_week_games(week):
    """Check what games are in a specific week"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, home_team, away_team, game_date
            FROM nfl_games 
            WHERE week = ? 
            ORDER BY id
        """, (week,))
        games = cursor.fetchall()
        
        print(f"\n📅 WEEK {week} GAMES ({len(games)} total):")
        for game in games:
            print(f"   Game {game[0]}: {game[2]} @ {game[1]} ({game[3]})")
        
        conn.close()
        return games
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def fix_week9_vs_week10():
    """Fix the Week 9/10 scheduling confusion"""
    
    # CORRECT Week 9 (Oct 30 - Nov 3, 2025)
    correct_week9 = [
        ("Miami Dolphins", "Baltimore Ravens", "2025-10-30"),        # Thursday Night
        ("Cincinnati Bengals", "Chicago Bears", "2025-11-02"),      # Sunday 1pm
        ("Detroit Lions", "Minnesota Vikings", "2025-11-02"),       # Sunday 1pm  
        ("Green Bay Packers", "Carolina Panthers", "2025-11-02"),   # Sunday 1pm
        ("Houston Texans", "Denver Broncos", "2025-11-02"),         # Sunday 1pm
        ("New England Patriots", "Atlanta Falcons", "2025-11-02"),  # Sunday 1pm
        ("New York Giants", "San Francisco 49ers", "2025-11-02"),   # Sunday 1pm
        ("Pittsburgh Steelers", "Indianapolis Colts", "2025-11-02"), # Sunday 1pm
        ("Tennessee Titans", "Los Angeles Chargers", "2025-11-02"), # Sunday 1pm
        ("Los Angeles Rams", "New Orleans Saints", "2025-11-02"),   # Sunday 4pm
        ("Las Vegas Raiders", "Jacksonville Jaguars", "2025-11-02"), # Sunday 4pm
        ("Buffalo Bills", "Kansas City Chiefs", "2025-11-02"),      # Sunday 4:25pm
        ("Washington Commanders", "Seattle Seahawks", "2025-11-02"), # Sunday Night
        ("Dallas Cowboys", "Arizona Cardinals", "2025-11-03")       # Monday Night
    ]
    
    # Week 10 would be Nov 7-10, 2025 (KC@LAR, ARI@HOU should be here)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        print("🔧 FIXING WEEK 9 SCHEDULE (14 games only):")
        
        # Get Week 9 game IDs (should only be 14 games)
        cursor.execute("SELECT id FROM nfl_games WHERE week = 9 ORDER BY id")
        week9_ids = [row[0] for row in cursor.fetchall()]
        
        # Update only the first 14 games to be Week 9
        for i, (home_team, away_team, game_date) in enumerate(correct_week9):
            if i < len(week9_ids):
                game_id = week9_ids[i]
                
                cursor.execute("""
                    UPDATE nfl_games 
                    SET home_team = ?, away_team = ?, game_date = ?
                    WHERE id = ?
                """, (home_team, away_team, game_date, game_id))
                
                print(f"   ✅ Game {game_id}: {away_team} @ {home_team} ({game_date})")
        
        # Move the extra games (KC@LAR, ARI@HOU) to Week 10
        if len(week9_ids) > 14:
            extra_games = week9_ids[14:]  # Games 15, 16 should be Week 10
            
            print(f"\n🔄 MOVING {len(extra_games)} GAMES TO WEEK 10:")
            for game_id in extra_games:
                cursor.execute("""
                    UPDATE nfl_games 
                    SET week = 10
                    WHERE id = ?
                """, (game_id,))
                
                # Get the game info
                cursor.execute("SELECT home_team, away_team FROM nfl_games WHERE id = ?", (game_id,))
                game_info = cursor.fetchone()
                if game_info:
                    print(f"   ✅ Game {game_id}: {game_info[1]} @ {game_info[0]} → Week 10")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Week 9/10 schedule fixed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def clear_invalid_picks():
    """Clear picks for games that moved to Week 10"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Clear all Week 9 picks (we'll re-add the correct ones)
        cursor.execute("""
            DELETE FROM user_picks 
            WHERE game_id IN (
                SELECT id FROM nfl_games WHERE week = 9
            )
        """)
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"\n🗑️  CLEARED {deleted} Week 9 picks (will re-add correct ones)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def add_correct_week9_picks():
    """Add picks for the correct 14 Week 9 games"""
    
    # User picks for the REAL 14 Week 9 games (no KC@LAR, no ARI@HOU)
    users_picks = {
        'JAVIER': ['ravens', 'bears', 'minn', 'panthers', 'broncos', 'falcons', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'chiefs', 'seahawks', 'cardinals'],
        'VIZCA': ['ravens', 'bears', 'minn', 'panthers', 'texans', 'falcons', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'chiefs', 'seahawks', 'cardinals'],
        'ROBERT': ['ravens', 'bears', 'minn', 'panthers', 'broncos', 'falcons', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'chiefs', 'seahawks', 'cardinals'],
        'COYOTE': ['ravens', 'bengals', 'minn', 'panthers', 'broncos', 'falcons', '49ers', 'steelers', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks', 'cardinals'],
        'JEAN': ['ravens', 'bears', 'minn', 'panthers', 'broncos', 'falcons', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'chiefs', 'seahawks', 'cardinals'],
        'RAMFIS': ['ravens', 'bears', 'minn', 'panthers', 'texans', 'falcons', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'chiefs', 'seahawks', 'cardinals'],
        'GUILLERMO': ['ravens', 'bears', 'minn', 'panthers', 'broncos', 'falcons', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'chiefs', 'seahawks', 'cardinals'],
        'JONIEL': ['ravens', 'bears', 'minn', 'panthers', 'broncos', 'falcons', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'chiefs', 'seahawks', 'cardinals'],
        'RADA': ['ravens', 'bears', 'minn', 'panthers', 'texans', 'falcons', '49ers', 'steelers', 'chargers', 'saints', 'jaguars', 'chiefs', 'seahawks', 'cardinals'],
        'RAYMOND': ['ravens', 'bears', 'minn', 'panthers', 'broncos', 'falcons', '49ers', 'steelers', 'chargers', 'saints', 'jaguars', 'bills', 'seahawks', 'cardinals'],
        'SHORTY': ['ravens', 'bears', 'minn', 'panthers', 'broncos', 'falcons', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'chiefs', 'seahawks', 'cardinals'],
        'KRISTIAN': ['ravens', 'bears', 'minn', 'panthers', 'texans', 'falcons', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'chiefs', 'seahawks', 'cardinals'],
        'FER': ['ravens', 'bears', 'minn', 'panthers', 'broncos', 'falcons', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'chiefs', 'seahawks', 'cardinals'],
        'MIKITIN': ['ravens', 'bears', 'minn', 'panthers', 'broncos', 'falcons', '49ers', 'colts', 'chargers', 'saints', 'jaguars', 'chiefs', 'seahawks', 'cardinals']
    }
    
    team_map = {
        'ravens': 'Baltimore Ravens', 'bears': 'Chicago Bears',
        'minn': 'Minnesota Vikings', 'panthers': 'Carolina Panthers',
        'broncos': 'Denver Broncos', 'texans': 'Houston Texans',
        'falcons': 'Atlanta Falcons', '49ers': 'San Francisco 49ers',
        'colts': 'Indianapolis Colts', 'chargers': 'Los Angeles Chargers',
        'saints': 'New Orleans Saints', 'jaguars': 'Jacksonville Jaguars',
        'chiefs': 'Kansas City Chiefs', 'bills': 'Buffalo Bills',
        'seahawks': 'Seattle Seahawks', 'cardinals': 'Arizona Cardinals'
    }
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Get Week 9 games (should be 14 now)
        cursor.execute("""
            SELECT id, home_team, away_team 
            FROM nfl_games 
            WHERE week = 9 
            ORDER BY id
        """)
        games = cursor.fetchall()
        
        print(f"\n📝 ADDING PICKS FOR {len(games)} WEEK 9 GAMES:")
        
        total_updated = 0
        for username, picks in users_picks.items():
            try:
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
        
        print(f"\n✅ Added picks for {total_updated} users!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🏈 FIXING WEEK 9/10 SCHEDULE CONFUSION")
    print("=" * 45)
    
    # Check current Week 9
    print("BEFORE FIX:")
    week9_games = check_week_games(9)
    week10_games = check_week_games(10)
    
    # Fix the schedule
    fix_week9_vs_week10()
    
    # Clear invalid picks
    clear_invalid_picks()
    
    # Add correct picks
    add_correct_week9_picks()
    
    # Show final result
    print("\nAFTER FIX:")
    check_week_games(9)
    check_week_games(10)
    
    print("\n🎯 FIXED!")
    print("✅ Week 9: 14 games (Oct 30 - Nov 3)")
    print("✅ Week 10: Remaining games (Nov 7-10)")
    print("✅ All picks corrected")

if __name__ == "__main__":
    main()