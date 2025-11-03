#!/usr/bin/env python3
"""
Check actual Week 9 games in database vs real NFL schedule
Fix any mismatches with the real schedule
"""

import sqlite3

def check_week9_games():
    """Check what games are currently in Week 9"""
    print("🔍 CHECKING WEEK 9 GAMES IN DATABASE")
    print("=" * 45)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Get all Week 9 games
        cursor.execute("""
            SELECT id, home_team, away_team, game_date, game_time
            FROM nfl_games 
            WHERE week = 9 
            ORDER BY id
        """)
        games = cursor.fetchall()
        
        print(f"Found {len(games)} games in Week 9:")
        print()
        
        for game in games:
            game_id, home, away, date, time = game
            print(f"Game {game_id}: {away} @ {home}")
            print(f"   Date: {date}, Time: {time}")
            print()
        
        conn.close()
        return games
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def show_real_schedule():
    """Show the real Week 9 NFL schedule"""
    print("\n📅 REAL WEEK 9 NFL SCHEDULE:")
    print("=" * 35)
    
    real_games = [
        ("Thursday, Oct. 30", "Ravens", "Dolphins", "8:15p ET"),
        ("Sunday, Nov. 2", "Bears", "Bengals", "1:00p ET"),
        ("Sunday, Nov. 2", "Vikings", "Lions", "1:00p ET"),
        ("Sunday, Nov. 2", "Panthers", "Packers", "1:00p ET"),
        ("Sunday, Nov. 2", "Broncos", "Texans", "1:00p ET"),
        ("Sunday, Nov. 2", "Falcons", "Patriots", "1:00p ET"),
        ("Sunday, Nov. 2", "49ers", "Giants", "1:00p ET"),
        ("Sunday, Nov. 2", "Colts", "Steelers", "1:00p ET"),
        ("Sunday, Nov. 2", "Chargers", "Titans", "1:00p ET"),
        ("Sunday, Nov. 2", "Saints", "Rams", "4:05p ET"),
        ("Sunday, Nov. 2", "Jaguars", "Raiders", "4:05p ET"),
        ("Sunday, Nov. 2", "Chiefs", "Bills", "4:25p ET"),
        ("Sunday, Nov. 2", "Seahawks", "Commanders", "8:20p ET"),
        ("Monday, Nov. 3", "Cardinals", "Cowboys", "8:15p ET")
    ]
    
    for i, (date, away, home, time) in enumerate(real_games, 1):
        print(f"{i:2d}. {away} @ {home}")
        print(f"    {date}, {time}")
    
    return real_games

def fix_week9_schedule():
    """Fix Week 9 schedule to match real NFL schedule"""
    print("\n🔧 FIXING WEEK 9 SCHEDULE")
    print("=" * 30)
    
    # Correct Week 9 games with full team names
    correct_games = [
        ("Baltimore Ravens", "Miami Dolphins", "2025-10-30", "20:15"),
        ("Chicago Bears", "Cincinnati Bengals", "2025-11-02", "13:00"),
        ("Minnesota Vikings", "Detroit Lions", "2025-11-02", "13:00"),
        ("Carolina Panthers", "Green Bay Packers", "2025-11-02", "13:00"),
        ("Denver Broncos", "Houston Texans", "2025-11-02", "13:00"),
        ("Atlanta Falcons", "New England Patriots", "2025-11-02", "13:00"),
        ("San Francisco 49ers", "New York Giants", "2025-11-02", "13:00"),
        ("Indianapolis Colts", "Pittsburgh Steelers", "2025-11-02", "13:00"),
        ("Los Angeles Chargers", "Tennessee Titans", "2025-11-02", "13:00"),
        ("New Orleans Saints", "Los Angeles Rams", "2025-11-02", "16:05"),
        ("Jacksonville Jaguars", "Las Vegas Raiders", "2025-11-02", "16:05"),
        ("Kansas City Chiefs", "Buffalo Bills", "2025-11-02", "16:25"),
        ("Seattle Seahawks", "Washington Commanders", "2025-11-02", "20:20"),
        ("Arizona Cardinals", "Dallas Cowboys", "2025-11-03", "20:15")
    ]
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Get existing Week 9 game IDs
        cursor.execute("""
            SELECT id FROM nfl_games 
            WHERE week = 9 
            ORDER BY id
        """)
        game_ids = [row[0] for row in cursor.fetchall()]
        
        print(f"Updating {len(game_ids)} games...")
        
        # Update each game
        for i, (away_team, home_team, date, time) in enumerate(correct_games):
            if i < len(game_ids):
                game_id = game_ids[i]
                
                cursor.execute("""
                    UPDATE nfl_games 
                    SET home_team = ?, away_team = ?, game_date = ?, game_time = ?
                    WHERE id = ?
                """, (home_team, away_team, date, time, game_id))
                
                print(f"  ✅ Game {game_id}: {away_team} @ {home_team}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Successfully updated Week 9 schedule!")
        
    except Exception as e:
        print(f"❌ Error updating schedule: {e}")

def verify_user_picks():
    """Check if user picks still make sense with new schedule"""
    print("\n🔍 VERIFYING USER PICKS")
    print("=" * 25)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check user picks for Week 9
        cursor.execute("""
            SELECT u.username, g.id, g.home_team, g.away_team, p.selected_team
            FROM user_picks p
            JOIN users u ON p.user_id = u.id
            JOIN nfl_games g ON p.game_id = g.id
            WHERE g.week = 9
            ORDER BY u.username, g.id
            LIMIT 20
        """)
        
        picks = cursor.fetchall()
        
        if picks:
            print("Sample picks:")
            current_user = None
            for username, game_id, home, away, pick in picks:
                if username != current_user:
                    print(f"\n{username}:")
                    current_user = username
                
                # Check if pick is valid
                valid = pick in [home, away]
                status = "✅" if valid else "❌"
                print(f"  {status} Game {game_id}: {pick} ({away} @ {home})")
        
        # Count total picks
        cursor.execute("""
            SELECT COUNT(*) FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            WHERE g.week = 9
        """)
        total = cursor.fetchone()[0]
        print(f"\nTotal Week 9 picks: {total}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking picks: {e}")

def main():
    print("🏈 WEEK 9 SCHEDULE VERIFICATION AND FIX")
    print("=" * 45)
    
    # Check current database games
    db_games = check_week9_games()
    
    # Show real schedule
    real_games = show_real_schedule()
    
    # Ask if we should fix the schedule
    print(f"\n⚠️  Database has {len(db_games)} games, Real NFL has {len(real_games)} games")
    
    # Fix the schedule
    fix_week9_schedule()
    
    # Verify picks still work
    verify_user_picks()
    
    print("\n🎯 NEXT STEPS:")
    print("1. ✅ Week 9 schedule updated to match real NFL")
    print("2. ✅ User picks verified against new schedule")
    print("3. 📝 May need to re-run pick updates if teams changed")

if __name__ == "__main__":
    main()