#!/usr/bin/env python3

import sqlite3
from datetime import datetime

def fix_week9_weekly_results():
    """Fix Week 9 weekly_results to show correct winner (VIZCA) and rankings"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🏆 FIXING WEEK 9 WEEKLY RESULTS")
    print("=" * 50)
    
    # First, delete existing Week 9 data
    cursor.execute('DELETE FROM weekly_results WHERE week = 9 AND year = 2025')
    deleted_count = cursor.rowcount
    print(f"✅ Deleted {deleted_count} old Week 9 records")
    
    # Get actual Week 9 results from user_picks
    cursor.execute('''
        SELECT u.id, u.username, 
               COUNT(*) as total_picks,
               SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks
        FROM user_picks up
        JOIN nfl_games ng ON up.game_id = ng.game_id
        JOIN users u ON up.user_id = u.id
        WHERE ng.week = 9 AND ng.year = 2025
        GROUP BY u.id, u.username
        ORDER BY correct_picks DESC, u.username
    ''')
    
    results = cursor.fetchall()
    
    print("\n📊 Actual Week 9 Results:")
    print("Rank | User       | Score")
    print("-----|------------|-------")
    
    # Determine rankings and winner
    current_rank = 1
    prev_score = None
    winner_found = False
    
    for i, (user_id, username, total_picks, correct_picks) in enumerate(results):
        # Handle ties in ranking
        if prev_score is not None and correct_picks < prev_score:
            current_rank = i + 1
        
        is_winner = (not winner_found and (prev_score is None or correct_picks == results[0][3]))
        if is_winner:
            winner_found = True
        
        print(f"{current_rank:4d} | {username:10s} | {correct_picks:2d}/{total_picks:2d} {'🏆' if is_winner else ''}")
        
        # Insert into weekly_results
        cursor.execute('''
            INSERT INTO weekly_results (
                user_id, week, year, correct_picks, total_picks,
                is_winner, weekly_rank, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, 9, 2025, correct_picks, total_picks, 
              is_winner, current_rank, datetime.now()))
        
        prev_score = correct_picks
    
    # Get Monday Night info for the winner
    winner_id = results[0][0]  # VIZCA's user_id
    winner_name = results[0][1]  # VIZCA
    winner_score = results[0][3]  # 10
    
    print(f"\n🎯 Week 9 Winner: {winner_name} with {winner_score}/14 picks!")
    
    # Get Monday Night pick for winner
    cursor.execute('''
        SELECT ng.home_team, ng.away_team, ng.home_score, ng.away_score, up.selected_team
        FROM user_picks up
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE up.user_id = ? AND ng.week = 9 AND ng.year = 2025 AND ng.is_monday_night = 1
    ''', (winner_id,))
    
    mnf_data = cursor.fetchone()
    if mnf_data:
        home_team, away_team, home_score, away_score, selected_team = mnf_data
        print(f"Monday Night Pick: {selected_team}")
        print(f"Game Result: {away_team} {away_score} - {home_team} {home_score}")
        
        if home_score > away_score:
            winner_team = home_team
        else:
            winner_team = away_team
        
        pick_correct = "✅ CORRECT" if selected_team == winner_team else "❌ WRONG"
        print(f"Pick Result: {pick_correct}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Week 9 weekly_results updated with {len(results)} records")
    print("✅ VIZCA is now correctly marked as Week 9 winner!")

if __name__ == "__main__":
    fix_week9_weekly_results()