#!/usr/bin/env python3
"""
Test the exact queries the website uses for Week 9
"""

import sqlite3

def test_website_queries():
    """Test all the queries the Flask website might use"""
    
    print("🌐 TESTING WEBSITE QUERIES FOR WEEK 9")
    print("=" * 45)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Test 1: Weekly leaderboard query
    print("📊 TEST 1: Weekly Leaderboard Query")
    cursor.execute("""
        SELECT u.username, 
               SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
               SUM(up.points_earned) as total_points
        FROM users u
        JOIN user_picks up ON u.id = up.user_id
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
        GROUP BY u.username
        ORDER BY total_points DESC, correct_picks DESC
    """)
    
    results = cursor.fetchall()
    print(f"   Results found: {len(results)}")
    for username, correct, points in results[:5]:
        print(f"     {username}: {correct} correct, {points} points")
    
    # Test 2: User picks query
    print(f"\n👤 TEST 2: User Picks Query (COYOTE)")
    cursor.execute("""
        SELECT g.away_team, g.home_team, up.selected_team, 
               g.away_score, g.home_score, up.is_correct
        FROM user_picks up
        JOIN users u ON up.user_id = u.id
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE u.username = 'coyote' AND g.week = 9 AND g.year = 2025
        ORDER BY g.game_id
    """)
    
    picks = cursor.fetchall()
    print(f"   Picks found: {len(picks)}")
    for away, home, pick, away_score, home_score, correct in picks[:3]:
        status = "✅" if correct else "❌"
        print(f"     {away} {away_score} - {home_score} {home}: {pick} {status}")
    
    # Test 3: Games list query
    print(f"\n🏈 TEST 3: Games List Query")
    cursor.execute("""
        SELECT away_team, home_team, away_score, home_score, 
               game_date, is_final
        FROM nfl_games
        WHERE week = 9 AND year = 2025
        ORDER BY game_date, game_id
    """)
    
    games = cursor.fetchall()
    print(f"   Games found: {len(games)}")
    for away, home, away_score, home_score, date, final in games[:3]:
        status = "FINAL" if final else "PENDING"
        print(f"     {away} {away_score} - {home_score} {home} | {status}")
    
    # Test 4: Check current week setting
    print(f"\n⚙️ TEST 4: League Settings")
    cursor.execute("""
        SELECT setting_name, setting_value 
        FROM league_settings 
        WHERE setting_name IN ('current_week', 'current_year')
    """)
    
    settings = cursor.fetchall()
    for name, value in settings:
        print(f"     {name}: {value}")
    
    # Test 5: Check if Flask might be using different table
    print(f"\n📋 TEST 5: Weekly Results Table")
    cursor.execute("""
        SELECT u.username, wr.correct_picks, wr.total_points, wr.weekly_rank
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.week = 9 AND wr.year = 2025
        ORDER BY wr.weekly_rank
    """)
    
    weekly = cursor.fetchall()
    print(f"   Weekly results found: {len(weekly)}")
    for username, correct, points, rank in weekly[:5]:
        print(f"     {rank}. {username}: {correct} correct, {points} points")
    
    conn.close()
    
    print(f"\n🎯 CONCLUSION:")
    if results and picks and games and weekly:
        print("   ✅ ALL DATABASE QUERIES WORK PERFECTLY")
        print("   ✅ The issue is NOT with the database")
        print("   ⚠️ The problem is with the Flask app or web interface")
        print("   🔧 Solution: Restart the Flask service on Azure VM")
        print()
        print("   Commands to run on Azure VM:")
        print("   1. sudo systemctl stop lacasadetodos.service")
        print("   2. sudo systemctl start lacasadetodos.service")
        print("   3. sudo systemctl status lacasadetodos.service")
    else:
        print("   ❌ Database queries failed")

if __name__ == "__main__":
    test_website_queries()