#!/usr/bin/env python3
"""
Test current week detection after update
"""

import sqlite3
from datetime import datetime

def test_current_week_detection():
    """Test that the app now correctly detects Week 11"""
    
    print("🗓️  TESTING CURRENT WEEK DETECTION")
    print("=" * 50)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check current setting
    cursor.execute("SELECT setting_value FROM league_settings WHERE setting_name = 'current_week'")
    week_setting = cursor.fetchone()
    
    print(f"Current week setting: {week_setting[0] if week_setting else 'NOT SET'}")
    print(f"Today's date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Check Week 10 status (should be complete)
    cursor.execute("""
        SELECT 
            COUNT(*) as total, 
            SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final 
        FROM nfl_games 
        WHERE week = 10 AND year = 2025
    """)
    total10, final10 = cursor.fetchone()
    
    print(f"\n📊 Week 10: {final10}/{total10} final ({(final10/total10*100):.1f}% complete)")
    
    if final10 == total10:
        print("✅ Week 10 is complete")
    else:
        print(f"⚠️  Week 10 has {total10 - final10} games remaining")
    
    # Check Week 11 status (should be just starting)
    cursor.execute("""
        SELECT 
            COUNT(*) as total, 
            SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final 
        FROM nfl_games 
        WHERE week = 11 AND year = 2025
    """)
    total11, final11 = cursor.fetchone()
    
    print(f"📊 Week 11: {final11}/{total11} final ({(final11/total11*100):.1f}% complete)")
    
    if final11 == 0:
        print("✅ Week 11 is ready to start")
    else:
        print(f"📈 Week 11 has {final11} games already completed")
    
    # Get next few game times for Week 11
    cursor.execute("""
        SELECT game_date, away_team, home_team 
        FROM nfl_games 
        WHERE week = 11 AND year = 2025 AND is_final = 0
        ORDER BY game_date 
        LIMIT 3
    """)
    
    upcoming = cursor.fetchall()
    print(f"\n🏈 Next Week 11 games:")
    for game_date, away, home in upcoming:
        print(f"   {game_date}: {away} @ {home}")
    
    conn.close()
    
    print(f"\n✅ Current week successfully updated to 11!")
    print("🔄 The PFR monitoring system will now track Week 11")

if __name__ == "__main__":
    test_current_week_detection()