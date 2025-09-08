#!/usr/bin/env python3
"""
Investigate why users have more correct picks than possible games
"""

import sqlite3

def investigate_pick_anomaly():
    """Check why some users have impossible pick counts"""
    print("🔍 INVESTIGATING PICK COUNT ANOMALY")
    print("=" * 60)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # First, get basic Week 1 info
    cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 1 AND year = 2025')
    total_games_week1 = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 1 AND year = 2025 AND is_final = 1')
    final_games_week1 = cursor.fetchone()[0]
    
    print(f"📊 Week 1, 2025: {total_games_week1} total games, {final_games_week1} final games")
    
    # Check each user's picks for Week 1
    print("\n👥 USER PICKS FOR WEEK 1:")
    cursor.execute('''
        SELECT u.username, u.id,
               COUNT(p.id) as total_picks,
               COUNT(CASE WHEN p.is_correct = 1 THEN 1 END) as correct_picks,
               COUNT(CASE WHEN p.is_correct = 0 THEN 1 END) as incorrect_picks,
               COUNT(CASE WHEN p.is_correct IS NULL THEN 1 END) as null_picks
        FROM users u
        LEFT JOIN user_picks p ON u.id = p.user_id
        LEFT JOIN nfl_games g ON p.game_id = g.id
        WHERE u.is_admin = 0 AND (g.week = 1 AND g.year = 2025 OR g.week IS NULL)
        GROUP BY u.id, u.username
        ORDER BY correct_picks DESC
    ''')
    
    user_results = cursor.fetchall()
    
    print("Username | ID | Total Picks | Correct | Incorrect | Null | Issue?")
    print("-" * 70)
    
    for username, user_id, total_picks, correct, incorrect, null_picks in user_results:
        issue = "❌ TOO MANY!" if correct > total_games_week1 else "✅"
        print(f"{username:12} | {user_id:2} | {total_picks:11} | {correct:7} | {incorrect:9} | {null_picks:4} | {issue}")
    
    # Let's specifically check Raymond's picks
    print(f"\n🔍 DETAILED CHECK FOR RAYMOND:")
    cursor.execute('SELECT id FROM users WHERE username = "raymond"')
    raymond_result = cursor.fetchone()
    
    if raymond_result:
        raymond_id = raymond_result[0]
        
        # Get all of Raymond's picks across all weeks
        cursor.execute('''
            SELECT g.week, g.year, COUNT(p.id) as picks,
                   COUNT(CASE WHEN p.is_correct = 1 THEN 1 END) as correct,
                   COUNT(CASE WHEN g.is_final = 1 THEN 1 END) as final_games
            FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            WHERE p.user_id = ?
            GROUP BY g.week, g.year
            ORDER BY g.year, g.week
        ''', (raymond_id,))
        
        raymond_picks = cursor.fetchall()
        
        print("Week | Year | Picks | Correct | Final Games")
        print("-" * 45)
        for week, year, picks, correct, final_games in raymond_picks:
            print(f"{week:4} | {year:4} | {picks:5} | {correct:7} | {final_games:11}")
    
    # Check if there are duplicate picks
    print(f"\n🔍 CHECKING FOR DUPLICATE PICKS:")
    cursor.execute('''
        SELECT p.user_id, p.game_id, COUNT(*) as pick_count
        FROM user_picks p
        JOIN nfl_games g ON p.game_id = g.id
        WHERE g.week = 1 AND g.year = 2025
        GROUP BY p.user_id, p.game_id
        HAVING COUNT(*) > 1
        ORDER BY pick_count DESC
    ''')
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print("❌ FOUND DUPLICATE PICKS:")
        print("User ID | Game ID | Pick Count")
        print("-" * 30)
        for user_id, game_id, count in duplicates:
            cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
            username = cursor.fetchone()[0]
            print(f"{user_id:7} | {game_id:7} | {count:10} ({username})")
    else:
        print("✅ No duplicate picks found")
    
    # Check if picks are being counted from multiple weeks
    print(f"\n🔍 CHECKING LEADERBOARD QUERY LOGIC:")
    cursor.execute('''
        SELECT u.username,
               SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as total_correct_all_weeks,
               SUM(CASE WHEN p.is_correct = 1 AND g.week = 1 AND g.year = 2025 THEN 1 ELSE 0 END) as correct_week1_only
        FROM users u
        LEFT JOIN user_picks p ON u.id = p.user_id
        LEFT JOIN nfl_games g ON p.game_id = g.id
        WHERE u.is_admin = 0
        GROUP BY u.id, u.username
        HAVING total_correct_all_weeks > 0
        ORDER BY total_correct_all_weeks DESC
    ''')
    
    all_weeks_results = cursor.fetchall()
    
    print("Username | All Weeks Correct | Week 1 Only Correct")
    print("-" * 50)
    for username, all_weeks, week1_only in all_weeks_results:
        print(f"{username:12} | {all_weeks:17} | {week1_only:18}")
    
    conn.close()

if __name__ == "__main__":
    investigate_pick_anomaly()
