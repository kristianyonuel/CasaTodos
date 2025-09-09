#!/usr/bin/env python3
"""
Diagnose and fix the scoring issue after manual pick updates
"""

import sqlite3

def diagnose_scoring_issue():
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=== DIAGNOSING SCORING ISSUE ===")
    
    # Check if games are still marked as final
    cursor.execute('''
        SELECT COUNT(*) as total_games, 
               COUNT(CASE WHEN is_final = 1 THEN 1 END) as final_games
        FROM nfl_games 
        WHERE week = 1 AND year = 2025
    ''')
    game_stats = cursor.fetchone()
    print(f"Week 1 Games: {game_stats['final_games']}/{game_stats['total_games']} marked as final")
    
    # Check user picks status
    cursor.execute('''
        SELECT COUNT(*) as total_picks,
               COUNT(CASE WHEN is_correct = 1 THEN 1 END) as correct_picks,
               COUNT(CASE WHEN is_correct = 0 THEN 1 END) as incorrect_picks,
               COUNT(CASE WHEN is_correct IS NULL THEN 1 END) as null_picks
        FROM user_picks p
        JOIN nfl_games g ON p.game_id = g.id
        WHERE g.week = 1 AND g.year = 2025
    ''')
    pick_stats = cursor.fetchone()
    print(f"Week 1 Picks: {pick_stats['correct_picks']} correct, {pick_stats['incorrect_picks']} incorrect, {pick_stats['null_picks']} null")
    
    # Check coyote's specific picks
    cursor.execute('''
        SELECT u.username, p.selected_team, p.predicted_away_score, p.predicted_home_score, 
               p.is_correct, g.home_team, g.away_team, g.home_score, g.away_score, g.is_final
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        JOIN nfl_games g ON p.game_id = g.id
        WHERE u.username = 'coyote' AND g.week = 1 AND g.year = 2025
        ORDER BY g.game_date
    ''')
    
    coyote_picks = cursor.fetchall()
    print(f"\n=== COYOTE'S PICKS STATUS ===")
    
    correct_count = 0
    for pick in coyote_picks:
        if pick['is_final']:
            # Determine actual winner
            if pick['home_score'] > pick['away_score']:
                actual_winner = pick['home_team']
            elif pick['away_score'] > pick['home_score']:
                actual_winner = pick['away_team']
            else:
                actual_winner = 'TIE'
            
            is_correct_should_be = pick['selected_team'] == actual_winner
            if is_correct_should_be:
                correct_count += 1
                
            status = "✅" if pick['is_correct'] == 1 else "❌" if pick['is_correct'] == 0 else "?"
            expected = "✅" if is_correct_should_be else "❌"
            
            print(f"{pick['away_team']} @ {pick['home_team']}: {pick['away_score']}-{pick['home_score']}")
            print(f"  Selected: {pick['selected_team']}, Actual: {actual_winner}")
            print(f"  Stored: {status}, Expected: {expected}")
            if pick['is_correct'] != (1 if is_correct_should_be else 0):
                print(f"  ⚠️  MISMATCH!")
            print()
    
    print(f"Expected correct picks for coyote: {correct_count}")
    
    conn.close()

def fix_scoring():
    print("\n=== FIXING SCORING ===")
    from scoring_updater import ScoringUpdater
    
    # Re-run the game scoring to fix is_correct flags
    updater = ScoringUpdater()
    
    # This should recalculate all is_correct values based on current game results
    print("Recalculating all pick results...")
    success = updater.update_weekly_results(1, 2025)
    
    if success:
        print("✅ Scoring fixed and weekly results updated!")
        
        # Show corrected results
        results = updater.get_week_winners(1, 2025)
        print(f"\n=== CORRECTED WEEK 1 RESULTS ===")
        for i, result in enumerate(results[:5], 1):
            print(f"{i}. {result['username']}: {result['correct_picks']} correct")
    else:
        print("❌ Failed to fix scoring")

if __name__ == "__main__":
    diagnose_scoring_issue()
    fix_scoring()
