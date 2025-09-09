#!/usr/bin/env python3
"""
Debug template context for specific user
"""

import sqlite3
from datetime import datetime
import sys
import os

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deadline_manager import DeadlineManager
from nfl_week_calculator import get_current_nfl_week

def debug_user_context(username):
    """Debug what template context a specific user would receive"""
    
    print(f'=== DEBUGGING TEMPLATE CONTEXT FOR {username.upper()} ===')
    
    # Get user info
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, is_admin, is_active FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user:
        print(f'❌ User {username} not found!')
        conn.close()
        return
    
    user_id, username, is_admin, is_active = user
    
    print(f'User Info:')
    print(f'  ID: {user_id}')
    print(f'  Username: {username}')
    print(f'  Is Admin: {is_admin} ({"ADMIN" if is_admin else "USER"})')
    print(f'  Is Active: {is_active}')
    
    # Get current NFL week
    current_week = get_current_nfl_week()
    print(f'\nCurrent NFL Week: {current_week}')
    
    # Get deadline summary for current week
    deadline_manager = DeadlineManager()
    deadline_summary = deadline_manager.get_deadline_summary(current_week, 2025)
    
    print(f'\nDeadline Summary for Week {current_week}:')
    print(f'  all_deadlines_passed: {deadline_summary["all_deadlines_passed"]}')
    print(f'  next_deadline: {deadline_summary["next_deadline"]}')
    
    # Template condition logic
    template_condition = is_admin and deadline_summary["all_deadlines_passed"]
    print(f'\nTemplate Condition Analysis:')
    print(f'  is_admin: {is_admin}')
    print(f'  all_deadlines_passed: {deadline_summary["all_deadlines_passed"]}')
    print(f'  is_admin AND all_deadlines_passed: {template_condition}')
    
    print(f'\n🔍 Export Button Should Be Visible: {"YES" if template_condition else "NO"}')
    
    # Check if there are any deadline overrides for this user
    cursor.execute('SELECT game_type, deadline_override FROM deadline_overrides WHERE user_id = ?', (user_id,))
    overrides = cursor.fetchall()
    
    if overrides:
        print(f'\nDeadline Overrides for {username}:')
        for game_type, override_time in overrides:
            print(f'  {game_type}: {override_time}')
    else:
        print(f'\nNo deadline overrides for {username}')
    
    # Check recent activity that might affect session
    cursor.execute('''
        SELECT game_id, predicted_winner, confidence, tiebreaker_score, submission_time 
        FROM user_picks 
        WHERE user_id = ? 
        ORDER BY submission_time DESC 
        LIMIT 5
    ''', (user_id,))
    recent_picks = cursor.fetchall()
    
    if recent_picks:
        print(f'\nRecent picks by {username}:')
        for game_id, winner, confidence, tiebreaker, submission_time in recent_picks:
            print(f'  Game {game_id}: {winner} (confidence: {confidence}, tiebreaker: {tiebreaker}) at {submission_time}')
    
    conn.close()

def check_session_issues():
    """Check for potential session-related issues"""
    print('\n=== POTENTIAL SESSION ISSUES ===')
    
    # Check if there might be any caching issues
    print('Potential causes for incorrect button visibility:')
    print('1. Browser cache - user seeing cached version of page')
    print('2. Session data - old session data with incorrect admin status')
    print('3. Template caching - Flask template cache showing old version')
    print('4. Multiple user sessions - user logged in as different account')
    print('5. Race condition - deadline status changed after page load')
    
    print('\nRecommended troubleshooting steps:')
    print('1. Ask kristian to hard refresh the page (Ctrl+F5)')
    print('2. Ask kristian to log out and log back in')
    print('3. Check if kristian has multiple browser tabs/windows open')
    print('4. Verify the URL kristian is viewing')
    print('5. Check server logs for kristian\'s recent requests')

if __name__ == "__main__":
    # Debug kristian specifically
    debug_user_context('kristian')
    
    # Also debug admin user for comparison
    print('\n' + '='*60)
    debug_user_context('admin')
    
    # Check for session issues
    check_session_issues()
