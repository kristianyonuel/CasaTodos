#!/usr/bin/env python3
"""
Check what the admin 'Set User Picks' interface is looking for
This should match what the admin area expects to see
"""

import sqlite3

def check_admin_picks_interface():
    """Check what data the admin interface expects for setting picks"""
    
    print("🔍 ADMIN 'SET USER PICKS' INTERFACE CHECK")
    print("=" * 50)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check what the admin interface might be querying
    print("📅 CHECKING WHAT ADMIN INTERFACE EXPECTS:")
    
    # 1. Check if there are any admin-specific settings
    cursor.execute("SELECT * FROM league_settings WHERE setting_name LIKE '%admin%' OR setting_name LIKE '%pick%'")
    admin_settings = cursor.fetchall()
    if admin_settings:
        print("Admin-related settings:")
        for setting in admin_settings:
            print(f"  {setting[2]}: {setting[3]}")
    
    # 2. Check what games are available for pick setting
    print(f"\n🏈 GAMES AVAILABLE FOR PICKS:")
    cursor.execute("""
        SELECT game_id, week, year, away_team, home_team, game_date, is_final
        FROM nfl_games 
        WHERE week = 9 AND year = 2025
        ORDER BY game_date
    """)
    games = cursor.fetchall()
    
    print(f"Found {len(games)} Week 9 games:")
    for i, (game_id, week, year, away, home, date, is_final) in enumerate(games, 1):
        status = "FINAL" if is_final else "PENDING"
        print(f"  {i:2d}. {game_id} - {away} @ {home} ({status})")
    
    # 3. Check what picks already exist (what admin sees)
    print(f"\n📝 EXISTING PICKS (Admin View):")
    cursor.execute("""
        SELECT u.username, COUNT(up.game_id) as pick_count,
               MIN(g.week) as min_week, MAX(g.week) as max_week
        FROM users u
        LEFT JOIN user_picks up ON u.id = up.user_id
        LEFT JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
        GROUP BY u.id, u.username
        ORDER BY u.username
    """)
    user_picks = cursor.fetchall()
    
    if user_picks:
        print("User picks count for Week 9:")
        for username, pick_count, min_week, max_week in user_picks:
            print(f"  {username:12s}: {pick_count:2d} picks")
    else:
        print("❌ No user picks found for Week 9")
    
    # 4. Check if admin interface looks at a different table or field
    print(f"\n🔍 POTENTIAL ADMIN INTERFACE ISSUES:")
    
    # Check if there's a different picks table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%pick%'")
    pick_tables = cursor.fetchall()
    print("Pick-related tables:")
    for table in pick_tables:
        print(f"  {table[0]}")
    
    # Check if there's an admin_picks or similar table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [row[0] for row in cursor.fetchall()]
    admin_tables = [t for t in all_tables if 'admin' in t.lower()]
    if admin_tables:
        print("Admin-related tables:")
        for table in admin_tables:
            print(f"  {table}")
    
    # 5. Check user_picks table structure
    print(f"\n📋 USER_PICKS TABLE STRUCTURE:")
    cursor.execute("PRAGMA table_info(user_picks)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # 6. Check if there are any constraints or issues
    print(f"\n⚠️  POTENTIAL ISSUES:")
    
    # Check for duplicate picks
    cursor.execute("""
        SELECT user_id, game_id, COUNT(*) as count
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
        GROUP BY user_id, game_id
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    if duplicates:
        print("❌ Duplicate picks found:")
        for user_id, game_id, count in duplicates:
            print(f"  User {user_id}, Game {game_id}: {count} picks")
    else:
        print("✅ No duplicate picks")
    
    # Check for missing user-game combinations
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 9 AND year = 2025")
    total_games = cursor.fetchone()[0]
    expected_picks = total_users * total_games
    
    cursor.execute("""
        SELECT COUNT(*) FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
    """)
    actual_picks = cursor.fetchone()[0]
    
    print(f"Pick completeness: {actual_picks}/{expected_picks} ({total_users} users × {total_games} games)")
    
    if actual_picks != expected_picks:
        print("❌ Some picks are missing!")
        
        # Find which users are missing picks
        cursor.execute("""
            SELECT u.username, COUNT(up.game_id) as picks
            FROM users u
            LEFT JOIN user_picks up ON u.id = up.user_id AND up.game_id IN 
                (SELECT game_id FROM nfl_games WHERE week = 9 AND year = 2025)
            GROUP BY u.id, u.username
            HAVING COUNT(up.game_id) < ?
            ORDER BY picks
        """, (total_games,))
        missing_picks = cursor.fetchall()
        for username, picks in missing_picks:
            print(f"  {username}: only {picks}/{total_games} picks")
    
    conn.close()
    
    print(f"\n🎯 ADMIN INTERFACE DIAGNOSIS:")
    print("The admin 'Set User Picks' interface might be:")
    print("1. Looking at a different week/year")
    print("2. Using a different query than weekly leaderboard")
    print("3. Expecting data in a different format")
    print("4. Having caching issues at the Flask route level")

if __name__ == "__main__":
    check_admin_picks_interface()