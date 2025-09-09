#!/usr/bin/env python3
"""
Fix coyote's reversed Monday Night prediction and update Week 1 results
"""

import sqlite3
from scoring_updater import ScoringUpdater

def fix_coyote_and_update():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get the Monday Night game ID and coyote's user ID
    cursor.execute('SELECT id FROM nfl_games WHERE week = 1 AND year = 2025 AND is_monday_night = 1')
    game_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM users WHERE username = "coyote"')
    user_id = cursor.fetchone()[0]
    
    print('=== FIXING COYOTE\'S REVERSED PREDICTION ===')
    print('Old: MIN 21 - CHI 27')
    print('New: MIN 27 - CHI 21')
    
    # Update coyote's prediction
    cursor.execute('''
        UPDATE user_picks 
        SET predicted_away_score = 27, predicted_home_score = 21
        WHERE user_id = ? AND game_id = ?
    ''', (user_id, game_id))
    
    conn.commit()
    conn.close()
    print('✅ Database updated successfully!')
    
    # Regenerate Week 1 results with corrected tiebreaker logic
    print('\n=== UPDATING WEEK 1 RESULTS ===')
    updater = ScoringUpdater()
    success = updater.update_weekly_results(1, 2025)
    
    if success:
        print('✅ Week 1 results updated with new tiebreaker logic!')
        
        # Show the corrected results
        results = updater.get_week_winners(1, 2025)
        print(f'\n=== FINAL WEEK 1 RESULTS (Top 5) ===')
        for i, result in enumerate(results[:5], 1):
            mnf = result['monday_tiebreaker']
            correct_str = "✅" if mnf.get("correct_winner") else "❌"
            print(f'{i}. {result["username"]}: {result["correct_picks"]} correct')
            print(f'   MNF: {correct_str} Winner, Home±{mnf["home_diff"]}, Away±{mnf["away_diff"]}')
        
        print('\n🏆 READY FOR UBUNTU COMMIT!')
        print('Tiebreaker logic: Correct winner → Home team → Away team → Total → Time')
        
    else:
        print('❌ Failed to update Week 1 results')

if __name__ == "__main__":
    fix_coyote_and_update()
