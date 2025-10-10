#!/usr/bin/env python3

import sqlite3
from scoring_updater import ScoringUpdater

def manual_update_week4():
    """Manually update Week 4 results and determine winner if all games are complete"""
    
    print("🔧 Manual Week 4 Results Update")
    print("=" * 50)
    
    # Initialize scoring updater
    updater = ScoringUpdater()
    
    # Update Week 4, 2025 results
    week = 4
    year = 2025
    
    print(f"📊 Updating results for Week {week}, {year}...")
    success = updater.update_weekly_results(week, year)
    
    if success:
        print("✅ Week 4 results updated successfully!")
    else:
        print("❌ Failed to update Week 4 results")
        return
    
    # Check results
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print()
    print("🏆 Updated Week 4 Standings:")
    cursor.execute('''
        SELECT u.username, wr.correct_picks, wr.total_picks, wr.is_winner,
               wr.monday_score_diff, wr.total_points
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.week = ? AND wr.year = ?
        ORDER BY wr.is_winner DESC, wr.correct_picks DESC, 
                 wr.monday_score_diff ASC, u.username
    ''', (week, year))
    
    results = cursor.fetchall()
    
    for username, correct, total, is_winner, mnf_diff, points in results:
        winner_mark = "🏆 WINNER" if is_winner else ""
        mnf_info = f"(MNF diff: {mnf_diff})" if mnf_diff is not None else ""
        print(f"  {username}: {correct}/{total} {mnf_info} {winner_mark}")
    
    # Check game completion status
    print()
    print("🏈 Week 4 Game Status:")
    cursor.execute('''
        SELECT COUNT(*) as total, 
               SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as completed
        FROM nfl_games 
        WHERE week = ? AND year = ?
    ''', (week, year))
    
    total_games, completed_games = cursor.fetchone()
    print(f"  Games: {completed_games}/{total_games} completed")
    
    if completed_games == total_games:
        print("  ✅ Week is complete - winner should be determined")
    else:
        print(f"  ⏳ {total_games - completed_games} games remaining")
    
    conn.close()

if __name__ == "__main__":
    manual_update_week4()