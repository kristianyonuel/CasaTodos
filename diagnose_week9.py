#!/usr/bin/env python3
"""
Quick diagnostic for Week 9 display issues
"""

import sqlite3

def diagnose_week9_issues():
    """Check what's wrong with Week 9 display"""
    
    print("🔍 DIAGNOSING WEEK 9 DISPLAY ISSUES")
    print("=" * 45)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check Year 2025 specifically
    print("📅 Year 2025 check:")
    cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 9 AND year = 2025")
    games_2025 = cursor.fetchone()[0]
    print(f"   Games with year 2025: {games_2025}")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
    """)
    picks_2025 = cursor.fetchone()[0]
    print(f"   Picks with year 2025: {picks_2025}")
    
    # Check all years
    print(f"\n📊 All years in database:")
    cursor.execute("SELECT DISTINCT year FROM nfl_games ORDER BY year")
    years = cursor.fetchall()
    for year_row in years:
        year = year_row[0]
        cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE year = ? AND week = 9", (year,))
        count = cursor.fetchone()[0]
        print(f"   Year {year}: {count} Week 9 games")
    
    # Check COYOTE's picks
    print(f"\n👤 COYOTE Week 9 picks:")
    cursor.execute("""
        SELECT g.away_team, g.home_team, up.selected_team, g.year
        FROM user_picks up
        JOIN users u ON up.user_id = u.id
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE u.username = 'coyote' AND g.week = 9
        ORDER BY g.game_id
        LIMIT 5
    """)
    
    coyote_picks = cursor.fetchall()
    if coyote_picks:
        for away, home, pick, year in coyote_picks:
            print(f"   {away} @ {home}: picked {pick} (Year {year})")
    else:
        print("   ❌ No picks found for COYOTE")
    
    # Check weekly_results table
    print(f"\n📈 Weekly results check:")
    cursor.execute("SELECT COUNT(*) FROM weekly_results WHERE week = 9 AND year = 2025")
    weekly_count = cursor.fetchone()[0]
    print(f"   Weekly results for Week 9, 2025: {weekly_count}")
    
    if weekly_count > 0:
        cursor.execute("""
            SELECT u.username, wr.correct_picks, wr.total_points
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            WHERE wr.week = 9 AND wr.year = 2025
            ORDER BY wr.total_points DESC
            LIMIT 3
        """)
        
        top_results = cursor.fetchall()
        print("   Top 3 weekly results:")
        for username, correct, points in top_results:
            print(f"     {username}: {correct} correct, {points} points")
    
    # Test exact website query
    print(f"\n🌐 Testing website-style query:")
    cursor.execute("""
        SELECT u.username, 
               SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
               SUM(up.points_earned) as points
        FROM users u
        JOIN user_picks up ON u.id = up.user_id
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025 AND g.is_final = 1
        GROUP BY u.username
        ORDER BY points DESC
        LIMIT 3
    """)
    
    website_results = cursor.fetchall()
    if website_results:
        print("   Website query results:")
        for username, correct, points in website_results:
            print(f"     {username}: {correct} correct, {points} points")
    else:
        print("   ❌ Website query returned no results!")
        
        # Check why
        cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 9 AND year = 2025 AND is_final = 1")
        final_games = cursor.fetchone()[0]
        print(f"   Final games count: {final_games}")
    
    conn.close()

if __name__ == "__main__":
    diagnose_week9_issues()