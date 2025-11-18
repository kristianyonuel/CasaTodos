#!/usr/bin/env python3
"""
Update current week from 10 to 11

Week 10 ended on November 10, 2025 (Monday Night Football)
Today is November 14, 2025 - Week 11 should be active
"""

import sqlite3
from datetime import datetime

def update_current_week_to_11():
    """Update the current_week setting from 10 to 11"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🗓️  UPDATING CURRENT WEEK TO 11")
    print("=" * 50)
    print(f"Today: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("Week 10 ended: November 10, 2025 (Monday Night)")
    print("Week 11 started: November 14, 2025 (Thursday)")
    
    # Check current setting
    cursor.execute("SELECT setting_name, setting_value FROM league_settings WHERE setting_name = 'current_week'")
    current_setting = cursor.fetchone()
    
    if current_setting:
        current_week = current_setting[1]
        print(f"\nCurrent setting: {current_week}")
        
        if current_week == '11':
            print("✅ Already set to Week 11")
        else:
            print(f"🔄 Updating from Week {current_week} to Week 11...")
            cursor.execute("UPDATE league_settings SET setting_value = '11' WHERE setting_name = 'current_week'")
            conn.commit()
            
            # Verify
            if cursor.rowcount > 0:
                print("✅ Updated current_week from {current_week} to 11")
            else:
                print("❌ Failed to update current_week")
    else:
        print("❌ current_week setting not found")
        print("➕ Adding current_week = 11 setting...")
        
        cursor.execute("""
            INSERT INTO league_settings (category, setting_name, setting_value, setting_type, display_name, description, is_active, is_editable, sort_order) 
            VALUES ('general', 'current_week', '11', 'integer', 'Current Week', 'Current NFL week being displayed', 1, 1, 5)
        """)
        conn.commit()
        print("✅ Added current_week = 11")
    
    # Verify the final setting
    cursor.execute("SELECT setting_value FROM league_settings WHERE setting_name = 'current_week'")
    new_value = cursor.fetchone()
    
    if new_value:
        print(f"\n✅ Verified: current_week = {new_value[0]}")
        
        # Check Week 11 games
        cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 11 AND year = 2025")
        week11_games = cursor.fetchone()[0]
        print(f"📊 Week 11 games in database: {week11_games}")
        
        if week11_games > 0:
            print("✅ Week 11 games are ready")
        else:
            print("⚠️  No Week 11 games found - may need to create them")
    
    conn.close()

if __name__ == "__main__":
    update_current_week_to_11()