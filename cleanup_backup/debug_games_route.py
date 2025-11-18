#!/usr/bin/env python3
"""
Debug script to check Thursday pick revelation variables in app.py
"""

import sqlite3
from deadline_manager import DeadlineManager

def debug_games_route_logic():
    """Debug the exact logic used in the games route"""
    
    print("🔍 Debugging Games Route Logic")
    print("=" * 50)
    
    week = 2
    year = 2025
    
    # Simulate the app.py games route logic
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Get games (simplified)
        cursor.execute('''
            SELECT * FROM nfl_games 
            WHERE week = ? AND year = ? 
            ORDER BY game_date
        ''', (week, year))
        
        games_raw = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        
        # Convert to dict format like in app.py
        games_data = []
        for game_row in games_raw:
            game_dict = {}
            for i, col_name in enumerate(column_names):
                game_dict[col_name] = game_row[i]
            
            # Add Thursday Night detection like in app.py
            game_dict['is_actual_thursday_night'] = game_dict.get('is_thursday_night', False)
            games_data.append(game_dict)
        
        print(f"Total games found: {len(games_data)}")
        
        # Find Thursday games
        thursday_games = [g for g in games_data if g.get('is_actual_thursday_night', False)]
        print(f"Thursday games found: {len(thursday_games)}")
        
        for game in thursday_games:
            print(f"  Game {game['id']}: {game['away_team']} @ {game['home_team']}")
            print(f"    is_thursday_night: {game.get('is_thursday_night', False)}")
            print(f"    is_actual_thursday_night: {game.get('is_actual_thursday_night', False)}")
        
        # Get deadline status like in app.py
        deadline_manager = DeadlineManager()
        deadline_data = deadline_manager.get_week_deadlines(week, year)
        
        deadlines = {}
        deadline_status = {}
        
        for key, value in deadline_data.items():
            if value and isinstance(value, dict) and 'deadline' in value:
                deadlines[key] = value['deadline']
                deadline_status[key] = {
                    'passed': value['status']['is_closed'],
                    'hours_until': value['status']['hours_until_deadline']
                }
        
        simple_status = {
            'thursday': deadline_status.get('thursday_night'),
            'sunday': deadline_status.get('sunday_games'),
            'monday': deadline_status.get('monday_night')
        }
        
        thursday_deadline_passed = simple_status.get('thursday', {}).get('passed', False)
        
        print(f"\\nDeadline Status:")
        print(f"  simple_status: {simple_status}")
        print(f"  thursday_deadline_passed: {thursday_deadline_passed}")
        
        # Get all picks like in app.py
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
        
        print(f"\\nAll picks found: {len(all_picks)}")
        
        # Filter picks for Thursday games (like template would do)
        thursday_picks = [p for p in all_picks if any(g['id'] == p['game_id'] and g.get('is_actual_thursday_night', False) for g in games_data)]
        
        print(f"Thursday picks found: {len(thursday_picks)}")
        for pick in thursday_picks:
            print(f"  {pick['username']}: {pick['selected_team']} (Game {pick['game_id']})")
        
        # Final check - should Thursday revelation show?
        should_show = thursday_deadline_passed and len(thursday_games) > 0
        print(f"\\n🎯 Should Thursday Pick Revelation Show? {should_show}")
        print(f"   Conditions:")
        print(f"   - Thursday deadline passed: {thursday_deadline_passed}")
        print(f"   - Thursday games exist: {len(thursday_games) > 0}")
        print(f"   - Thursday picks exist: {len(thursday_picks) > 0}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_games_route_logic()
