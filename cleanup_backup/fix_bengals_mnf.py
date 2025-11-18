#!/usr/bin/env python3
"""
Fix Bengals @ Broncos Monday Night Football game
- Move from Tuesday midnight to Monday 7:15 PM AST  
- Set MNF flag for both Monday games (Jets @ Dolphins and Bengals @ Broncos)
"""

import sqlite3

def fix_bengals_mnf():
    """Fix Bengals @ Broncos Monday Night Football scheduling"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print('🏈 FIXING BENGALS @ BRONCOS MONDAY NIGHT FOOTBALL')
    print('=' * 55)
    
    # Show current state
    print('\n📊 CURRENT STATE:')
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_monday_night,
               strftime('%w', game_date) as day_of_week
        FROM nfl_games 
        WHERE week = 4 AND year = 2025
        AND (away_team = 'CIN' OR away_team = 'NYJ')
        ORDER BY game_date
    ''')
    
    games = cursor.fetchall()
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    for game in games:
        day_name = day_names[int(game[5])]
        mnf_flag = '🏈 MNF' if game[4] else ''
        print(f'  {game[1]} @ {game[2]} ({day_name}) - {game[3]} {mnf_flag} (ID: {game[0]})')
    
    print('\n🔧 APPLYING FIXES:')
    
    # Fix 1: Move Bengals @ Broncos to Monday 7:15 PM AST (19:15)
    cursor.execute('''
        UPDATE nfl_games 
        SET game_date = '2025-09-29 19:15:00'
        WHERE id = 198 AND away_team = 'CIN' AND home_team = 'DEN'
    ''')
    if cursor.rowcount > 0:
        print('  ✅ Moved CIN @ DEN to Monday 7:15 PM AST')
    
    # Fix 2: Set MNF flag for Bengals @ Broncos
    cursor.execute('''
        UPDATE nfl_games 
        SET is_monday_night = 1
        WHERE id = 198 AND away_team = 'CIN' AND home_team = 'DEN'
    ''')
    if cursor.rowcount > 0:
        print('  ✅ Set MNF flag for CIN @ DEN')
    
    # Fix 3: Ensure Jets @ Dolphins keeps MNF flag
    cursor.execute('''
        UPDATE nfl_games 
        SET is_monday_night = 1
        WHERE id = 197 AND away_team = 'NYJ' AND home_team = 'MIA'
    ''')
    if cursor.rowcount > 0:
        print('  ✅ Confirmed MNF flag for NYJ @ MIA')
    
    conn.commit()
    
    print('\n📊 UPDATED STATE:')
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_monday_night,
               strftime('%w', game_date) as day_of_week
        FROM nfl_games 
        WHERE week = 4 AND year = 2025
        AND (away_team = 'CIN' OR away_team = 'NYJ')
        ORDER BY game_date
    ''')
    
    games = cursor.fetchall()
    
    for game in games:
        day_name = day_names[int(game[5])]
        mnf_indicator = ' 🏈 MNF' if game[4] else ''
        print(f'  {game[1]} @ {game[2]} ({day_name}) - {game[3]} (ID: {game[0]}){mnf_indicator}')
    
    print('\n🎯 TESTING MNF DETECTION:')
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_monday_night
        FROM nfl_games 
        WHERE week = 4 AND year = 2025 AND is_monday_night = 1
        ORDER BY game_date
    ''')
    
    mnf_games = cursor.fetchall()
    if mnf_games:
        print(f'  Found {len(mnf_games)} Monday Night Football games:')
        for game in mnf_games:
            print(f'    🏆 {game[1]} @ {game[2]} - {game[3]} (ID: {game[0]})')
    else:
        print('  ❌ No MNF games found!')
    
    # Test the latest Monday game detection logic
    print('\n🔍 LATEST MONDAY GAME DETECTION:')
    cursor.execute('''
        SELECT id, away_team, home_team, game_date
        FROM nfl_games 
        WHERE week = 4 AND year = 2025
        AND strftime('%w', game_date) = '1'
        ORDER BY game_date DESC, id DESC
        LIMIT 1
    ''')
    
    latest_monday = cursor.fetchone()
    if latest_monday:
        print(f'  Latest Monday game: {latest_monday[1]} @ {latest_monday[2]} (ID: {latest_monday[0]})')
        print('  (This is what the app will use for tiebreaker logic)')
    
    conn.close()
    print('\n✅ Bengals Monday Night Football fix completed!')
    print('📺 Week 4 now has TWO Monday Night Football games:')
    print('   - Jets @ Dolphins (6:15 PM AST / 7:15 PM Bolivia Time)')
    print('   - Bengals @ Broncos (7:15 PM AST / 8:15 PM Bolivia Time)')

if __name__ == "__main__":
    fix_bengals_mnf()