#!/usr/bin/env python3
"""
Fix all is_correct values for user picks based on current game results
"""

import sqlite3


def fix_all_picks():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("=== FIXING ALL USER PICKS ===")
    
    # Get all picks for Week 1 with game results
    cursor.execute('''
        SELECT p.id, p.user_id, p.game_id, p.selected_team, p.is_correct,
               g.home_team, g.away_team, g.home_score, g.away_score, g.is_final,
               u.username
        FROM user_picks p
        JOIN nfl_games g ON p.game_id = g.id
        JOIN users u ON p.user_id = u.id
        WHERE g.week = 1 AND g.year = 2025 AND g.is_final = 1
        ORDER BY u.username, g.game_date
    ''')
    
    picks = cursor.fetchall()
    print(f"Found {len(picks)} picks to process...")
    
    updates_made = 0
    user_scores = {}
    
    for pick in picks:
        pick_id, user_id, game_id, selected_team, current_is_correct, home_team, away_team, home_score, away_score, is_final, username = pick
        
        # Determine actual winner
        if home_score > away_score:
            actual_winner = home_team
        elif away_score > home_score:
            actual_winner = away_team
        else:
            actual_winner = 'TIE'  # Shouldn't happen in NFL
        
        # Calculate if pick should be correct
        should_be_correct = 1 if selected_team == actual_winner else 0
        
        # Update if different from current value
        if current_is_correct != should_be_correct:
            cursor.execute('''
                UPDATE user_picks 
                SET is_correct = ? 
                WHERE id = ?
            ''', (should_be_correct, pick_id))
            updates_made += 1
        
        # Track user scores
        if username not in user_scores:
            user_scores[username] = {'correct': 0, 'total': 0}
        user_scores[username]['total'] += 1
        if should_be_correct == 1:
            user_scores[username]['correct'] += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ Updated {updates_made} pick records")
    
    # Show user scores
    print("\n=== USER SCORES AFTER FIX ===")
    sorted_users = sorted(user_scores.items(), key=lambda x: (-x[1]['correct'], x[0]))
    for username, scores in sorted_users[:10]:
        print(f"{username}: {scores['correct']}/{scores['total']} correct")
    
    # Now update weekly results
    print("\n=== UPDATING WEEKLY RESULTS ===")
    from scoring_updater import ScoringUpdater
    updater = ScoringUpdater()
    success = updater.update_weekly_results(1, 2025)
    
    if success:
        print("✅ Weekly results updated successfully!")
        
        # Show final results
        results = updater.get_week_winners(1, 2025)
        print(f"\n=== FINAL WEEK 1 LEADERBOARD ===")
        for i, result in enumerate(results[:5], 1):
            mnf = result['monday_tiebreaker']
            correct_str = "✅" if mnf.get("correct_winner") else "❌"
            print(f"{i}. {result['username']}: {result['correct_picks']} correct")
            if mnf.get('home_diff') is not None:
                print(f"   MNF: {correct_str} Winner, Home±{mnf['home_diff']}, Away±{mnf['away_diff']}")
    else:
        print("❌ Failed to update weekly results")

if __name__ == "__main__":
    fix_all_picks()
