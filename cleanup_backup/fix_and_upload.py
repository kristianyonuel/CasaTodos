#!/usr/bin/env python3
"""
Simple database sync to server
"""

import sqlite3

def add_current_week_setting():
    """Add current_week setting to league_settings"""
    
    print("🔧 ADDING CURRENT_WEEK SETTING")
    print("=" * 40)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check if current_week exists
    cursor.execute("SELECT * FROM league_settings WHERE setting_name = 'current_week'")
    existing = cursor.fetchone()
    
    if existing:
        print(f"✅ current_week already exists: {existing[3]}")
        # Update to week 9
        cursor.execute("UPDATE league_settings SET setting_value = '9' WHERE setting_name = 'current_week'")
        print("✅ Updated current_week to 9")
    else:
        print("➕ Adding current_week setting...")
        cursor.execute("""
            INSERT INTO league_settings 
            (category, setting_name, setting_value, setting_type, display_name, description, is_public, is_editable, sort_order)
            VALUES ('general', 'current_week', '9', 'integer', 'Current Week', 'Current NFL week being displayed', 1, 1, 5)
        """)
        print("✅ Added current_week = 9")
    
    conn.commit()
    conn.close()
    
    print("\n📤 UPLOAD COMMANDS:")
    print("Copy and paste these commands:")
    print()
    print("# Upload database")
    print("scp nfl_fantasy.db casa@20.157.116.145:/home/casa/CasaTodos/nfl_fantasy.db.new")
    print()
    print("# Replace and restart")
    print('ssh casa@20.157.116.145 "cd /home/casa/CasaTodos && cp nfl_fantasy.db nfl_fantasy.db.backup_$(date +%s) && mv nfl_fantasy.db.new nfl_fantasy.db && sudo systemctl restart lacasadetodos.service"')
    print()
    print("🎯 After running these commands, your leaderboard should show:")
    print("   1. JEAN - 9/14 correct")
    print("   2. KRISTIAN, MIKITIN, ROBERT, SHORTY, VIZCA - 8/14 correct")
    print("   And so on...")

if __name__ == "__main__":
    add_current_week_setting()