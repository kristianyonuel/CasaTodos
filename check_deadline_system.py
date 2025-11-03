#!/usr/bin/env python3
"""
Investigate deadline system causing leaderboard to show 0 correct picks
"""

import sqlite3
from datetime import datetime, timedelta

def check_deadline_system():
    """Check deadline system and why scores are hidden"""
    
    print("🕒 DEADLINE SYSTEM INVESTIGATION")
    print("=" * 45)
    
    print(f"📅 Current Date: {datetime.now().strftime('%A, %B %d, %Y')}")
    print(f"⏰ Current Time: {datetime.now().strftime('%H:%M:%S')}")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check Week 9 games and their deadlines
    print(f"\n🏈 WEEK 9 GAMES AND DEADLINES:")
    cursor.execute("""
        SELECT game_id, away_team, home_team, game_date, 
               is_monday_night, is_thursday_night, is_sunday_night,
               game_status, is_final
        FROM nfl_games 
        WHERE week = 9 
        ORDER BY game_date
    """)
    
    games = cursor.fetchall()
    monday_games = []
    
    for game_id, away, home, date, is_mon, is_thu, is_sun, status, is_final in games:
        day_type = ""
        if is_mon:
            day_type = "🌙 MONDAY NIGHT"
            monday_games.append((game_id, away, home, date))
        elif is_thu:
            day_type = "🏈 THURSDAY NIGHT"
        elif is_sun:
            day_type = "🌅 SUNDAY NIGHT"
        else:
            day_type = "🕐 REGULAR"
        
        print(f"   {away} @ {home}")
        print(f"      Date: {date} | Type: {day_type} | Status: {status} | Final: {is_final}")
    
    # Check if there are deadline rules
    print(f"\n⏰ DEADLINE ANALYSIS:")
    if monday_games:
        print(f"   Monday Night Games Found: {len(monday_games)}")
        for game_id, away, home, date in monday_games:
            print(f"   - {away} @ {home} ({date})")
    
    # Check what the web app might be checking
    print(f"\n🔍 POSSIBLE DEADLINE LOGIC:")
    print("The web app likely has logic like:")
    print("- 'Hide scores until all Week 9 games are completed'")
    print("- 'Hide scores until Monday Night Football ends'")
    print("- 'Hide scores until Sunday deadline passes'")
    
    # Check current database scoring state
    cursor.execute("""
        SELECT COUNT(*) as total_games,
               SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games
        FROM nfl_games 
        WHERE week = 9
    """)
    
    total, final = cursor.fetchone()
    print(f"\n📊 GAME COMPLETION STATUS:")
    print(f"   Total Week 9 games: {total}")
    print(f"   Games finalized: {final}")
    print(f"   Completion: {final}/{total} ({(final/total*100):.1f}%)")
    
    # Check scoring state
    cursor.execute("""
        SELECT COUNT(*) as scored_picks
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND up.is_correct IS NOT NULL
    """)
    
    scored = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*) as total_picks
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9
    """)
    
    total_picks = cursor.fetchone()[0]
    print(f"\n🎯 PICK SCORING STATUS:")
    print(f"   Total picks: {total_picks}")
    print(f"   Picks scored: {scored}")
    print(f"   Scoring: {scored}/{total_picks} ({(scored/total_picks*100):.1f}%)")
    
    # Check for any deadline-related tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%deadline%'")
    deadline_tables = cursor.fetchall()
    
    if deadline_tables:
        print(f"\n📋 DEADLINE-RELATED TABLES:")
        for table in deadline_tables:
            print(f"   - {table[0]}")
    
    # Look for potential deadline configuration
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n🔧 NEXT STEPS:")
    print("1. Check app.py for deadline logic")
    print("2. Look for deadline management code")
    print("3. Check if there's a 'reveal scores' function")
    print("4. Monday Night game might need to finish first")
    
    conn.close()

if __name__ == "__main__":
    check_deadline_system()