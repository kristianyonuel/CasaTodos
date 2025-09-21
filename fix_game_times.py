#!/usr/bin/env python3
"""
Fix incorrect game times in NFL database
NFL Sunday early games should start at 1:00 PM AST (17:00 UTC), not 9:00 AM AST (13:00 UTC)
"""

import sqlite3
from datetime import datetime, timedelta

def fix_game_times():
    """Fix incorrect game times in the database"""
    
    print("🔧 FIXING NFL GAME TIMES IN DATABASE")
    print("=" * 50)
    
    # Connect to database
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Find games that need time correction
    print("📋 Analyzing games that need time correction...")
    
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, week, year
        FROM nfl_games 
        WHERE week = 3 AND year = 2025 
        AND strftime('%w', game_date) = '0'  -- Sunday
        AND strftime('%H:%M', game_date) = '13:00'  -- 1:00 PM UTC (wrong)
        ORDER BY game_date
    ''')
    
    games_to_fix = cursor.fetchall()
    print(f"Found {len(games_to_fix)} games with incorrect times:")
    print()
    
    fixes_applied = 0
    
    for game in games_to_fix:
        game_id, away, home, old_date, week, year = game
        
        # Parse the old datetime
        old_dt = datetime.fromisoformat(old_date)
        
        # Calculate the corrected time (add 4 hours: 13:00 UTC -> 17:00 UTC)
        new_dt = old_dt + timedelta(hours=4)
        new_date = new_dt.strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"Game {game_id}: {away} @ {home}")
        print(f"  OLD: {old_date} (13:00 UTC = 09:00 AM AST)")
        print(f"  NEW: {new_date} (17:00 UTC = 01:00 PM AST)")
        
        # Update the database
        cursor.execute('''
            UPDATE nfl_games 
            SET game_date = ? 
            WHERE id = ?
        ''', (new_date, game_id))
        
        fixes_applied += 1
        print(f"  ✅ Updated")
        print()
    
    # Also check for other Sunday times that might need adjustment
    print("📋 Checking other Sunday game times...")
    
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, strftime('%H:%M', game_date) as time_utc
        FROM nfl_games 
        WHERE week = 3 AND year = 2025 
        AND strftime('%w', game_date) = '0'  -- Sunday
        AND strftime('%H:%M', game_date) != '17:00'  -- Not already at 5 PM UTC
        ORDER BY game_date
    ''')
    
    other_games = cursor.fetchall()
    for game in other_games:
        game_id, away, home, game_date, time_utc = game
        
        # Convert time to AST for display
        dt = datetime.fromisoformat(game_date)
        ast_hour = (dt.hour - 4) % 24
        ast_time = f"{ast_hour:02d}:{dt.minute:02d}"
        ast_12h = datetime(2000, 1, 1, ast_hour, dt.minute).strftime('%I:%M %p')
        
        print(f"Game {game_id}: {away} @ {home}")
        print(f"  Time: {game_date} ({time_utc} UTC = {ast_12h} AST)")
        
        # These might be correct (late afternoon games, etc.)
        if time_utc in ['16:05', '16:25', '20:20']:
            print(f"  ✅ This time looks correct for late games")
        print()
    
    # Commit changes
    if fixes_applied > 0:
        conn.commit()
        print(f"✅ Applied {fixes_applied} time corrections to the database")
        
        # Verify the fixes
        print("\\n🔍 VERIFICATION - Updated game times:")
        cursor.execute('''
            SELECT id, away_team, home_team, game_date
            FROM nfl_games 
            WHERE week = 3 AND year = 2025 
            AND strftime('%w', game_date) = '0'  -- Sunday
            AND strftime('%H:%M', game_date) = '17:00'  -- Now 5 PM UTC
            ORDER BY game_date
        ''')
        
        fixed_games = cursor.fetchall()
        for game in fixed_games:
            game_id, away, home, game_date = game
            print(f"  ✅ Game {game_id}: {away} @ {home} - {game_date} (17:00 UTC = 01:00 PM AST)")
    else:
        print("ℹ️  No games needed time correction")
    
    conn.close()
    
    print("\\n🎉 Game time fix completed!")
    print("📱 Sunday early games should now display as '01:00 PM AST' instead of '09:00 AM AST'")

if __name__ == '__main__':
    fix_game_times()
