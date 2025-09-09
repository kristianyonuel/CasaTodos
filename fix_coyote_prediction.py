#!/usr/bin/env python3
"""
Fix coyote's reversed Monday Night prediction
"""

import sqlite3
from scoring_updater import ScoringUpdater


def fix_coyote_prediction():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get the Monday Night game
    cursor.execute('''
        SELECT id, home_team, away_team, home_score, away_score 
        FROM nfl_games 
        WHERE week = 1 AND year = 2025 
        AND home_team = "CHI" AND away_team = "MIN"
    ''')
    game = cursor.fetchone()
    print(f'Monday Night Game: {game[2]} {game[4]} - {game[1]} {game[3]}')
    
    # Get coyote's current pick
    cursor.execute('''
        SELECT p.id, p.predicted_away_score, p.predicted_home_score 
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        WHERE u.username = "coyote" AND p.game_id = ?
    ''', (game[0],))
    pick = cursor.fetchone()
    print(f'Coyote current prediction: MIN {pick[1]} - CHI {pick[2]}')
    
    # Update to correct values: MIN 27 - CHI 21
    cursor.execute('''
        UPDATE user_picks 
        SET predicted_away_score = 27, predicted_home_score = 21 
        WHERE id = ?
    ''', (pick[0],))
    conn.commit()
    conn.close()
    
    print('✅ Corrected coyote prediction to: MIN 27 - CHI 21')
    
    # Update weekly results with new tiebreaker scores
    print('\n=== UPDATING WEEKLY RESULTS WITH CORRECTED TIEBREAKER ===')
    updater = ScoringUpdater()
    success = updater.update_weekly_results(1, 2025)
    
    if success:
        print("✅ Weekly results updated with corrected tiebreaker!")
        
        # Show final results
        results = updater.get_week_winners(1, 2025)
        print(f"\n=== FINAL WEEK 1 LEADERBOARD (CORRECTED) ===")
        for i, result in enumerate(results[:5], 1):
            mnf = result['monday_tiebreaker']
            correct_str = "✅" if mnf.get("correct_winner") else "❌"
            print(f"{i}. {result['username']}: {result['correct_picks']} correct")
            if mnf.get('home_diff') is not None:
                home_diff = mnf['home_diff']
                away_diff = mnf['away_diff']
                print(f"   MNF: {correct_str} Winner, Home±{home_diff}, Away±{away_diff}")


if __name__ == "__main__":
    fix_coyote_prediction()
