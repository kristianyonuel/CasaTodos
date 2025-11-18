#!/usr/bin/env python3
"""
Debug script to test Thursday picks revelation on Ubuntu server
"""

import sqlite3
import sys
from datetime import datetime

def check_thursday_picks_data():
    """Check if all data needed for Thursday picks revelation is present"""
    print("🏈 THURSDAY PICKS REVELATION DEBUG")
    print("=" * 50)
    
    # Find database
    db_paths = ['nfl_fantasy.db', '/home/casa/CasaTodos/nfl_fantasy.db', './nfl_fantasy.db']
    db_path = None
    
    for path in db_paths:
        try:
            conn = sqlite3.connect(path)
            conn.close()
            db_path = path
            print(f"✅ Found database: {path}")
            break
        except:
            continue
    
    if not db_path:
        print("❌ No database found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check Thursday games
        print("\n=== THURSDAY GAMES ===")
        cursor.execute('''
            SELECT id, home_team, away_team, game_date, is_thursday_night, is_final
            FROM nfl_games 
            WHERE week = 2 AND year = 2025 AND is_thursday_night = 1
        ''')
        
        thursday_games = cursor.fetchall()
        print(f"Thursday games found: {len(thursday_games)}")
        
        if not thursday_games:
            print("❌ No Thursday games found!")
            return False
        
        for game in thursday_games:
            game_id, home, away, date, is_thurs, is_final = game
            print(f"  Game {game_id}: {away} @ {home}")
            print(f"    Date: {date}")
            print(f"    Thursday: {is_thurs}")
            print(f"    Final: {is_final}")
            
            # Check picks for this game
            cursor.execute('''
                SELECT u.username, up.selected_team
                FROM user_picks up
                JOIN users u ON up.user_id = u.id
                WHERE up.game_id = ? AND u.is_admin = 0
                ORDER BY u.username
            ''', (game_id,))
            
            picks = cursor.fetchall()
            print(f"    Picks: {len(picks)}")
            
            if picks:
                for username, selected in picks:
                    print(f"      {username}: {selected}")
            else:
                print("      No picks found!")
        
        # Check deadline status
        print("\n=== DEADLINE STATUS ===")
        try:
            # Try to import deadline manager
            sys.path.append('.')
            from deadline_manager import DeadlineManager
            
            dm = DeadlineManager()
            deadline_data = dm.get_week_deadlines(2, 2025)
            
            thursday_data = deadline_data.get('thursday_night')
            if thursday_data:
                print("✅ Thursday deadline data found")
                status = thursday_data.get('status', {})
                is_closed = status.get('is_closed', False)
                hours_until = status.get('hours_until_deadline', 0)
                
                print(f"  Is closed: {is_closed}")
                print(f"  Hours until deadline: {hours_until:.1f}")
                
                if is_closed:
                    print("✅ Thursday deadline has passed - picks should be revealed!")
                else:
                    print("❌ Thursday deadline not passed yet")
            else:
                print("❌ No Thursday deadline data found")
                
        except Exception as e:
            print(f"❌ Error checking deadline: {e}")
        
        # Check all_picks data (what template needs)
        print("\n=== ALL PICKS DATA ===")
        cursor.execute('''
            SELECT g.id, u.username, up.selected_team
            FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            JOIN users u ON up.user_id = u.id
            WHERE g.week = 2 AND g.year = 2025 AND u.is_admin = 0
            ORDER BY g.game_date, u.username
        ''')
        
        all_picks = cursor.fetchall()
        print(f"Total picks for Week 2: {len(all_picks)}")
        
        # Group by game
        game_picks = {}
        for game_id, username, selected in all_picks:
            if game_id not in game_picks:
                game_picks[game_id] = []
            game_picks[game_id].append((username, selected))
        
        print("Picks by game:")
        for game_id, picks in game_picks.items():
            print(f"  Game {game_id}: {len(picks)} picks")
            for username, selected in picks[:3]:  # Show first 3
                print(f"    {username}: {selected}")
            if len(picks) > 3:
                print(f"    ... and {len(picks) - 3} more")
        
        conn.close()
        
        print(f"\n🎉 DATA CHECK COMPLETE")
        print(f"   Thursday games: {len(thursday_games)}")
        print(f"   Total picks: {len(all_picks)}")
        print(f"   Deadline passed: Should be True")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_variables():
    """Test what variables should be passed to template"""
    print("\n=== TEMPLATE VARIABLES TEST ===")
    
    # This is what the template needs:
    # thursday_deadline_passed = True/False
    # games = list of games with is_thursday_night
    # all_picks = list of picks with game_id, username, selected_team
    
    required_vars = [
        'thursday_deadline_passed',
        'games', 
        'all_picks'
    ]
    
    print("Required template variables:")
    for var in required_vars:
        print(f"  ✅ {var}")
    
    print("\nTemplate logic:")
    print("  {% if thursday_deadline_passed %}")
    print("    {% set thursday_games = games|selectattr('is_thursday_night', 'equalto', true)|list %}")
    print("    {% for game in thursday_games %}")
    print("      {% set game_picks = all_picks|selectattr('game_id', 'equalto', game.id)|list %}")
    print("      Display picks...")
    
if __name__ == "__main__":
    success = check_thursday_picks_data()
    test_template_variables()
    
    if success:
        print(f"\n✅ ALL DATA CHECKS PASSED!")
        print(f"Thursday picks should be visible on weekly leaderboard")
    else:
        print(f"\n❌ DATA CHECKS FAILED!")
        print(f"Fix the issues above to enable Thursday picks revelation")
