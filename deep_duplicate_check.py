#!/usr/bin/env python3
"""
Deep investigation into duplicate picks causing inflated counts
"""

import sqlite3

def deep_duplicate_investigation():
    """Find all types of duplicate picks"""
    print("🔍 DEEP DUPLICATE INVESTIGATION")
    print("=" * 60)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check 1: Multiple picks for same user-game combination
    print("1️⃣ CHECKING MULTIPLE PICKS PER USER-GAME:")
    cursor.execute('''
        SELECT p.user_id, u.username, p.game_id, g.week, g.year,
               COUNT(*) as pick_count,
               GROUP_CONCAT(p.id) as pick_ids,
               GROUP_CONCAT(p.is_correct) as correctness_values
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        JOIN nfl_games g ON p.game_id = g.id
        GROUP BY p.user_id, p.game_id
        HAVING COUNT(*) > 1
        ORDER BY pick_count DESC, u.username
    ''')
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print("❌ FOUND DUPLICATE PICKS:")
        print("User | Game | Week | Year | Count | Pick IDs | Correctness")
        print("-" * 65)
        for user_id, username, game_id, week, year, count, pick_ids, correctness in duplicates:
            print(f"{username:8} | {game_id:4} | {week:4} | {year:4} | {count:5} | {pick_ids:8} | {correctness}")
    else:
        print("✅ No duplicate user-game picks found")
    
    # Check 2: Same user, same week, multiple games with same teams
    print(f"\n2️⃣ CHECKING FOR DUPLICATE GAMES (same teams, same week):")
    cursor.execute('''
        SELECT week, year, home_team, away_team, COUNT(*) as game_count,
               GROUP_CONCAT(id) as game_ids
        FROM nfl_games
        GROUP BY week, year, home_team, away_team
        HAVING COUNT(*) > 1
        ORDER BY game_count DESC
    ''')
    
    duplicate_games = cursor.fetchall()
    
    if duplicate_games:
        print("❌ FOUND DUPLICATE GAMES:")
        print("Week | Year | Home | Away | Count | Game IDs")
        print("-" * 50)
        for week, year, home, away, count, game_ids in duplicate_games:
            print(f"{week:4} | {year:4} | {home:4} | {away:4} | {count:5} | {game_ids}")
    else:
        print("✅ No duplicate games found")
    
    # Check 3: Raymond's specific picks analysis
    print(f"\n3️⃣ RAYMOND'S DETAILED PICK ANALYSIS:")
    cursor.execute('SELECT id FROM users WHERE username = "raymond"')
    raymond_result = cursor.fetchone()
    
    if raymond_result:
        raymond_id = raymond_result[0]
        
        # Get ALL of Raymond's picks with full details
        cursor.execute('''
            SELECT p.id as pick_id, p.game_id, g.week, g.year,
                   g.home_team, g.away_team, p.selected_team,
                   p.is_correct, g.is_final, p.created_at
            FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            WHERE p.user_id = ?
            ORDER BY g.week, g.year, g.game_date, p.created_at
        ''', (raymond_id,))
        
        raymond_all_picks = cursor.fetchall()
        
        print(f"Raymond has {len(raymond_all_picks)} total picks:")
        print("Pick ID | Game ID | Week | Year | Home | Away | Selected | Correct | Final | Created")
        print("-" * 85)
        
        week1_correct = 0
        for pick_id, game_id, week, year, home, away, selected, correct, final, created in raymond_all_picks:
            if week == 1 and year == 2025 and correct == 1:
                week1_correct += 1
            print(f"{pick_id:7} | {game_id:7} | {week:4} | {year:4} | {home:4} | {away:4} | {selected:8} | {correct:7} | {final:5} | {created}")
        
        print(f"\nRaymond's Week 1 correct picks: {week1_correct}")
    
    # Check 4: Current leaderboard query debug
    print(f"\n4️⃣ CURRENT LEADERBOARD QUERY DEBUG:")
    cursor.execute('''
        SELECT u.username,
               SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as old_total,
               SUM(CASE WHEN p.is_correct = 1 AND g.is_final = 1 THEN 1 ELSE 0 END) as new_total
        FROM users u
        LEFT JOIN user_picks p ON u.id = p.user_id
        LEFT JOIN nfl_games g ON p.game_id = g.id
        WHERE u.is_admin = 0 AND u.username IN ('raymond', 'coyote')
        GROUP BY u.id, u.username
    ''')
    
    query_comparison = cursor.fetchall()
    
    print("User | Old Query Total | New Query Total")
    print("-" * 40)
    for username, old_total, new_total in query_comparison:
        print(f"{username:8} | {old_total:15} | {new_total:15}")
    
    # Check 5: Pick correctness investigation
    print(f"\n5️⃣ PICK CORRECTNESS INVESTIGATION:")
    cursor.execute('''
        SELECT u.username,
               COUNT(p.id) as total_picks,
               COUNT(CASE WHEN p.is_correct = 1 THEN 1 END) as correct_count,
               COUNT(CASE WHEN p.is_correct = 0 THEN 1 END) as incorrect_count,
               COUNT(CASE WHEN p.is_correct IS NULL THEN 1 END) as null_count
        FROM users u
        JOIN user_picks p ON u.id = p.user_id
        WHERE u.username IN ('raymond', 'coyote')
        GROUP BY u.id, u.username
    ''')
    
    correctness_data = cursor.fetchall()
    
    print("User | Total Picks | Correct | Incorrect | Null")
    print("-" * 50)
    for username, total, correct, incorrect, null in correctness_data:
        print(f"{username:8} | {total:11} | {correct:7} | {incorrect:9} | {null:4}")
    
    conn.close()

if __name__ == "__main__":
    deep_duplicate_investigation()
