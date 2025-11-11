#!/usr/bin/env python3
"""
Debug Admin Picks Issue - CORRECTED VERSION
Examines why KRISTIAN's picks aren't showing in admin interface
"""

import sqlite3
import json

def debug_admin_picks_corrected():
    """Debug the admin user picks loading issue with correct schema"""
    print("=" * 60)
    print("DEBUGGING ADMIN PICKS ISSUE - CORRECTED")
    print("=" * 60)
    
    # Connect to database
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Find KRISTIAN's user ID
    print("\n1. Finding KRISTIAN's User ID:")
    cursor.execute("SELECT id, username FROM users WHERE username LIKE '%kristian%'")
    kristian_user = cursor.fetchone()
    
    if not kristian_user:
        print("❌ KRISTIAN user not found!")
        return
    
    print(f"✅ Found KRISTIAN: ID = {kristian_user['id']}, Username = {kristian_user['username']}")
    kristian_id = kristian_user['id']
    
    # 2. Check KRISTIAN's picks with CORRECT query (week/year in nfl_games)
    print(f"\n2. KRISTIAN's Week 9 Picks in Database (CORRECTED QUERY):")
    cursor.execute("""
        SELECT 
            up.id as pick_id,
            up.user_id,
            up.game_id,
            up.selected_team,
            up.predicted_away_score,
            up.predicted_home_score,
            g.away_team,
            g.home_team,
            g.week,
            g.year,
            g.game_date,
            g.is_monday_night
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.id
        WHERE up.user_id = ? AND g.week = 9 AND g.year = 2025
        ORDER BY g.game_date
    """, (kristian_id,))
    
    kristian_picks = cursor.fetchall()
    print(f"Found {len(kristian_picks)} picks for KRISTIAN in Week 9:")
    
    for pick in kristian_picks:
        print(f"  Pick ID: {pick['pick_id']}, Game ID: {pick['game_id']}")
        print(f"    {pick['away_team']} @ {pick['home_team']}")
        print(f"    Selected: {pick['selected_team']}")
        if pick['is_monday_night']:
            print(f"    MNF Prediction: {pick['predicted_away_score']}-{pick['predicted_home_score']}")
        print()
    
    # 3. Simulate the CORRECT admin endpoint query
    print("\n3. Simulating CORRECTED Admin Endpoint Query:")
    print("This is what the Flask /admin/user_picks endpoint SHOULD be doing:")
    
    # Correct query that Flask should use
    picks_for_admin = []
    for pick in kristian_picks:
        pick_dict = {
            'pick_id': pick['pick_id'],
            'game_id': pick['game_id'],
            'selected_team': pick['selected_team'],
            'predicted_away_score': pick['predicted_away_score'],
            'predicted_home_score': pick['predicted_home_score'],
            'away_team': pick['away_team'],
            'home_team': pick['home_team'],
            'is_monday_night': bool(pick['is_monday_night'])
        }
        picks_for_admin.append(pick_dict)
    
    print(f"Admin query should return {len(picks_for_admin)} picks")
    print("Sample pick data structure:")
    if picks_for_admin:
        print(json.dumps(picks_for_admin[0], indent=2))
    
    # 4. Check ALL Week 9 games and KRISTIAN's picks for each
    print("\n4. Week 9 Games vs KRISTIAN's Picks:")
    cursor.execute("""
        SELECT id, away_team, home_team, game_date, is_monday_night
        FROM nfl_games 
        WHERE week = 9 AND year = 2025
        ORDER BY game_date
    """)
    
    week9_games = cursor.fetchall()
    print(f"Total Week 9 games: {len(week9_games)}")
    
    for game in week9_games:
        # Check if KRISTIAN has a pick for this game
        cursor.execute("""
            SELECT selected_team FROM user_picks 
            WHERE user_id = ? AND game_id = ?
        """, (kristian_id, game['id']))
        
        pick = cursor.fetchone()
        pick_status = pick['selected_team'] if pick else "❌ NO PICK"
        
        print(f"  Game {game['id']}: {game['away_team']} @ {game['home_team']} -> {pick_status}")
    
    # 5. Test the exact query the JavaScript should be making
    print("\n5. Testing JavaScript Admin Query Format:")
    
    # This simulates what happens when admin interface calls:
    # /admin/user_picks?user_id=4&week=9&year=2025
    test_query = """
        SELECT 
            up.id as pick_id,
            up.game_id,
            up.selected_team,
            up.predicted_away_score,
            up.predicted_home_score,
            g.away_team,
            g.home_team,
            g.is_monday_night
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.id
        WHERE up.user_id = ? AND g.week = ? AND g.year = ?
        ORDER BY g.game_date
    """
    
    cursor.execute(test_query, (kristian_id, 9, 2025))
    admin_results = cursor.fetchall()
    
    print(f"Admin endpoint query returned {len(admin_results)} picks")
    print("This should match the number of picks above!")
    
    # 6. Check if the problem is in the JavaScript form element naming
    print("\n6. Form Element Analysis for JavaScript:")
    print("The HTML should have these radio button names for games:")
    
    for game in week9_games:
        pick_found = None
        for pick in kristian_picks:
            if pick['game_id'] == game['id']:
                pick_found = pick['selected_team']
                break
        
        print(f"  <input name=\"game_{game['id']}\" value=\"{game['away_team']}\" {('checked' if pick_found == game['away_team'] else '')}>")
        print(f"  <input name=\"game_{game['id']}\" value=\"{game['home_team']}\" {('checked' if pick_found == game['home_team'] else '')}>")
    
    # 7. Generate the corrected Flask endpoint response
    print("\n7. Correct Flask Endpoint Response:")
    flask_response = []
    for pick in kristian_picks:
        flask_pick = {
            'pick_id': pick['pick_id'],
            'game_id': pick['game_id'],
            'selected_team': pick['selected_team'],
            'predicted_away_score': pick['predicted_away_score'],
            'predicted_home_score': pick['predicted_home_score'],
            'away_team': pick['away_team'],
            'home_team': pick['home_team'],
            'is_monday_night': bool(pick['is_monday_night'])
        }
        flask_response.append(flask_pick)
    
    print(f"Flask should return: {len(flask_response)} picks")
    print("JSON structure:")
    if flask_response:
        print(json.dumps(flask_response[:2], indent=2))  # Show first 2 picks
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("ROOT CAUSE IDENTIFIED")
    print("=" * 60)
    print("\nThe issue is likely in the Flask admin endpoint query.")
    print("The endpoint needs to JOIN user_picks with nfl_games properly")
    print("because week/year are stored in nfl_games, not user_picks.")
    print("\nCorrect Flask query should be:")
    print(test_query)
    print("\nThis should return", len(admin_results), "picks for KRISTIAN in Week 9")

if __name__ == "__main__":
    debug_admin_picks_corrected()