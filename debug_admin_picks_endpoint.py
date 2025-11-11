#!/usr/bin/env python3
"""
Debug Admin Picks Endpoint Issue
Examines why KRISTIAN's picks aren't showing in admin interface despite being in database
"""

import sqlite3
import json
from datetime import datetime

def debug_admin_picks_issue():
    """Debug the admin user picks loading issue"""
    print("=" * 60)
    print("DEBUGGING ADMIN PICKS ENDPOINT ISSUE")
    print("=" * 60)
    
    # Connect to database
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Check KRISTIAN's user ID
    print("\n1. Finding KRISTIAN's User ID:")
    cursor.execute("SELECT id, username FROM users WHERE username LIKE '%kristian%' OR username LIKE '%KRISTIAN%'")
    kristian_user = cursor.fetchone()
    
    if not kristian_user:
        print("❌ KRISTIAN user not found!")
        cursor.execute("SELECT id, username FROM users ORDER BY username")
        all_users = cursor.fetchall()
        print("\nAll users in database:")
        for user in all_users:
            print(f"  ID: {user['id']}, Username: {user['username']}")
        return
    
    print(f"✅ Found KRISTIAN: ID = {kristian_user['id']}, Username = {kristian_user['username']}")
    kristian_id = kristian_user['id']
    
    # 2. Check KRISTIAN's picks in database for Week 9
    print(f"\n2. KRISTIAN's Week 9 Picks in Database:")
    cursor.execute("""
        SELECT up.*, g.away_team, g.home_team, g.game_date, g.is_monday_night
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.id
        WHERE up.user_id = ? AND up.week = 9 AND up.year = 2025
        ORDER BY g.game_date
    """, (kristian_id,))
    
    kristian_picks = cursor.fetchall()
    print(f"Found {len(kristian_picks)} picks for KRISTIAN in Week 9:")
    
    for pick in kristian_picks:
        print(f"  Game ID: {pick['game_id']}, {pick['away_team']} @ {pick['home_team']}")
        print(f"    Selected: {pick['selected_team']}")
        if pick['is_monday_night']:
            print(f"    Score Prediction: {pick['predicted_away_score']}-{pick['predicted_home_score']}")
        print()
    
    # 3. Simulate the admin endpoint query
    print("\n3. Simulating Admin Endpoint Query:")
    print("Query that admin interface should be using:")
    
    # This mimics what the Flask endpoint /admin/user_picks should do
    cursor.execute("""
        SELECT 
            up.id as pick_id,
            up.game_id,
            up.selected_team,
            up.predicted_away_score,
            up.predicted_home_score,
            g.away_team,
            g.home_team,
            g.is_monday_night,
            g.game_date
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.id
        WHERE up.user_id = ? AND up.week = ? AND up.year = ?
        ORDER BY g.game_date
    """, (kristian_id, 9, 2025))
    
    admin_query_results = cursor.fetchall()
    print(f"Admin query returned {len(admin_query_results)} picks:")
    
    for pick in admin_query_results:
        print(f"  Game ID: {pick['game_id']}, Pick ID: {pick['pick_id']}")
        print(f"    {pick['away_team']} @ {pick['home_team']}")
        print(f"    Selected: {pick['selected_team']}")
        if pick['is_monday_night']:
            print(f"    MNF Prediction: {pick['predicted_away_score']}-{pick['predicted_home_score']}")
        print()
    
    # 4. Check if there are any issues with game IDs or data
    print("\n4. Week 9 Games Analysis:")
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
            WHERE user_id = ? AND game_id = ? AND week = 9 AND year = 2025
        """, (kristian_id, game['id']))
        
        pick = cursor.fetchone()
        pick_status = pick['selected_team'] if pick else "NO PICK"
        
        print(f"  Game {game['id']}: {game['away_team']} @ {game['home_team']} -> {pick_status}")
    
    # 5. Check for any data type issues
    print("\n5. Data Type Analysis:")
    cursor.execute("""
        SELECT typeof(user_id), typeof(game_id), typeof(week), typeof(year), selected_team
        FROM user_picks 
        WHERE user_id = ? AND week = 9 AND year = 2025
        LIMIT 3
    """, (kristian_id,))
    
    type_check = cursor.fetchall()
    for row in type_check:
        print(f"  user_id type: {row[0]}, game_id type: {row[1]}, week type: {row[2]}, year type: {row[3]}")
        print(f"  selected_team: '{row[4]}'")
    
    # 6. Test JSON serialization (what Flask would return)
    print("\n6. JSON Serialization Test:")
    picks_for_json = []
    for pick in admin_query_results:
        pick_dict = {
            'pick_id': pick['pick_id'],
            'game_id': pick['game_id'],
            'selected_team': pick['selected_team'],
            'predicted_away_score': pick['predicted_away_score'],
            'predicted_home_score': pick['predicted_home_score'],
            'away_team': pick['away_team'],
            'home_team': pick['home_team'],
            'is_monday_night': pick['is_monday_night']
        }
        picks_for_json.append(pick_dict)
    
    try:
        json_output = json.dumps(picks_for_json, indent=2)
        print("✅ JSON serialization successful")
        print(f"First pick in JSON:\n{json.dumps(picks_for_json[0], indent=2)}")
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
    
    # 7. Check for any special characters or encoding issues
    print("\n7. Data Quality Check:")
    for pick in kristian_picks:
        selected = pick['selected_team']
        if selected:
            print(f"  Selected team: '{selected}' (length: {len(selected)})")
            print(f"    ASCII: {all(ord(c) < 128 for c in selected)}")
            print(f"    Repr: {repr(selected)}")
        else:
            print(f"  ❌ NULL or empty selected_team for game {pick['game_id']}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test the actual Flask endpoint /admin/user_picks")
    print("2. Check JavaScript console for errors in browser")
    print("3. Verify form element IDs match between HTML and JavaScript")
    print("4. Check if there are any Flask template rendering issues")

if __name__ == "__main__":
    debug_admin_picks_issue()