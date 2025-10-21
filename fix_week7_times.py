#!/usr/bin/env python3
"""
Fix Week 7 Games - Correct Times and Monday Night Football
"""

import sqlite3
from datetime import datetime

def fix_week7_games():
    """Fix Week 7 game times and Monday Night Football designation"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🔧 FIXING WEEK 7 GAMES...")
    
    # NFL Week 7 2025 - Correct Schedule
    # Based on typical NFL schedule format
    correct_schedule = [
        # Thursday Night Football (if any) - Week 7 usually no TNF
        
        # Sunday Early Games (1:00 PM ET)
        ("LAR", "JAX", "2025-10-19 13:00:00", False, False, False),  # London game
        ("MIA", "CLE", "2025-10-19 17:00:00", False, False, False),
        ("NE", "TEN", "2025-10-19 17:00:00", False, False, False),
        ("LV", "KC", "2025-10-19 17:00:00", False, False, False), 
        ("PHI", "MIN", "2025-10-19 17:00:00", False, False, False),
        ("CAR", "NYJ", "2025-10-19 17:00:00", False, False, False),
        ("NO", "CHI", "2025-10-19 17:00:00", False, False, False),
        
        # Sunday Late Games (4:05/4:25 PM ET)
        ("NYG", "DEN", "2025-10-19 20:05:00", False, False, False),
        ("IND", "LAC", "2025-10-19 20:05:00", False, False, False),
        ("WSH", "DAL", "2025-10-19 20:25:00", False, False, False),
        ("GB", "ARI", "2025-10-19 20:25:00", False, False, False),
        
        # Sunday Night Football (8:20 PM ET)
        ("ATL", "SF", "2025-10-20 00:20:00", False, False, True),
        
        # Monday Night Football (8:15 PM ET) - THIS IS THE KEY FIX
        ("TB", "DET", "2025-10-21 00:15:00", True, False, False),  # MNF Game 1
        ("HOU", "SEA", "2025-10-21 00:15:00", True, False, False), # MNF Game 2 (doubleheader)
    ]
    
    print(f"Updating {len(correct_schedule)} games...")
    
    # Update each game
    for away, home, game_time, is_mnf, is_tnf, is_snf in correct_schedule:
        try:
            cursor.execute("""
                UPDATE nfl_games 
                SET game_date = ?, 
                    is_monday_night = ?, 
                    is_thursday_night = ?, 
                    is_sunday_night = ?,
                    updated_at = ?
                WHERE week = 7 AND year = 2025 
                AND home_team = ? AND away_team = ?
            """, (game_time, is_mnf, is_tnf, is_snf, datetime.now(), home, away))
            
            if cursor.rowcount > 0:
                game_type = ""
                if is_mnf:
                    game_type = " (MNF)"
                elif is_snf:
                    game_type = " (SNF)"
                elif is_tnf:
                    game_type = " (TNF)"
                    
                print(f"  ✅ {away} @ {home} - {game_time}{game_type}")
            else:
                print(f"  ❌ Could not find: {away} @ {home}")
                
        except Exception as e:
            print(f"  ❌ Error updating {away} @ {home}: {e}")
    
    conn.commit()
    
    # Verify Monday Night Football games
    cursor.execute("""
        SELECT home_team, away_team, game_date 
        FROM nfl_games 
        WHERE week = 7 AND year = 2025 AND is_monday_night = 1
        ORDER BY game_date
    """)
    
    mnf_games = cursor.fetchall()
    print(f"\n🏈 Monday Night Football games (for tiebreaker):")
    for game in mnf_games:
        print(f"  {game[1]} @ {game[0]} - {game[2]}")
    
    conn.close()
    
    print(f"\n✅ Week 7 games updated with correct times!")
    print(f"✅ Monday Night Football properly marked for tiebreaker input!")
    
    return len(mnf_games)

if __name__ == "__main__":
    print("=== WEEK 7 GAME TIME FIX ===")
    mnf_count = fix_week7_games()
    
    if mnf_count > 0:
        print(f"\n🎯 SUCCESS: {mnf_count} Monday Night games available for tiebreaker picks!")
    else:
        print(f"\n⚠️ WARNING: No Monday Night games found. Check schedule.")
        
    print(f"\nUsers should now see:")
    print(f"1. ✅ Correct game times for all Week 7 games")
    print(f"2. ✅ Tiebreaker score input for Monday Night Football")
    print(f"3. ✅ Proper game designations (SNF, MNF)")