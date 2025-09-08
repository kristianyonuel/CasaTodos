#!/usr/bin/env python3
"""
Debug the leaderboard calculation to see why averages are wrong
"""

import sqlite3

def debug_leaderboard_calculation():
    """Debug the leaderboard SQL query step by step"""
    print("🔍 DEBUGGING LEADERBOARD CALCULATION")
    print("=" * 60)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Test the exact query from app.py
    print("📊 Testing the current leaderboard query...")
    cursor.execute('''
        SELECT u.username,
               COUNT(DISTINCT CASE WHEN wr.is_winner = 1 THEN wr.week || '-' || wr.year END) as weekly_wins,
               SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as total_games_won,
               COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week || '-' || g.year END) as weeks_played,
               COUNT(CASE WHEN g.is_final = 1 THEN 1 END) as total_games_played,
               ROUND(
                   CASE 
                       WHEN COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week || '-' || g.year END) > 0
                       THEN CAST(SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / 
                            COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week || '-' || g.year END)
                       ELSE 0 
                   END, 1
               ) as avg_games_won_per_week
        FROM users u
        LEFT JOIN user_picks p ON u.id = p.user_id
        LEFT JOIN nfl_games g ON p.game_id = g.id
        LEFT JOIN weekly_results wr ON u.id = wr.user_id
        WHERE u.is_admin = 0
        GROUP BY u.id, u.username
        HAVING COUNT(CASE WHEN g.is_final = 1 THEN 1 END) > 0 OR COUNT(CASE WHEN wr.is_winner = 1 THEN 1 END) > 0
        ORDER BY weekly_wins DESC, total_games_won DESC, avg_games_won_per_week DESC, u.username
    ''')
    
    results = cursor.fetchall()
    
    print("Results breakdown:")
    print("User | Weekly Wins | Total Games Won | Weeks Played | Total Games | Avg Per Week")
    print("-" * 80)
    
    for row in results:
        username, weekly_wins, total_games_won, weeks_played, total_games_played, avg_per_week = row
        print(f"{username:12} | {weekly_wins:11} | {total_games_won:15} | {weeks_played:12} | {total_games_played:11} | {avg_per_week}")
    
    # Let's also test with a simpler approach
    print("\n🧮 Testing simplified calculation...")
    cursor.execute('''
        SELECT u.username,
               COUNT(DISTINCT CASE WHEN wr.is_winner = 1 THEN wr.week END) as weekly_wins,
               SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as total_correct,
               COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week END) as weeks_with_final_games,
               CASE 
                   WHEN COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week END) > 0
                   THEN ROUND(CAST(SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / 
                             COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week END), 1)
                   ELSE 0.0 
               END as calculated_avg
        FROM users u
        LEFT JOIN user_picks p ON u.id = p.user_id AND p.is_correct IS NOT NULL
        LEFT JOIN nfl_games g ON p.game_id = g.id AND g.is_final = 1
        LEFT JOIN weekly_results wr ON u.id = wr.user_id
        WHERE u.is_admin = 0
        GROUP BY u.id, u.username
        ORDER BY weekly_wins DESC, total_correct DESC, calculated_avg DESC, u.username
    ''')
    
    simple_results = cursor.fetchall()
    
    print("Simplified results:")
    print("User | Weekly Wins | Total Correct | Weeks w/ Finals | Calculated Avg")
    print("-" * 70)
    
    for row in simple_results:
        username, weekly_wins, total_correct, weeks_finals, calc_avg = row
        print(f"{username:12} | {weekly_wins:11} | {total_correct:13} | {weeks_finals:15} | {calc_avg}")
    
    conn.close()

if __name__ == "__main__":
    debug_leaderboard_calculation()
