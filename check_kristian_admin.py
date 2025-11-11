#!/usr/bin/env python3
"""
Check exactly what KRISTIAN's picks look like in the database
and what the admin interface should be showing
"""

import sqlite3

def check_kristian_picks_detailed():
    """Check KRISTIAN's specific picks for admin interface"""
    
    print("🔍 CHECKING KRISTIAN'S PICKS FOR ADMIN INTERFACE")
    print("=" * 50)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get KRISTIAN's user ID
    cursor.execute("SELECT id FROM users WHERE username = 'kristian'")
    kristian_id = cursor.fetchone()
    if not kristian_id:
        print("❌ KRISTIAN not found!")
        return
    
    kristian_id = kristian_id[0]
    print(f"KRISTIAN's user ID: {kristian_id}")
    
    # Get all Week 9 games in order
    cursor.execute("""
        SELECT game_id, away_team, home_team, game_date
        FROM nfl_games 
        WHERE week = 9 AND year = 2025
        ORDER BY game_id
    """)
    
    games = cursor.fetchall()
    print(f"\nFound {len(games)} Week 9 games")
    
    # Check KRISTIAN's picks for each game
    print(f"\nKRISTIAN's picks by game:")
    print("Game | Matchup | KRISTIAN's Pick | In Database?")
    print("-" * 60)
    
    picks_found = 0
    for game_id, away, home, date in games:
        cursor.execute("""
            SELECT selected_team, is_correct 
            FROM user_picks 
            WHERE user_id = ? AND game_id = ?
        """, (kristian_id, game_id))
        
        pick = cursor.fetchone()
        if pick:
            selected_team, is_correct = pick
            status = "✅ CORRECT" if is_correct else "❌ WRONG"
            print(f"{game_id} | {away} @ {home} | {selected_team} | {status}")
            picks_found += 1
        else:
            print(f"{game_id} | {away} @ {home} | NO PICK | ❌ MISSING")
    
    print(f"\nSUMMARY: KRISTIAN has {picks_found}/{len(games)} picks in database")
    
    # Check if there's a different way the admin interface queries
    print(f"\nADMIN INTERFACE QUERY TEST:")
    cursor.execute("""
        SELECT g.game_id, g.away_team, g.home_team, up.selected_team
        FROM nfl_games g
        LEFT JOIN user_picks up ON g.game_id = up.game_id AND up.user_id = ?
        WHERE g.week = 9 AND g.year = 2025
        ORDER BY g.game_id
    """, (kristian_id,))
    
    admin_results = cursor.fetchall()
    print("What admin interface should see:")
    for game_id, away, home, selected in admin_results:
        pick_display = selected if selected else "EMPTY"
        print(f"  {game_id}: {away} @ {home} → {pick_display}")
    
    # Check for any caching or session issues
    print(f"\nDATABASE INTEGRITY CHECK:")
    cursor.execute("SELECT COUNT(*) FROM user_picks WHERE user_id = ?", (kristian_id,))
    total_picks = cursor.fetchone()[0]
    print(f"KRISTIAN's total picks in database: {total_picks}")
    
    # Check if picks are in a different table or format
    cursor.execute("PRAGMA table_info(user_picks)")
    columns = cursor.fetchall()
    print(f"user_picks table has {len(columns)} columns")
    
    conn.close()

if __name__ == "__main__":
    check_kristian_picks_detailed()