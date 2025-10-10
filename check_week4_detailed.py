#!/usr/bin/env python3
"""
Quick check for Week 4 games and New England status
"""

import sqlite3
from datetime import datetime

def check_week4():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("=== WEEK 4 ANALYSIS ===")
    print(f"Current time: {datetime.now()}")
    print()
    
    # Check if Week 4 exists
    cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 4 AND year = 2025')
    week4_count = cursor.fetchone()[0]
    print(f"Week 4 games in database: {week4_count}")
    
    if week4_count == 0:
        print("❌ NO WEEK 4 GAMES FOUND!")
        print("\nAvailable weeks:")
        cursor.execute('SELECT DISTINCT week, year, COUNT(*) FROM nfl_games GROUP BY week, year ORDER BY year DESC, week DESC')
        weeks = cursor.fetchall()
        for week, year, count in weeks:
            print(f"  Week {week}, {year}: {count} games")
        conn.close()
        return
    
    # Check all Week 4 games
    print(f"\n📊 All Week 4 games:")
    cursor.execute('''
        SELECT id, away_team, home_team, is_final, home_score, away_score, is_monday_night
        FROM nfl_games 
        WHERE week = 4 AND year = 2025 
        ORDER BY id
    ''')
    games = cursor.fetchall()
    
    for game in games:
        game_id, away, home, is_final, h_score, a_score, is_mnf = game
        status = "FINAL" if is_final else "SCHEDULED"
        mnf_marker = " (MNF)" if is_mnf else ""
        if is_final and h_score is not None and a_score is not None:
            score = f"{away} {a_score} - {h_score} {home}"
        else:
            score = f"{away} @ {home} (TBD)"
        print(f"  {game_id}: {score} - {status}{mnf_marker}")
    
    # Look for New England specifically
    print(f"\n🔍 New England games in Week 4:")
    ne_games = [g for g in games if 'NE' in [g[1], g[2]]]
    
    if ne_games:
        for game in ne_games:
            game_id, away, home, is_final, h_score, a_score, is_mnf = game
            status = "FINAL" if is_final else "SCHEDULED"
            if is_final and h_score is not None and a_score is not None:
                score = f"{away} {a_score} - {h_score} {home}"
            else:
                score = f"{away} @ {home}"
            print(f"  ✅ {game_id}: {score} - {status}")
    else:
        print("  ❌ No New England games found in Week 4")
        print("  Checking for alternative team names...")
        # Check for other possible NE representations
        for game in games:
            game_id, away, home, is_final, h_score, a_score, is_mnf = game
            if 'Patriots' in away or 'Patriots' in home or 'New England' in away or 'New England' in home:
                print(f"    Found: {away} @ {home}")
    
    # Check leaderboard availability
    print(f"\n📈 Leaderboard analysis:")
    cursor.execute('''
        SELECT COUNT(*) as total_games,
               SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games,
               SUM(CASE WHEN game_date < datetime('now') OR is_final = 1 THEN 1 ELSE 0 END) as available_games
        FROM nfl_games 
        WHERE week = 4 AND year = 2025
    ''')
    stats = cursor.fetchone()
    total, final, available = stats
    
    print(f"  Total games: {total}")
    print(f"  Final games: {final}")
    print(f"  Available for leaderboard: {available}")
    print(f"  Leaderboard should show: {'YES' if available > 0 else 'NO'}")
    
    # Check user picks
    cursor.execute('''
        SELECT COUNT(*) as total_picks,
               COUNT(DISTINCT u.username) as users_with_picks
        FROM user_picks p
        JOIN nfl_games g ON p.game_id = g.id
        JOIN users u ON p.user_id = u.id
        WHERE g.week = 4 AND g.year = 2025 AND u.is_admin = 0
    ''')
    picks_stats = cursor.fetchone()
    print(f"  Total picks made: {picks_stats[0]}")
    print(f"  Users with picks: {picks_stats[1]}")
    
    conn.close()

if __name__ == "__main__":
    check_week4()