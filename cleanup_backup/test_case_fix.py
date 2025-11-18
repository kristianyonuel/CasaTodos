#!/usr/bin/env python3
"""
Test case sensitivity fix for score updater
"""

import sqlite3
from score_updater import NFLScoreUpdater

def test_case_sensitivity_fix():
    """Test that the score updater can match games regardless of case"""
    print("🧪 Testing Case Sensitivity Fix")
    print("=" * 40)
    
    # Check current WSH@GB game status
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT game_id, away_team, home_team, away_score, home_score, is_final
        FROM nfl_games 
        WHERE (away_team = 'WSH' AND home_team = 'GB') 
        OR (away_team = 'wsh' AND home_team = 'gb')
        OR (UPPER(away_team) = 'WSH' AND UPPER(home_team) = 'GB')
    ''')
    
    game = cursor.fetchone()
    if game:
        game_id, away, home, away_score, home_score, is_final = game
        print(f"Found game: {game_id}")
        print(f"Teams: {away} @ {home}")
        print(f"Current score: {away_score}-{home_score}")
        print(f"Final: {'Yes' if is_final else 'No'}")
        
        # Test the case-insensitive query
        print(f"\n🔧 Testing case-insensitive matching...")
        
        # Test with different cases
        test_cases = [
            ('WSH', 'GB'),
            ('wsh', 'gb'), 
            ('Wsh', 'Gb'),
            ('WsH', 'gB')
        ]
        
        for test_away, test_home in test_cases:
            cursor.execute('''
                SELECT game_id 
                FROM nfl_games 
                WHERE UPPER(away_team) = UPPER(?) 
                AND UPPER(home_team) = UPPER(?)
            ''', (test_away, test_home))
            
            result = cursor.fetchone()
            status = "✅ FOUND" if result else "❌ NOT FOUND"
            print(f"  {test_away}@{test_home}: {status}")
        
        # Now test the score updater with mock data
        print(f"\n🚀 Testing Score Updater...")
        
        # Create mock ESPN data with lowercase teams
        mock_espn_data = {
            'wsh@gb': {  # lowercase to test case sensitivity
                'espn_id': 'test_game',
                'away_team': 'wsh',  # lowercase
                'home_team': 'gb',   # lowercase  
                'away_score': 18,
                'home_score': 27,
                'is_final': True,
                'game_status': 'Final',
                'game_date': '2025-09-12T20:15:00Z'
            }
        }
        
        updater = NFLScoreUpdater('nfl_fantasy.db')
        updated_count = updater.update_game_scores(mock_espn_data)
        
        print(f"✅ Score updater processed {updated_count} games")
        
        # Check if the game was updated
        cursor.execute('''
            SELECT away_score, home_score, is_final
            FROM nfl_games 
            WHERE game_id = ?
        ''', (game_id,))
        
        updated_game = cursor.fetchone()
        if updated_game:
            new_away, new_home, new_final = updated_game
            print(f"Updated score: {new_away}-{new_home}")
            print(f"Final: {'Yes' if new_final else 'No'}")
            
            if new_away == 18 and new_home == 27 and new_final:
                print("🎉 SUCCESS: Case sensitivity fix working!")
            else:
                print("⚠️ Partial success: Game found but not fully updated")
        else:
            print("❌ Game not found after update")
    else:
        print("❌ WSH@GB game not found in database")
    
    conn.close()

if __name__ == "__main__":
    test_case_sensitivity_fix()
