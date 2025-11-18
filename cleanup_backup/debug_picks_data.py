#!/usr/bin/env python3

import sqlite3
from datetime import datetime

def debug_picks_data():
    """Debug picks data to understand why 'View All Picks' shows no results"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=== DEBUGGING PICKS DATA ===")
    
    # Check total picks
    cursor.execute('SELECT COUNT(*) as total_picks FROM user_picks')
    total_picks = cursor.fetchone()['total_picks']
    print(f"Total picks in database: {total_picks}")
    
    # Check games data
    print("\n=== AVAILABLE WEEKS IN GAMES TABLE ===")
    cursor.execute('SELECT DISTINCT week, year FROM nfl_games ORDER BY year, week')
    games_weeks = cursor.fetchall()
    for row in games_weeks:
        print(f"  Week {row['week']}, Year {row['year']}")
    
    # Check picks by week/year
    print("\n=== PICKS COUNT BY WEEK/YEAR ===")
    cursor.execute('''
        SELECT g.week, g.year, COUNT(p.id) as pick_count
        FROM nfl_games g
        LEFT JOIN user_picks p ON g.id = p.game_id
        GROUP BY g.week, g.year
        ORDER BY g.year, g.week
    ''')
    picks_by_week = cursor.fetchall()
    for row in picks_by_week:
        print(f"  Week {row['week']}, Year {row['year']}: {row['pick_count']} picks")
    
    # Check sample pick data
    print("\n=== SAMPLE PICK DATA ===")
    cursor.execute('''
        SELECT u.username, g.week, g.year, g.away_team, g.home_team, p.selected_team, p.id as pick_id
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        JOIN nfl_games g ON p.game_id = g.id
        ORDER BY g.year, g.week, u.username
        LIMIT 10
    ''')
    sample_picks = cursor.fetchall()
    for row in sample_picks:
        print(f"  {row['username']}: Week {row['week']} {row['year']} - {row['away_team']} @ {row['home_team']}, picked {row['selected_team']} (pick_id: {row['pick_id']})")
    
    # Test the exact query from admin/all_picks
    print("\n=== TESTING ADMIN ALL_PICKS QUERY ===")
    test_week = 1
    test_year = 2025
    print(f"Testing with Week {test_week}, Year {test_year}")
    
    cursor.execute('''
        SELECT 
            p.id as pick_id,
            u.username,
            g.away_team,
            g.home_team,
            g.game_time,
            g.is_monday_night,
            p.selected_team,
            p.predicted_home_score,
            p.predicted_away_score,
            p.pick_time
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        JOIN nfl_games g ON p.game_id = g.id
        WHERE g.week = ? AND g.year = ?
        ORDER BY u.username, g.game_time
    ''', (test_week, test_year))
    
    admin_picks = cursor.fetchall()
    print(f"Admin query returned {len(admin_picks)} picks")
    
    for row in admin_picks:
        print(f"  {row['username']}: {row['away_team']} @ {row['home_team']}, picked {row['selected_team']}")
    
    # Check if there are any picks for week 1, 2025 specifically
    print(f"\n=== CHECKING SPECIFIC WEEK/YEAR COMBINATIONS ===")
    for week in [1, 2, 3]:
        for year in [2024, 2025]:
            cursor.execute('''
                SELECT COUNT(*) as count FROM user_picks p
                JOIN nfl_games g ON p.game_id = g.id
                WHERE g.week = ? AND g.year = ?
            ''', (week, year))
            count = cursor.fetchone()['count']
            if count > 0:
                print(f"  Week {week}, Year {year}: {count} picks")
    
    conn.close()

if __name__ == '__main__':
    debug_picks_data()
