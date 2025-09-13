#!/usr/bin/env python3
"""
Test script to fix case sensitivity issue in score updater
"""

import sqlite3
from score_updater import NFLScoreUpdater

def test_case_sensitivity_fix():
    """Test the case sensitivity fix for game matching"""
    
    print("🔧 Testing Case Sensitivity Fix")
    print("=" * 50)
    
    # Check current game status
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT game_id, away_team, home_team, away_score, home_score, is_final
        FROM nfl_games 
        WHERE (UPPER(away_team) = 'WSH' AND UPPER(home_team) = 'GB') 
        OR (UPPER(away_team) = 'GB' AND UPPER(home_team) = 'WSH')
        AND week = 2 AND year = 2025
    ''')
    
    game = cursor.fetchone()
    if game:
        game_id, away, home, away_score, home_score, is_final = game
        print(f"Before Update:")
        print(f"  Game ID: {game_id}")
        print(f"  Matchup: {away} @ {home}")
        print(f"  Score: {away_score}-{home_score}")
        print(f"  Final: {'Yes' if is_final else 'No'}")
    else:
        print("❌ WSH@GB game not found!")
        conn.close()
        return
    
    conn.close()
    
    # Test the score updater with the fix
    print("\n🚀 Running Score Updater with Case Fix...")
    try:
        updater = NFLScoreUpdater('nfl_fantasy.db')
        results = updater.run_update_cycle()
        
        print(f"✅ Update completed:")
        print(f"  Games checked: {results['games_checked']}")
        print(f"  Games updated: {results['games_updated']}")
        print(f"  Duration: {results['duration_seconds']:.2f}s")
        
        # Check game status after update
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT game_id, away_team, home_team, away_score, home_score, is_final
            FROM nfl_games 
            WHERE (UPPER(away_team) = 'WSH' AND UPPER(home_team) = 'GB') 
            OR (UPPER(away_team) = 'GB' AND UPPER(home_team) = 'WSH')
            AND week = 2 AND year = 2025
        ''')
        
        game = cursor.fetchone()
        if game:
            game_id, away, home, away_score, home_score, is_final = game
            print(f"\nAfter Update:")
            print(f"  Game ID: {game_id}")
            print(f"  Matchup: {away} @ {home}")
            print(f"  Score: {away_score}-{home_score}")
            print(f"  Final: {'Yes' if is_final else 'No'}")
            
            if away_score is not None and home_score is not None:
                print("🎯 SUCCESS: Score updated!")
            else:
                print("⚠️ Score still not updated - checking ESPN API response...")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error in score updater: {e}")

if __name__ == "__main__":
    test_case_sensitivity_fix()
