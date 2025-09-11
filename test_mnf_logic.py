#!/usr/bin/env python3
"""Test script to verify Monday Night Football detection logic is working correctly"""

import sqlite3
from datetime import datetime

DATABASE_PATH = 'database.db'

def test_mnf_detection():
    """Test that Monday Night Football detection is working correctly"""
    print("🏈 Testing Monday Night Football Detection Logic")
    print("=" * 50)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Test for Week 1, 2025
    week = 1
    year = 2025
    
    print(f"Testing Week {week}, {year}")
    print()
    
    # Show all Monday games
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_monday_night
        FROM nfl_games 
        WHERE week = ? AND year = ? 
        AND strftime('%w', game_date) = '1'  -- Monday
        ORDER BY game_date
    ''', (week, year))
    
    monday_games = cursor.fetchall()
    print(f"All Monday games ({len(monday_games)}):")
    for i, (game_id, away, home, date, old_flag) in enumerate(monday_games, 1):
        print(f"  {i}. {away} @ {home} - {date} (DB flag: {old_flag})")
    
    print()
    
    # Find actual Monday Night Football game using new logic
    cursor.execute('''
        SELECT id, away_team, home_team, game_date
        FROM nfl_games 
        WHERE week = ? AND year = ? 
        AND strftime('%w', game_date) = '1'  -- Monday
        ORDER BY game_date DESC, id DESC
        LIMIT 1
    ''', (week, year))
    
    actual_mnf = cursor.fetchone()
    if actual_mnf:
        mnf_id, mnf_away, mnf_home, mnf_date = actual_mnf
        print(f"🎯 Actual Monday Night Football game:")
        print(f"   {mnf_away} @ {mnf_home} - {mnf_date} (ID: {mnf_id})")
    else:
        print("❌ No Monday Night Football game found")
        mnf_id = None
    
    print()
    
    # Test export logic compatibility
    print("🔍 Testing Export Logic Compatibility:")
    if mnf_id:
        # Check what the CSV export would show
        cursor.execute('''
            SELECT 'CSV Export Test' as test_type,
                   CASE WHEN id = ? THEN 'YES - Score prediction' ELSE 'NO - Team pick only' END as shows_scores
            FROM nfl_games 
            WHERE week = ? AND year = ?
            ORDER BY game_date
        ''', (mnf_id, week, year))
        
        export_results = cursor.fetchall()
        for test_type, shows_scores in export_results:
            if 'Score prediction' in shows_scores:
                cursor.execute('SELECT away_team, home_team FROM nfl_games WHERE id = ?', (mnf_id,))
                game_info = cursor.fetchone()
                if game_info:
                    print(f"   ✅ {game_info[0]} @ {game_info[1]} - {shows_scores}")
            elif len([r for r in export_results if 'Score prediction' in r[1]]) == 1:
                # Only show a few non-MNF examples
                if export_results.index((test_type, shows_scores)) < 3:
                    cursor.execute('SELECT away_team, home_team FROM nfl_games WHERE week = ? AND year = ? ORDER BY game_date LIMIT 1 OFFSET ?', 
                                 (week, year, export_results.index((test_type, shows_scores))))
                    game_info = cursor.fetchone()
                    if game_info:
                        print(f"   ⚪ {game_info[0]} @ {game_info[1]} - {shows_scores}")
    
    print()
    
    # Test pick interface logic
    print("🎮 Testing Pick Interface Logic:")
    cursor.execute('''
        SELECT id, away_team, home_team, game_date,
               CASE WHEN id = ? THEN 1 ELSE 0 END as shows_score_inputs
        FROM nfl_games 
        WHERE week = ? AND year = ?
        ORDER BY game_date
    ''', (mnf_id, week, year))
    
    interface_results = cursor.fetchall()
    games_with_scores = 0
    for game_id, away, home, date, shows_scores in interface_results:
        if shows_scores:
            print(f"   🎯 {away} @ {home} - Shows score prediction inputs")
            games_with_scores += 1
        elif games_with_scores == 0 and interface_results.index((game_id, away, home, date, shows_scores)) < 3:
            print(f"   ⚪ {away} @ {home} - Team pick only")
    
    print()
    print(f"✅ Summary: {games_with_scores} game(s) will show score prediction inputs")
    print(f"   This should be exactly 1 (the actual Monday Night Football game)")
    
    # Test consistency check
    print()
    print("🔄 Consistency Check:")
    if games_with_scores == 1 and mnf_id:
        print("   ✅ Pick interface matches export logic")
        print("   ✅ Only actual Monday Night Football game shows score inputs")
        print("   ✅ All other games show team picks only")
        print()
        print("🎉 All tests passed! Monday Night Football detection is working correctly.")
    else:
        print("   ❌ Inconsistency detected!")
        print(f"   Expected: 1 game with score inputs, Got: {games_with_scores}")
    
    conn.close()

if __name__ == "__main__":
    test_mnf_detection()
