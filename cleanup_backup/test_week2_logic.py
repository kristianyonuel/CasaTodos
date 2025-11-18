import sqlite3
from datetime import datetime

def test_current_week_logic():
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print('=== Testing Current Week Detection ===')
    
    # Simulate the games() route logic
    current_nfl_week = 2  # Based on your mention that we're in Week 2
    
    # Get week from URL parameter or use current week (simulating no parameter)
    week = current_nfl_week
    year = 2025
    
    print(f'Using Week {week}, Year {year}')
    
    # Get all games for this week
    cursor.execute('''
        SELECT id, away_team, home_team, game_date,
               strftime('%w', game_date) as day_of_week
        FROM nfl_games 
        WHERE week = ? AND year = ? 
        ORDER BY game_date
    ''', (week, year))
    
    games_raw = cursor.fetchall()
    print(f'\nFound {len(games_raw)} games for Week {week}:')
    
    # Find the actual Monday Night Football game (latest game on Monday)
    cursor.execute('''
        SELECT id FROM nfl_games 
        WHERE week = ? AND year = ? 
        AND strftime('%w', game_date) = '1'  -- Monday
        ORDER BY game_date DESC, id DESC
        LIMIT 1
    ''', (week, year))
    
    monday_night_game = cursor.fetchone()
    monday_night_game_id = monday_night_game[0] if monday_night_game else None
    
    print(f'\nDetected Monday Night Football Game ID: {monday_night_game_id}')
    
    # Show which games get the is_actual_monday_night flag
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    for game in games_raw:
        game_dict = dict(game)
        day_name = day_names[int(game['day_of_week'])]
        
        # Add actual Monday Night Football detection (same as in app.py)
        game_dict['is_actual_monday_night'] = (game_dict['id'] == monday_night_game_id)
        
        mnf_indicator = " ← MNF SCORE BOXES" if game_dict['is_actual_monday_night'] else ""
        print(f"  Game {game['id']}: {game['away_team']} @ {game['home_team']} - {game['game_date']} ({day_name}){mnf_indicator}")
    
    conn.close()

if __name__ == '__main__':
    test_current_week_logic()
