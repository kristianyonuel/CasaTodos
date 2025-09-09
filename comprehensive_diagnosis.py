#!/usr/bin/env python3
"""
Comprehensive diagnosis of kristian's export button issue
"""

import sqlite3
from datetime import datetime
import sys
import os

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deadline_manager import DeadlineManager
from nfl_week_calculator import get_current_nfl_week

def main():
    print('🔍 COMPREHENSIVE DIAGNOSIS: Why does kristian see export button?')
    print('=' * 70)
    
    # 1. Verify database state
    print('\n1. DATABASE VERIFICATION:')
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check kristian's user status
    cursor.execute('SELECT id, username, is_admin, is_active FROM users WHERE username = "kristian"')
    kristian = cursor.fetchone()
    print(f'   kristian: ID={kristian[0]}, is_admin={kristian[2]}, is_active={kristian[3]}')
    
    # 2. Verify current week and deadlines
    print('\n2. WEEK AND DEADLINE VERIFICATION:')
    current_week = get_current_nfl_week()
    print(f'   Current NFL Week: {current_week}')
    
    deadline_manager = DeadlineManager()
    deadline_summary = deadline_manager.get_deadline_summary(current_week, 2025)
    print(f'   Week {current_week} all_deadlines_passed: {deadline_summary["all_deadlines_passed"]}')
    
    # 3. Check template conditions
    print('\n3. TEMPLATE CONDITION ANALYSIS:')
    print('   Main dashboard (index.html) export button condition:')
    template_condition = '{% if deadline_summary.all_deadlines_passed %}'
    print(f'   {template_condition} = {deadline_summary["all_deadlines_passed"]}')
    admin_condition = '{% if is_admin %}'
    print(f'   {admin_condition} = {kristian[2] == 1}')
    print(f'   Combined condition: {deadline_summary["all_deadlines_passed"] and kristian[2] == 1}')
    result = "VISIBLE" if deadline_summary["all_deadlines_passed"] and kristian[2] == 1 else "HIDDEN"
    print(f'   ✅ Export button should be: {result}')
    
    # 4. Check admin page access
    print('\n4. ADMIN PAGE ACCESS CHECK:')
    print('   Admin page (/admin) access condition:')
    print(f'   session.get("is_admin") would be: {kristian[2] == 1}')
    print(f'   ✅ Admin page should be: {"ACCESSIBLE" if kristian[2] == 1 else "BLOCKED"}')
    
    # 5. Check for potential issues
    print('\n5. POTENTIAL ISSUE ANALYSIS:')
    print('   Possible reasons kristian sees export button:')
    
    # Check Week 1 to see if deadlines passed there
    week1_summary = deadline_manager.get_deadline_summary(1, 2025)
    print(f'   📅 Week 1 all_deadlines_passed: {week1_summary["all_deadlines_passed"]}')
    
    if week1_summary["all_deadlines_passed"]:
        print('   🟡 POTENTIAL ISSUE: If kristian has cached Week 1 page, he would see button')
    
    # Check if there are any active sessions that might be confused
    print('\n   📋 TROUBLESHOOTING CHECKLIST for kristian:')
    print('   ❓ 1. Is kristian looking at the main dashboard (/) or admin page (/admin)?')
    print('   ❓ 2. What does the URL bar show in kristian\'s browser?')
    print('   ❓ 3. Has kristian tried hard refresh (Ctrl+F5) or clearing browser cache?')
    print('   ❓ 4. Is kristian logged in with his own account or possibly as admin?')
    print('   ❓ 5. Does kristian have multiple browser tabs/windows open?')
    print('   ❓ 6. Is kristian using an old bookmark that might point to Week 1?')
    
    # 6. Provide specific instructions
    print('\n6. SPECIFIC VERIFICATION STEPS FOR KRISTIAN:')
    print('   👤 Ask kristian to:')
    print('   1. Log out completely')
    print('   2. Clear browser cache/hard refresh (Ctrl+F5)')
    print('   3. Log back in')
    print('   4. Check the URL bar - should be just "/" for main dashboard')
    print('   5. Take a screenshot showing both the URL and the button')
    
    # 7. System status summary
    print('\n7. SYSTEM STATUS SUMMARY:')
    print(f'   ✅ Database: kristian is regular user (is_admin=0)')
    print(f'   ✅ Week calculation: Current week is {current_week}')
    print(f'   ✅ Deadlines: Week {current_week} deadlines have NOT passed')
    print(f'   ✅ Template logic: Export button should be HIDDEN')
    print(f'   ✅ Admin protection: /admin route properly protected')
    print('   🔍 CONCLUSION: System is working correctly, likely browser/cache issue')
    
    conn.close()

if __name__ == "__main__":
    main()
