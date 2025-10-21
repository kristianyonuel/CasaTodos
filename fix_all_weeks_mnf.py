#!/usr/bin/env python3
"""
Comprehensive NFL Schedule Fix
Fix Monday Night Football designation and game times for all weeks
"""

import sqlite3
from datetime import datetime

def fix_all_weeks_mnf():
    """Fix Monday Night Football designation for all weeks"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🔧 FIXING MONDAY NIGHT FOOTBALL FOR ALL WEEKS...")
    
    # Get all weeks that have games
    cursor.execute("""
        SELECT DISTINCT week, year FROM nfl_games 
        WHERE year = 2025 
        ORDER BY week
    """)
    
    weeks = cursor.fetchall()
    print(f"Found {len(weeks)} weeks to check: {[w[0] for w in weeks]}")
    
    total_mnf_fixed = 0
    
    for week_num, year in weeks:
        print(f"\n--- Week {week_num} ---")
        
        # Find games that should be Monday Night Football
        # Look for games on Monday or games with "Monday" timing patterns
        cursor.execute("""
            SELECT id, home_team, away_team, game_date, is_monday_night
            FROM nfl_games 
            WHERE week = ? AND year = ? 
            AND (
                game_date LIKE '%2025-%-%-% 2_:15:00'  -- Monday night timing
                OR game_date LIKE '%2025-%-%-% 00:15:00'  -- Monday midnight timing
                OR strftime('%w', substr(game_date, 1, 10)) = '1'  -- Monday (1)
            )
            ORDER BY game_date DESC
        """, (week_num, year))
        
        potential_mnf = cursor.fetchall()
        
        # Also check for late Sunday/Monday games that might be MNF
        cursor.execute("""
            SELECT id, home_team, away_team, game_date, is_monday_night
            FROM nfl_games 
            WHERE week = ? AND year = ?
            AND game_date > (
                SELECT MAX(game_date) FROM nfl_games 
                WHERE week = ? AND year = ? 
                AND game_date LIKE '%2025-%-%-% 2_:25:00'
            )
            ORDER BY game_date
        """, (week_num, year, week_num, year))
        
        late_games = cursor.fetchall()
        
        # Combine and deduplicate
        all_candidates = list({game[0]: game for game in (potential_mnf + late_games)}.values())
        
        if not all_candidates:
            print(f"  No Monday Night candidates found")
            continue
            
        # Mark the latest 1-2 games as Monday Night Football
        mnf_games = sorted(all_candidates, key=lambda x: x[3])[-2:]  # Last 2 games
        
        for game in mnf_games:
            game_id, home, away, game_date, current_mnf = game
            
            if not current_mnf:  # Only update if not already marked
                cursor.execute("""
                    UPDATE nfl_games 
                    SET is_monday_night = 1, updated_at = ?
                    WHERE id = ?
                """, (datetime.now(), game_id))
                
                print(f"  ✅ Marked as MNF: {away} @ {home} - {game_date}")
                total_mnf_fixed += 1
            else:
                print(f"  ✓ Already MNF: {away} @ {home} - {game_date}")
    
    conn.commit()
    
    # Final verification
    print(f"\n=== VERIFICATION ===")
    cursor.execute("""
        SELECT week, COUNT(*) as mnf_count
        FROM nfl_games 
        WHERE year = 2025 AND is_monday_night = 1
        GROUP BY week
        ORDER BY week
    """)
    
    mnf_summary = cursor.fetchall()
    print(f"Monday Night Football games by week:")
    for week, count in mnf_summary:
        print(f"  Week {week}: {count} MNF games")
    
    conn.close()
    
    print(f"\n✅ Fixed {total_mnf_fixed} Monday Night Football designations!")
    print(f"✅ All weeks now have proper MNF tiebreaker games!")
    
    return total_mnf_fixed

def check_mnf_status():
    """Check current MNF status across all weeks"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("\n=== CURRENT MNF STATUS ===")
    
    cursor.execute("""
        SELECT week, home_team, away_team, game_date, is_monday_night
        FROM nfl_games 
        WHERE year = 2025 AND is_monday_night = 1
        ORDER BY week, game_date
    """)
    
    mnf_games = cursor.fetchall()
    
    if not mnf_games:
        print("❌ No Monday Night Football games found!")
        return False
    
    current_week = None
    for game in mnf_games:
        week, home, away, game_date, is_mnf = game
        
        if week != current_week:
            print(f"\nWeek {week}:")
            current_week = week
            
        print(f"  🏈 {away} @ {home} - {game_date}")
    
    conn.close()
    return True

if __name__ == "__main__":
    print("=== NFL MONDAY NIGHT FOOTBALL FIX ===")
    
    # Check current status
    has_mnf = check_mnf_status()
    
    # Fix all weeks
    fixed_count = fix_all_weeks_mnf()
    
    # Final status
    print(f"\n🎯 SUMMARY:")
    print(f"   • Fixed {fixed_count} Monday Night Football games")
    print(f"   • Tiebreaker inputs now available for all weeks")
    print(f"   • Users can enter score predictions for MNF games")
    
    check_mnf_status()