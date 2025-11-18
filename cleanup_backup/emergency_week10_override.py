#!/usr/bin/env python3
"""
Emergency Week 10 override - forces every possible week setting to 10
"""

import sqlite3

def emergency_week10_override():
    """Force everything to Week 10"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🚨 EMERGENCY WEEK 10 OVERRIDE ACTIVATED")
    print("=" * 50)
    
    # Add every possible setting that might control week display
    override_settings = [
        ('current_week', '10'),
        ('display_week', '10'), 
        ('picks_week', '10'),
        ('leaderboard_week', '10'),
        ('week_override', '10'),
        ('active_week', '10'),
        ('nfl_week', '10'),
        ('game_week', '10'),
        ('score_week', '10'),
        ('espn_week', '10'),
        ('update_week', '10'),
        ('background_week', '10'),
        ('api_week', '10'),
        ('fetch_week', '10'),
        ('live_week', '10')
    ]
    
    for setting_name, value in override_settings:
        cursor.execute("""
            INSERT OR REPLACE INTO league_settings 
            (category, setting_name, setting_value, setting_type, display_name, description, is_public, is_editable, sort_order)
            VALUES ('system', ?, ?, 'integer', ?, 'EMERGENCY WEEK 10 OVERRIDE', 0, 1, 99)
        """, (setting_name, value, setting_name.replace('_', ' ').title()))
        print(f"   ✅ {setting_name} = {value}")
    
    conn.commit()
    conn.close()
    
    print("\n🎯 ALL WEEK SETTINGS FORCED TO 10")
    print("   Flask app should now show Week 10!")
    
if __name__ == "__main__":
    emergency_week10_override()