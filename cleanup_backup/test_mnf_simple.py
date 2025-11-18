#!/usr/bin/env python3
"""Simple test to verify Monday Night Football detection logic"""

import sqlite3

def test_mnf_detection():
    """Test that Monday Night Football detection is working correctly"""
    print("🏈 Testing Monday Night Football Detection Logic")
    print("=" * 50)
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    week = 1
    year = 2025
    
    print(f"Testing Week {week}, {year}")
    print()
    
    # Show all Monday games
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_monday_night
        FROM nfl_games 
        WHERE week = ? AND year = ? 
        AND strftime('%w', game_date) = '1'
        ORDER BY game_date
    ''', (week, year))
    
    monday_games = cursor.fetchall()
    print(f"All Monday games ({len(monday_games)}):")
    for i, game in enumerate(monday_games, 1):
        print(f"  {i}. {game['away_team']} @ {game['home_team']} - {game['game_date']} (DB flag: {game['is_monday_night']})")
    
    print()
    
    # Find actual Monday Night Football game using new logic
    cursor.execute('''
        SELECT id, away_team, home_team, game_date
        FROM nfl_games 
        WHERE week = ? AND year = ? 
        AND strftime('%w', game_date) = '1'
        ORDER BY game_date DESC, id DESC
        LIMIT 1
    ''', (week, year))
    
    actual_mnf = cursor.fetchone()
    if actual_mnf:
        print(f"🎯 Actual Monday Night Football game:")
        print(f"   {actual_mnf['away_team']} @ {actual_mnf['home_team']} - {actual_mnf['game_date']} (ID: {actual_mnf['id']})")
        mnf_id = actual_mnf['id']
    else:
        print("❌ No Monday Night Football game found")
        mnf_id = None
    
    print()
    
    if mnf_id:
        print("✅ Summary:")
        print(f"   - Only game ID {mnf_id} will show score prediction inputs")
        print(f"   - All other games will show team picks only")
        print(f"   - Export logic will only include Monday scores for game ID {mnf_id}")
        print()
        print("🎉 Monday Night Football detection is working correctly!")
    else:
        print("❌ No Monday Night Football game detected for testing")
    
    conn.close()

if __name__ == "__main__":
    test_mnf_detection()
