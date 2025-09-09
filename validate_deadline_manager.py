#!/usr/bin/env python3
"""
Validate deadline manager for kristian user issue
"""

from deadline_manager import DeadlineManager
from nfl_week_calculator import get_current_nfl_week
import sqlite3

def validate_deadline_manager():
    print('=== DEADLINE MANAGER VALIDATION ===')
    current_week = get_current_nfl_week()
    print(f'Current Week: {current_week}')

    dm = DeadlineManager()

    # Test Week 1 (should have all deadlines passed)
    print(f'\n--- WEEK 1 DEADLINES ---')
    week1_summary = dm.get_deadline_summary(1, 2025)
    print(f'Week 1 all_deadlines_passed: {week1_summary["all_deadlines_passed"]}')

    # Test Week 2 (should NOT have all deadlines passed)
    print(f'\n--- WEEK 2 DEADLINES ---')
    week2_summary = dm.get_deadline_summary(2, 2025)
    print(f'Week 2 all_deadlines_passed: {week2_summary["all_deadlines_passed"]}')

    if week2_summary.get('next_deadline'):
        nd = week2_summary['next_deadline']
        print(f'Next deadline: {nd["type"]} - {nd["formatted_time"]}')
    else:
        print('No next deadline found')

    # Check Week 2 games
    print(f'\n--- WEEK 2 GAMES CHECK ---')
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 2 AND year = 2025')
    week2_games = cursor.fetchone()[0]
    print(f'Week 2 games in database: {week2_games}')

    if week2_games > 0:
        cursor.execute('''
            SELECT game_date, home_team, away_team 
            FROM nfl_games 
            WHERE week = 2 AND year = 2025 
            ORDER BY game_date LIMIT 3
        ''')
        games = cursor.fetchall()
        print('First 3 Week 2 games:')
        for game_date, home, away in games:
            print(f'  {away} @ {home} - {game_date}')
    else:
        print('No Week 2 games found in database!')

    # Check user kristian
    cursor.execute('SELECT id, is_admin FROM users WHERE username = "kristian"')
    user = cursor.fetchone()
    if user:
        user_id, is_admin = user
        print(f'\n--- USER kristian CHECK ---')
        print(f'kristian user_id: {user_id}, is_admin: {is_admin}')
        
        # Get user-specific deadline summary for current week
        user_summary = dm.get_user_deadline_summary(current_week, 2025, user_id)
        print(f'kristian Week {current_week} all_deadlines_passed: {user_summary["all_deadlines_passed"]}')
        
        if user_summary.get('next_deadline'):
            nd = user_summary['next_deadline']
            print(f'kristian next deadline: {nd["type"]} - {nd["formatted_time"]}')
        else:
            print('kristian has no upcoming deadlines')
        
        # Check template conditions
        print(f'\n--- TEMPLATE CONDITIONS ---')
        print(f'is_admin: {is_admin}')
        print(f'all_deadlines_passed: {user_summary["all_deadlines_passed"]}')
        should_show_export = is_admin and user_summary["all_deadlines_passed"]
        print(f'Should show Export All Users: {should_show_export}')
        
        if not is_admin and user_summary["all_deadlines_passed"]:
            print('🚨 PROBLEM: Regular user with all_deadlines_passed=True')
        elif is_admin and not user_summary["all_deadlines_passed"]:
            print('✅ CORRECT: Admin but deadlines not all passed')
        elif not is_admin and not user_summary["all_deadlines_passed"]:
            print('✅ CORRECT: Regular user and deadlines not all passed')
        else:
            print('✅ CORRECT: Admin and all deadlines passed')
            
    else:
        print('User kristian not found')

    conn.close()

if __name__ == "__main__":
    validate_deadline_manager()
