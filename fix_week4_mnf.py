#!/usr/bin/env python3
"""
Fix Monday Night Football detection for Week 4
- Correct the MNF flags 
- Fix game times that are causing incorrect MNF detection
- Remove MNF flag from Tuesday Bengals game
"""

import sqlite3
from datetime import datetime

def fix_week4_mnf():
    """Fix Week 4 Monday Night Football issues"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print('🏈 FIXING WEEK 4 MONDAY NIGHT FOOTBALL ISSUES')
    print('=' * 60)
    
    # Show current state
    print('\n📊 CURRENT STATE:')
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_monday_night,
               strftime('%w', game_date) as day_of_week
        FROM nfl_games 
        WHERE week = 4 AND year = 2025
        AND (strftime('%w', game_date) = '1' OR strftime('%w', game_date) = '2')
        ORDER BY game_date
    ''')
    
    games = cursor.fetchall()
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    for game in games:
        day_name = day_names[int(game[5])]
        print(f'  {game[1]} @ {game[2]} ({day_name}) - MNF: {game[4]} - Date: {game[3]} (ID: {game[0]})')
    
    print('\n🔧 APPLYING FIXES:')
    
    # Fix 1: Remove MNF flag from CIN @ DEN (Tuesday game)
    cursor.execute('''
        UPDATE nfl_games 
        SET is_monday_night = 0
        WHERE id = 198 AND away_team = 'CIN' AND home_team = 'DEN'
    ''')
    if cursor.rowcount > 0:
        print('  ✅ Removed MNF flag from CIN @ DEN (Tuesday game)')
    
    # Fix 2: Remove MNF flag from GB @ DAL (incorrect Monday game)
    cursor.execute('''
        UPDATE nfl_games 
        SET is_monday_night = 0
        WHERE id = 196 AND away_team = 'GB' AND home_team = 'DAL'
    ''')
    if cursor.rowcount > 0:
        print('  ✅ Removed MNF flag from GB @ DAL (early Monday game)')
    
    # Fix 3: Ensure NYJ @ MIA has MNF flag (should already be correct)
    cursor.execute('''
        UPDATE nfl_games 
        SET is_monday_night = 1
        WHERE id = 197 AND away_team = 'NYJ' AND home_team = 'MIA'
    ''')
    if cursor.rowcount > 0:
        print('  ✅ Confirmed MNF flag for NYJ @ MIA (primetime Monday game)')
    
    # Fix 4: Correct the GB @ DAL game time to be Sunday night instead of early Monday
    cursor.execute('''
        UPDATE nfl_games 
        SET game_date = '2025-09-28 20:20:00'
        WHERE id = 196 AND away_team = 'GB' AND home_team = 'DAL'
    ''')
    if cursor.rowcount > 0:
        print('  ✅ Moved GB @ DAL to Sunday night (20:20)')
    
    conn.commit()
    
    print('\n📊 UPDATED STATE:')
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_monday_night,
               strftime('%w', game_date) as day_of_week
        FROM nfl_games 
        WHERE week = 4 AND year = 2025
        AND (strftime('%w', game_date) IN ('0', '1', '2'))  -- Sunday, Monday, Tuesday
        ORDER BY game_date
    ''')
    
    games = cursor.fetchall()
    
    for game in games:
        day_name = day_names[int(game[5])]
        mnf_indicator = ' 🏈 MNF' if game[4] else ''
        print(f'  {game[1]} @ {game[2]} ({day_name}) - Date: {game[3]} (ID: {game[0]}){mnf_indicator}')
    
    print('\n🎯 TESTING MNF DETECTION LOGIC:')
    cursor.execute('''
        SELECT id, away_team, home_team, game_date
        FROM nfl_games 
        WHERE week = 4 AND year = 2025
        AND strftime('%w', game_date) = '1'
        ORDER BY game_date DESC, id DESC
        LIMIT 1
    ''')
    
    detected_mnf = cursor.fetchone()
    if detected_mnf:
        print(f'  🏆 Detected MNF: {detected_mnf[1]} @ {detected_mnf[2]} (ID: {detected_mnf[0]})')
    else:
        print('  ❌ No Monday games detected!')
    
    conn.close()
    print('\n✅ Week 4 Monday Night Football fixes completed!')

if __name__ == "__main__":
    fix_week4_mnf()