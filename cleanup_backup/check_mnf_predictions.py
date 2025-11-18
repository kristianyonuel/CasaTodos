"""
Check Monday Night Predictions Status
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_db_legacy

def check_mnf_predictions():
    """Check current Monday Night predictions in the database"""
    print("=== Monday Night Predictions Status ===")
    
    try:
        conn = get_db_legacy()
        cursor = conn.cursor()
        
        # Find the Monday Night game for Week 2
        cursor.execute('''
            SELECT id, home_team, away_team, game_date, is_final
            FROM nfl_games 
            WHERE week = 2 AND year = 2025 
            AND strftime('%w', game_date) = '1'
            ORDER BY game_date DESC
            LIMIT 1
        ''')
        
        mnf_game = cursor.fetchone()
        if not mnf_game:
            print("❌ No Monday Night game found for Week 2")
            return
            
        game_id, home_team, away_team, game_date, is_final = mnf_game
        print(f"Monday Night Game: {away_team} @ {home_team}")
        print(f"Game Date: {game_date}")
        print(f"Game ID: {game_id}")
        print(f"Is Final: {is_final}")
        
        # Check who has made predictions for this game
        cursor.execute('''
            SELECT u.username, p.selected_team, p.predicted_home_score, p.predicted_away_score
            FROM user_picks p
            JOIN users u ON p.user_id = u.id
            WHERE p.game_id = ? AND u.is_admin = 0
            ORDER BY u.username
        ''', (game_id,))
        
        predictions = cursor.fetchall()
        print(f"\nFound {len(predictions)} Monday Night predictions:")
        
        for username, selected_team, home_score, away_score in predictions:
            print(f"  {username}:")
            print(f"    Selected: {selected_team}")
            if home_score is not None and away_score is not None:
                print(f"    Score Prediction: {away_team} {away_score} - {home_score} {home_team}")
            else:
                print(f"    Score Prediction: None")
        
        # Check if this is the current actual MNF game
        cursor.execute('''
            SELECT COUNT(*) FROM nfl_games 
            WHERE week = 2 AND year = 2025 
            AND strftime('%w', game_date) = '1'
        ''')
        
        monday_game_count = cursor.fetchone()[0]
        print(f"\nTotal Monday games in Week 2: {monday_game_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking MNF predictions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_mnf_predictions()
