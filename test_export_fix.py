#!/usr/bin/env python3

import io
import csv
from app import get_db

def test_export_function():
    """Test the export function database connection issue"""
    print("Testing export function database connection...")
    
    try:
        # Simulate the export function logic
        week = 1
        year = 2025
        user_id = 1  # Test user ID
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            print("✅ Database connection established")
            
            # Get all games for the week
            cursor.execute('''
                SELECT id, away_team, home_team, game_date, is_monday_night
                FROM nfl_games 
                WHERE week = ? AND year = ?
                ORDER BY game_date
            ''', (week, year))
            
            games = [dict(row) for row in cursor.fetchall()]
            print(f"✅ Found {len(games)} games for Week {week}, {year}")
            
            if not games:
                print("❌ No games found")
                return False
            
            # Get user's picks for this week
            cursor.execute('''
                SELECT up.game_id, up.selected_team, 
                       up.predicted_home_score, up.predicted_away_score
                FROM user_picks up
                JOIN nfl_games g ON up.game_id = g.id
                WHERE up.user_id = ? AND g.week = ? AND g.year = ?
            ''', (user_id, week, year))
            
            user_picks = {}
            for row in cursor.fetchall():
                user_picks[row['game_id']] = {
                    'selected_team': row['selected_team'],
                    'predicted_home_score': row['predicted_home_score'],
                    'predicted_away_score': row['predicted_away_score']
                }
            
            print(f"✅ Found {len(user_picks)} user picks")
            
            # Find Monday Night Football game
            cursor.execute('''
                SELECT id FROM nfl_games 
                WHERE week = ? AND year = ? 
                AND strftime('%w', game_date) = '1'
                ORDER BY game_date DESC, id DESC
                LIMIT 1
            ''', (week, year))
            
            monday_night_game = cursor.fetchone()
            monday_night_game_id = monday_night_game[0] if monday_night_game else None
            
            print(f"✅ Monday Night game ID: {monday_night_game_id}")
            
            # Test CSV generation
            output = io.StringIO()
            writer = csv.writer(output)
            
            writer.writerow(['Test User - Week 1, 2025', 'My Pick', 'Monday Night Score'])
            writer.writerow(['Game', 'Selected Team', 'Score Prediction'])
            
            for game in games[:3]:  # Test first 3 games
                game_label = f"{game['away_team']} @ {game['home_team']}"
                pick_data = user_picks.get(game['id'], {})
                selected_team = pick_data.get('selected_team', 'No Pick Made')
                writer.writerow([game_label, selected_team, ''])
            
            csv_content = output.getvalue()
            output.close()
            
            print("✅ CSV generation successful")
            print(f"CSV preview:\n{csv_content[:200]}...")
            
        print("✅ Database connection closed properly")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_export_function()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
