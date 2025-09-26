#!/usr/bin/env python3
"""
Minimal Monday Night Football fix - only fix the specific MNF issue
without changing other game times that might cause server compatibility issues
"""

import sqlite3

def minimal_mnf_fix():
    """Apply only the essential MNF fixes for Week 4"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print('🏈 MINIMAL MONDAY NIGHT FOOTBALL FIX')
    print('=' * 40)
    
    # Check current state of Week 4 Monday games
    print('\n📊 CURRENT WEEK 4 MONDAY GAMES:')
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_monday_night
        FROM nfl_games 
        WHERE week = 4 AND year = 2025
        AND (away_team IN ('NYJ', 'CIN') OR home_team IN ('MIA', 'DEN'))
    ''')
    
    current_games = cursor.fetchall()
    for game in current_games:
        mnf_flag = ' (MNF)' if game[4] else ''
        print(f'  {game[1]} @ {game[2]} - {game[3]}{mnf_flag} (ID: {game[0]})')
    
    # Only fix if there are obvious issues
    issues_fixed = 0
    
    # Fix 1: Ensure CIN @ DEN has MNF flag (if it doesn't)
    cursor.execute('''
        UPDATE nfl_games 
        SET is_monday_night = 1
        WHERE week = 4 AND year = 2025 
        AND away_team = 'CIN' AND home_team = 'DEN'
        AND is_monday_night = 0
    ''')
    if cursor.rowcount > 0:
        print('\n✅ Set MNF flag for CIN @ DEN')
        issues_fixed += 1
    
    # Fix 2: Ensure NYJ @ MIA has MNF flag (if it doesn't)  
    cursor.execute('''
        UPDATE nfl_games 
        SET is_monday_night = 1
        WHERE week = 4 AND year = 2025 
        AND away_team = 'NYJ' AND home_team = 'MIA'
        AND is_monday_night = 0
    ''')
    if cursor.rowcount > 0:
        print('✅ Set MNF flag for NYJ @ MIA')
        issues_fixed += 1
    
    # Fix 3: Only fix obviously wrong times (midnight/early morning)
    cursor.execute('''
        UPDATE nfl_games 
        SET game_date = '2025-09-29 19:15:00'
        WHERE week = 4 AND year = 2025 
        AND away_team = 'NYJ' AND home_team = 'MIA'
        AND (game_date LIKE '%23:%' OR game_date LIKE '%00:%' OR game_date LIKE '%01:%')
    ''')
    if cursor.rowcount > 0:
        print('✅ Fixed NYJ @ MIA time to 7:15 PM')
        issues_fixed += 1
    
    cursor.execute('''
        UPDATE nfl_games 
        SET game_date = '2025-09-29 20:15:00'
        WHERE week = 4 AND year = 2025 
        AND away_team = 'CIN' AND home_team = 'DEN'
        AND (game_date LIKE '2025-09-30%' OR game_date LIKE '%00:%' OR game_date LIKE '%01:%')
    ''')
    if cursor.rowcount > 0:
        print('✅ Fixed CIN @ DEN time to 8:15 PM and moved to Monday')
        issues_fixed += 1
    
    conn.commit()
    
    print(f'\n📊 UPDATED WEEK 4 MONDAY GAMES:')
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_monday_night
        FROM nfl_games 
        WHERE week = 4 AND year = 2025
        AND (away_team IN ('NYJ', 'CIN') OR home_team IN ('MIA', 'DEN'))
        ORDER BY game_date
    ''')
    
    updated_games = cursor.fetchall()
    for game in updated_games:
        mnf_flag = ' 🏈 MNF' if game[4] else ''
        print(f'  {game[1]} @ {game[2]} - {game[3]}{mnf_flag} (ID: {game[0]})')
    
    print(f'\n✅ SUMMARY:')
    print(f'  - Applied {issues_fixed} targeted fixes')
    print(f'  - Preserved all existing user picks and data')
    print(f'  - Only changed essential MNF scheduling')
    print(f'  - Database should be server-compatible')
    
    conn.close()

if __name__ == "__main__":
    minimal_mnf_fix()