#!/usr/bin/env python3
"""
Test script to verify Thursday pick revelation functionality
"""

import sqlite3
from datetime import datetime
from deadline_manager import DeadlineManager

def test_thursday_picks():
    """Test if Thursday pick revelation should be working"""
    
    week = 2
    year = 2025
    
    print("🏈 Testing Thursday Pick Revelation")
    print("=" * 50)
    
    # Check database for Thursday games
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get Thursday games
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_thursday_night 
        FROM nfl_games 
        WHERE week = ? AND year = ? AND is_thursday_night = 1
    ''', (week, year))
    
    thursday_games = cursor.fetchall()
    print(f"Thursday Games Found: {len(thursday_games)}")
    
    for game in thursday_games:
        game_id, away_team, home_team, game_date, is_thursday_night = game
        print(f"  Game {game_id}: {away_team} @ {home_team} on {game_date}")
        
        # Get picks for this game
        cursor.execute('''
            SELECT u.username, up.selected_team, up.predicted_home_score, up.predicted_away_score
            FROM user_picks up
            JOIN users u ON up.user_id = u.id
            WHERE up.game_id = ?
            ORDER BY u.username
        ''', (game_id,))
        
        picks = cursor.fetchall()
        print(f"    Picks found: {len(picks)}")
        for username, selected_team, home_score, away_score in picks:
            score_info = f" ({home_score}-{away_score})" if home_score and away_score else ""
            print(f"      {username}: {selected_team}{score_info}")
    
    # Check deadline status
    print("\n📅 Deadline Status")
    print("-" * 30)
    
    try:
        deadline_manager = DeadlineManager()
        simple_status = deadline_manager.get_simple_deadline_status(week, year)
        
        thursday_status = simple_status.get('thursday', {})
        thursday_passed = thursday_status.get('passed', False)
        
        print(f"Thursday deadline passed: {thursday_passed}")
        print(f"Thursday status: {thursday_status}")
        
        if thursday_passed:
            print("✅ Thursday picks should be revealed!")
        else:
            print("❌ Thursday picks should NOT be revealed yet")
            
    except Exception as e:
        print(f"Error checking deadlines: {e}")
    
    conn.close()

def test_games_route_data():
    """Test the data that would be passed to the games template"""
    
    print("\n🎯 Testing Games Route Data")
    print("=" * 50)
    
    week = 2
    year = 2025
    
    # Simulate games route logic
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get all games
    cursor.execute('''
        SELECT * FROM nfl_games 
        WHERE week = ? AND year = ? 
        ORDER BY game_date
    ''', (week, year))
    
    games_raw = cursor.fetchall()
    games_data = []
    
    for game in games_raw:
        game_dict = dict(game)
        # Add Thursday Night detection
        game_dict['is_actual_thursday_night'] = game_dict.get('is_thursday_night', False)
        games_data.append(game_dict)
    
    # Get deadline status
    try:
        deadline_manager = DeadlineManager()
        simple_status = deadline_manager.get_simple_deadline_status(week, year)
        thursday_deadline_passed = simple_status.get('thursday', {}).get('passed', False)
        
        print(f"Thursday deadline passed: {thursday_deadline_passed}")
        
        # Find Thursday games
        thursday_games = [g for g in games_data if g.get('is_actual_thursday_night', False)]
        print(f"Thursday games in template data: {len(thursday_games)}")
        
        for game in thursday_games:
            print(f"  Game {game['id']}: {game['away_team']} @ {game['home_team']}")
            print(f"    is_actual_thursday_night: {game.get('is_actual_thursday_night', False)}")
            
        # Get all picks data
        cursor.execute('''
            SELECT g.id, u.username, up.selected_team, up.predicted_home_score, up.predicted_away_score
            FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            JOIN users u ON up.user_id = u.id
            WHERE g.week = ? AND g.year = ? AND u.is_admin = 0
            ORDER BY g.game_date, u.username
        ''', (week, year))
        
        all_picks = []
        for row in cursor.fetchall():
            all_picks.append({
                'game_id': row[0],
                'username': row[1],
                'selected_team': row[2],
                'predicted_home_score': row[3],
                'predicted_away_score': row[4]
            })
        
        # Filter picks for Thursday games
        thursday_picks = [p for p in all_picks if any(g['id'] == p['game_id'] and g.get('is_actual_thursday_night', False) for g in games_data)]
        
        print(f"Thursday picks in all_picks data: {len(thursday_picks)}")
        for pick in thursday_picks:
            print(f"  {pick['username']}: {pick['selected_team']} (Game {pick['game_id']})")
            
        if thursday_deadline_passed and thursday_games and thursday_picks:
            print("✅ All conditions met for Thursday pick revelation!")
        else:
            print("❌ Not all conditions met:")
            print(f"    Thursday deadline passed: {thursday_deadline_passed}")
            print(f"    Thursday games found: {len(thursday_games) > 0}")
            print(f"    Thursday picks found: {len(thursday_picks) > 0}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    conn.close()

if __name__ == "__main__":
    test_thursday_picks()
    test_games_route_data()
