#!/usr/bin/env python3
"""
Test script to verify weekly leaderboard data display
"""

import sqlite3
from datetime import datetime

def test_weekly_leaderboard_data():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🏈 Testing Weekly Leaderboard Data for Week 1")
    print("=" * 50)
    
    # Get all users and their weekly performance
    cursor.execute('''
        SELECT 
            u.id,
            u.username,
            COUNT(CASE WHEN 
                (p.predicted_home_score > p.predicted_away_score AND g.home_score > g.away_score) OR
                (p.predicted_home_score < p.predicted_away_score AND g.home_score < g.away_score)
                THEN 1 END) as correct_picks,
            COUNT(p.id) as total_picks
        FROM users u
        LEFT JOIN user_picks p ON u.id = p.user_id
        LEFT JOIN nfl_games g ON p.game_id = g.id
        WHERE g.week = 1
        GROUP BY u.id, u.username
        ORDER BY correct_picks DESC, u.username
    ''')
    
    weekly_data = cursor.fetchall()
    print(f"\n📊 Weekly Leaderboard Rankings:")
    for i, (user_id, username, correct, total) in enumerate(weekly_data, 1):
        print(f"  {i}. {username}: {correct}/{total} correct picks")
    
    # Check Monday Night Football pick status
    cursor.execute('''
        SELECT 
            g.id,
            g.home_team,
            g.away_team,
            g.is_final,
            g.is_monday_night,
            COUNT(p.id) as pick_count
        FROM nfl_games g
        LEFT JOIN user_picks p ON g.id = p.game_id
        WHERE g.week = 1 AND g.is_monday_night = 1
        GROUP BY g.id
    ''')
    
    mnf_data = cursor.fetchone()
    if mnf_data:
        game_id, home, away, is_final, is_mnf, pick_count = mnf_data
        status = "Final" if is_final else "In Progress"
        print(f"\n🌙 Monday Night Football:")
        print(f"  Game: {away} @ {home}")
        print(f"  Status: {status}")
        print(f"  Picks submitted: {pick_count}")
    
    # Show all picks for each user in Week 1
    print(f"\n📋 All User Picks for Week 1:")
    print("=" * 50)
    
    cursor.execute('''
        SELECT 
            u.username,
            g.away_team,
            g.home_team,
            p.predicted_away_score,
            p.predicted_home_score,
            g.away_score,
            g.home_score,
            g.is_final,
            g.is_monday_night,
            CASE WHEN 
                (p.predicted_home_score > p.predicted_away_score AND g.home_score > g.away_score) OR
                (p.predicted_home_score < p.predicted_away_score AND g.home_score < g.away_score)
                THEN 'Correct' 
                WHEN g.is_final = 1 THEN 'Incorrect'
                ELSE 'Pending'
            END as result
        FROM users u
        JOIN user_picks p ON u.id = p.user_id
        JOIN nfl_games g ON p.game_id = g.id
        WHERE g.week = 1
        ORDER BY u.username, g.game_date, g.id
    ''')
    
    all_picks = cursor.fetchall()
    current_user = None
    
    for pick in all_picks:
        username, away, home, pred_away, pred_home, actual_away, actual_home, is_final, is_mnf, result = pick
        
        if current_user != username:
            if current_user is not None:
                print()  # Add space between users
            current_user = username
            print(f"\n👤 {username}:")
        
        # Format the pick display
        pred_display = f"{pred_away}-{pred_home}"
        if is_final:
            actual_display = f"{actual_away}-{actual_home}"
        else:
            actual_display = "TBD"
        
        mnf_indicator = " 🌙" if is_mnf else ""
        print(f"  {away} @ {home}{mnf_indicator}: {pred_display} → {actual_display} ({result})")
    
    conn.close()

if __name__ == "__main__":
    test_weekly_leaderboard_data()
