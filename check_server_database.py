#!/usr/bin/env python3
"""
Server-side script to check and fix Week 9 picks visibility
Run this directly on the Azure VM to diagnose admin interface issues
"""

import sqlite3
import os

def check_server_database():
    """Check the database on the server side"""
    
    print("🔍 SERVER-SIDE DATABASE CHECK FOR WEEK 9")
    print("=" * 50)
    
    # Check both possible database locations
    db_paths = [
        '/home/casa/CasaTodos/nfl_fantasy.db',
        './nfl_fantasy.db',
        'nfl_fantasy.db',
        '/home/casa/nfl_fantasy.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            print(f"✅ Found database: {path}")
            break
    
    if not db_path:
        print("❌ Database not found at any expected location!")
        print("Checking current directory...")
        files = os.listdir('.')
        db_files = [f for f in files if f.endswith('.db')]
        print(f"Database files found: {db_files}")
        return
    
    # Check database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check users table
    print(f"\n👥 USERS CHECK:")
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"   Total users: {user_count}")
    
    # Check Week 9 games
    print(f"\n🏈 WEEK 9 GAMES CHECK:")
    cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 9")
    game_count = cursor.fetchone()[0]
    print(f"   Week 9 games: {game_count}")
    
    if game_count > 0:
        cursor.execute("SELECT game_id, away_team, home_team FROM nfl_games WHERE week = 9 LIMIT 3")
        games = cursor.fetchall()
        for game_id, away, home in games:
            print(f"   {game_id}: {away} @ {home}")
    
    # Check Week 9 picks
    print(f"\n📝 WEEK 9 PICKS CHECK:")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9
    """)
    pick_count = cursor.fetchone()[0]
    print(f"   Week 9 picks: {pick_count}")
    
    # Check specific user
    print(f"\n👤 COYOTE PICKS CHECK:")
    cursor.execute("""
        SELECT g.away_team, g.home_team, up.selected_team
        FROM user_picks up
        JOIN users u ON up.user_id = u.id
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE u.username = 'coyote' AND g.week = 9
        LIMIT 5
    """)
    
    coyote_picks = cursor.fetchall()
    print(f"   COYOTE has {len(coyote_picks)} Week 9 picks:")
    for away, home, pick in coyote_picks:
        print(f"     {away} @ {home}: {pick}")
    
    # Check if there's a year filter issue
    print(f"\n📅 YEAR FILTER CHECK:")
    cursor.execute("SELECT DISTINCT year FROM nfl_games WHERE week = 9")
    years = cursor.fetchall()
    print(f"   Years with Week 9 games: {[y[0] for y in years]}")
    
    # Check with year 2025 specifically
    cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 9 AND year = 2025")
    games_2025 = cursor.fetchone()[0]
    print(f"   Week 9 games for year 2025: {games_2025}")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
    """)
    picks_2025 = cursor.fetchone()[0]
    print(f"   Week 9 picks for year 2025: {picks_2025}")
    
    # Check what the admin interface query might be using
    print(f"\n🔧 ADMIN INTERFACE QUERY TEST:")
    
    # Test typical admin query
    cursor.execute("""
        SELECT u.username, COUNT(up.id) as pick_count
        FROM users u
        LEFT JOIN user_picks up ON u.id = up.user_id
        LEFT JOIN nfl_games g ON up.game_id = g.game_id AND g.week = 9 AND g.year = 2025
        GROUP BY u.username
        ORDER BY u.username
    """)
    
    admin_results = cursor.fetchall()
    print("   Admin-style query results:")
    for username, pick_count in admin_results:
        print(f"     {username}: {pick_count} picks")
    
    # Check if the issue is with the Flask app's current week setting
    print(f"\n⚙️ FLASK APP SETTINGS CHECK:")
    try:
        cursor.execute("SELECT setting_name, setting_value FROM league_settings WHERE setting_name IN ('current_week', 'current_year')")
        settings = cursor.fetchall()
        if settings:
            for name, value in settings:
                print(f"   {name}: {value}")
        else:
            print("   No current_week/current_year settings found")
    except:
        print("   league_settings table not found or accessible")
    
    conn.close()
    
    print(f"\n🎯 DIAGNOSIS:")
    if pick_count > 0:
        print("   ✅ Week 9 picks exist in database")
        print("   ⚠️ Issue is likely with Flask app query or caching")
        print("   🔧 Solution: Restart Flask service")
    else:
        print("   ❌ No Week 9 picks found in database")
        print("   🔧 Solution: Re-run pick insertion script")

if __name__ == "__main__":
    check_server_database()